"""
Transcript Parser for segmenting earnings calls
"""
import re
import logging
from typing import Dict, List, Optional

logging.basicConfig(level=logging.INFO)


class TranscriptParser:
    """Parse transcripts into management remarks and Q&A sections"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Patterns for finding prepared remarks section
        self.prepared_remarks_patterns = [
            r'prepared\s+remarks?:?',
            r'management\s+presentation',
            r'opening\s+remarks?'
        ]
        
        # Common patterns for Q&A section identification
        self.qa_start_patterns = [
            r'question[s]?\s*[&and]*\s*answer[s]?:?',
            r'q\s*&\s*a\s*session',
            r'q\s*and\s*a\s*session',
            r'questions\s*and\s*answers?:?',
            r'analyst\s*questions?',
            r'question[- ]and[- ]answer\s*session'
        ]
        
        # Executive name patterns for NVIDIA
        self.executive_patterns = [
            r'jensen\s+h?[ua]ng',
            r'colette\s+[mk]\.?\s*kress',
            r'stewart\s+stecker',
            r'president\s+and\s+chief\s+executive\s+officer',
            r'chief\s+financial\s+officer',
            r'executive\s+vice\s+president'
        ]
        
        # Speaker patterns - more flexible
        self.speaker_pattern = re.compile(r'^([A-Z][A-Za-z\s\-\.\,]+?)(?:\s*--|\s*:|\s*\|)', re.MULTILINE)
        
    def parse(self, transcript_data: Dict) -> Dict:
        """Parse transcript into structured sections"""
        if not transcript_data:
            return None
            
        full_text = transcript_data.get('full_text', '')
        if not full_text:
            return None
            
        self.logger.info(f"Parsing transcript for Q{transcript_data.get('quarter')} {transcript_data.get('year')}")
        
        # Clean up the text first
        full_text = self._clean_raw_text(full_text)
        
        # Find the prepared remarks section
        prepared_remarks_start = self._find_prepared_remarks_start(full_text)
        qa_start = self._find_qa_start(full_text)
        
        if prepared_remarks_start >= 0 and qa_start > prepared_remarks_start:
            # Extract sections properly
            prepared_remarks_text = full_text[prepared_remarks_start:qa_start].strip()
            qa_text = full_text[qa_start:].strip()
            
            self.logger.info(f"Found prepared remarks section at position {prepared_remarks_start}")
            self.logger.info(f"Found Q&A section at position {qa_start}")
        elif qa_start > 0:
            # If we found Q&A but not prepared remarks, use everything before Q&A
            prepared_remarks_text = full_text[:qa_start].strip()
            qa_text = full_text[qa_start:].strip()
            
            self.logger.info(f"Using text before Q&A as prepared remarks")
        else:
            # Fallback: split by heuristic
            split_pos = int(len(full_text) * 0.6)
            prepared_remarks_text = full_text[:split_pos].strip()
            qa_text = full_text[split_pos:].strip()
            
            self.logger.warning(f"Using heuristic split for sections")
        
        # Parse speakers and segments
        management_remarks = self._parse_management_segments(prepared_remarks_text)
        qa_session = self._parse_qa_segments(qa_text)
        
        return {
            'quarter': transcript_data.get('quarter'),
            'year': transcript_data.get('year'),
            'title': transcript_data.get('title'),
            'url': transcript_data.get('url'),
            'management_remarks': management_remarks,
            'qa_session': qa_session,
            'total_segments': len(management_remarks) + len(qa_session)
        }
        
    def _clean_raw_text(self, text: str) -> str:
        """Clean raw HTML/text before processing"""
        # Remove common HTML artifacts and metadata
        text = re.sub(r'<[^>]+>', '', text)  # Remove HTML tags
        text = re.sub(r'Image\s+source:?[^\n]*', '', text, flags=re.IGNORECASE)
        text = re.sub(r'Advertisement[^\n]*', '', text, flags=re.IGNORECASE)
        
        # Clean up whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)
        text = re.sub(r'^\s+|\s+$', '', text, flags=re.MULTILINE)
        
        return text.strip()
        
    def _find_prepared_remarks_start(self, text: str) -> int:
        """Find the start position of prepared remarks section"""
        text_lower = text.lower()
        
        for pattern in self.prepared_remarks_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                self.logger.info(f"Found prepared remarks section with pattern: {pattern}")
                return match.end()
        
        # If no explicit "Prepared Remarks" found, look for the first executive speaker
        for pattern in self.executive_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                # Find the start of this paragraph/section
                start = text.rfind('\n', 0, match.start())
                self.logger.info(f"Found executive speaker, starting prepared remarks from: {pattern}")
                return max(0, start)
        
        return -1
        # Find Q&A section start
        qa_start_pos = self._find_qa_start(full_text)
        
        if qa_start_pos > 0:
            management_text = full_text[:qa_start_pos].strip()
            qa_text = full_text[qa_start_pos:].strip()
        else:
            # If no clear Q&A section found, use heuristic
            # Assume last 40% is Q&A
            split_pos = int(len(full_text) * 0.6)
            management_text = full_text[:split_pos].strip()
            qa_text = full_text[split_pos:].strip()
        
        # Parse speakers and segments
        management_remarks = self._parse_segments(management_text)
        qa_session = self._parse_segments(qa_text)
        
        # Identify executives vs analysts in Q&A
        qa_session = self._classify_qa_speakers(qa_session)
        
        return {
            'quarter': transcript_data.get('quarter'),
            'year': transcript_data.get('year'),
            'title': transcript_data.get('title'),
            'url': transcript_data.get('url'),
            'management_remarks': management_remarks,
            'qa_session': qa_session,
            'total_segments': len(management_remarks) + len(qa_session)
        }
    
    def _find_qa_start(self, text: str) -> int:
        """Find the start position of Q&A section"""
        text_lower = text.lower()
        
        for pattern in self.qa_start_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                self.logger.info(f"Found Q&A section with pattern: {pattern}")
                return match.start()
        
        return -1
    
    def _parse_segments(self, text: str) -> List[Dict]:
        """Parse text into speaker segments"""
        segments = []
        
        # Clean up common boilerplate patterns first
        text = self._clean_boilerplate(text)
        
        # Split by speaker pattern
        parts = self.speaker_pattern.split(text)
        
        # Process parts (speaker, content, speaker, content, ...)
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                speaker = parts[i].strip()
                content = parts[i + 1].strip()
                
                # Clean and validate content
                content = self._clean_content(content)
                
                if content and len(content) > 50:  # Skip very short segments
                    segments.append({
                        'speaker': speaker,
                        'content': content,
                        'word_count': len(content.split())
                    })
        
        # If no speaker patterns found, treat as single segment but clean it
        if not segments and text.strip():
            cleaned_text = self._clean_content(text.strip())
            if cleaned_text and len(cleaned_text) > 50:
                segments.append({
                    'speaker': 'Unknown',
                    'content': cleaned_text,
                    'word_count': len(cleaned_text.split())
                })
        
        return segments
    
    def _clean_boilerplate(self, text: str) -> str:
        """Remove common boilerplate text that doesn't contain sentiment"""
        # Remove common boilerplate patterns
        boilerplate_patterns = [
            r'The Motley Fool\.\s*',
            r'Nvidia\s*\(\s*NVDA\s*[+-]?\d*\.?\d*%?\s*\)',
            r'Q\d+\s+\d{4}\s+Earnings\s+Call',
            r'[A-Z][a-z]+\s+\d{1,2},\s+\d{4}',
            r'\d{1,2}:\d{2}\s+[ap]\.m\.\s+ET',
            r'Image\s+source[^\n]*',
            r'Call\s+Participants',
            r'Prepared\s+Remarks',
            r'Questions\s+and\s+Answers',
            r'Operator\s*Good\s+afternoon\.[^.]*conference\s+operator[^.]*\.',
        ]
        
        for pattern in boilerplate_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _clean_content(self, content: str) -> str:
        """Clean content of titles, metadata, and formatting issues"""
        # Remove title patterns that often get mixed in
        title_patterns = [
            r'^[A-Z][a-z\s,]+(?:Director|Officer|President|CEO|CFO)[^\n]*\n',
            r'^Thanks?,?\s+[A-Z][a-z]+\.\s*',
            r'^\s*[\w\s]+,\s+[\w\s]+\s*\n',  # Remove title lines
        ]
        
        for pattern in title_patterns:
            content = re.sub(pattern, '', content, flags=re.MULTILINE)
        
        # Clean up excessive whitespace and newlines
        content = re.sub(r'\n\s*\n\s*\n+', '\n\n', content)
        content = re.sub(r'^\s+|\s+$', '', content)
        
        return content
    
    def _classify_qa_speakers(self, qa_segments: List[Dict]) -> List[Dict]:
        """Classify Q&A speakers as executives or analysts"""
        executive_keywords = ['ceo', 'cfo', 'president', 'chief', 'officer', 'jensen', 'huang', 'colette', 'kress']
        analyst_keywords = ['analyst', 'research', 'capital', 'securities', 'bank', 'morgan', 'goldman']
        
        for segment in qa_segments:
            speaker_lower = segment['speaker'].lower()
            
            # Check if executive
            is_executive = any(keyword in speaker_lower for keyword in executive_keywords)
            
            # Check if analyst
            is_analyst = any(keyword in speaker_lower for keyword in analyst_keywords)
            
            # If neither, guess based on position (questions from analysts, answers from executives)
            if not is_executive and not is_analyst:
                # Simple heuristic: shorter segments are often questions
                is_analyst = segment['word_count'] < 100
            
            segment['speaker_type'] = 'analyst' if is_analyst else 'executive'
        
        return qa_segments