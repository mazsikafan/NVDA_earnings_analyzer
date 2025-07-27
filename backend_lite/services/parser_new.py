"""
Improved Transcript Parser for segmenting earnings calls
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
    
    def _find_qa_start(self, text: str) -> int:
        """Find the start position of Q&A section"""
        text_lower = text.lower()
        
        for pattern in self.qa_start_patterns:
            match = re.search(pattern, text_lower, re.IGNORECASE)
            if match:
                self.logger.info(f"Found Q&A section with pattern: {pattern}")
                return match.start()
        
        return -1
    
    def _parse_management_segments(self, text: str) -> List[Dict]:
        """Parse management/prepared remarks section"""
        segments = []
        
        # Clean up the text first
        text = self._clean_boilerplate(text)
        
        # Split by speaker patterns
        parts = self.speaker_pattern.split(text)
        
        # Process parts (speaker, content, speaker, content, ...)
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                speaker = parts[i].strip()
                content = parts[i + 1].strip()
                
                # Skip operator and boilerplate speakers
                if self._is_meaningful_speaker(speaker) and self._is_meaningful_content(content):
                    cleaned_content = self._clean_content(content)
                    
                    if cleaned_content and len(cleaned_content.split()) > 30:  # Meaningful length
                        segments.append({
                            'speaker': speaker,
                            'content': cleaned_content,
                            'word_count': len(cleaned_content.split()),
                            'speaker_type': 'executive' if self._is_executive(speaker) else 'other'
                        })
        
        # If no speaker patterns found but we have text, try to extract executive content
        if not segments and text.strip():
            # Look for executive content without clear speaker markers
            executive_content = self._extract_executive_content(text)
            if executive_content:
                segments.append({
                    'speaker': 'Management',
                    'content': executive_content,
                    'word_count': len(executive_content.split()),
                    'speaker_type': 'executive'
                })
        
        self.logger.info(f"Extracted {len(segments)} management segments")
        return segments
    
    def _parse_qa_segments(self, text: str) -> List[Dict]:
        """Parse Q&A section into segments"""
        segments = []
        
        # Clean up the text first
        text = self._clean_boilerplate(text)
        
        # Split by speaker patterns
        parts = self.speaker_pattern.split(text)
        
        # Process parts (speaker, content, speaker, content, ...)
        for i in range(1, len(parts), 2):
            if i + 1 < len(parts):
                speaker = parts[i].strip()
                content = parts[i + 1].strip()
                
                # Skip very short segments and operator instructions
                if self._is_meaningful_content(content):
                    cleaned_content = self._clean_content(content)
                    
                    if cleaned_content and len(cleaned_content.split()) > 15:
                        speaker_type = self._classify_speaker(speaker, content)
                        
                        segments.append({
                            'speaker': speaker,
                            'content': cleaned_content,
                            'word_count': len(cleaned_content.split()),
                            'speaker_type': speaker_type
                        })
        
        self.logger.info(f"Extracted {len(segments)} Q&A segments")
        return segments
    
    def _is_meaningful_speaker(self, speaker: str) -> bool:
        """Check if speaker is meaningful (not operator, etc.)"""
        speaker_lower = speaker.lower()
        
        # Skip operators and boilerplate
        skip_speakers = [
            'operator', 'contents', 'image source', 'prepared remarks',
            'questions and answers', 'call participants'
        ]
        
        return not any(skip in speaker_lower for skip in skip_speakers)
    
    def _is_meaningful_content(self, content: str) -> bool:
        """Check if content is meaningful for analysis"""
        content_lower = content.lower()
        
        # Skip common boilerplate content
        boilerplate_indicators = [
            'good afternoon', 'conference operator', 'welcome everyone',
            'all lines have been placed on mute', 'prevent any background noise',
            'operator instructions', 'please go ahead', 'thank you operator'
        ]
        
        # If content is too short or mostly boilerplate
        if len(content.split()) < 10:
            return False
            
        boilerplate_count = sum(1 for indicator in boilerplate_indicators if indicator in content_lower)
        return boilerplate_count < 2
    
    def _is_executive(self, speaker: str) -> bool:
        """Check if speaker is an executive"""
        speaker_lower = speaker.lower()
        
        executive_indicators = [
            'jensen', 'huang', 'colette', 'kress', 'stewart', 'stecker',
            'chief executive officer', 'chief financial officer', 'president',
            'executive vice president', 'ceo', 'cfo'
        ]
        
        return any(indicator in speaker_lower for indicator in executive_indicators)
    
    def _classify_speaker(self, speaker: str, content: str) -> str:
        """Classify speaker as executive, analyst, or other"""
        speaker_lower = speaker.lower()
        
        # Check if executive
        if self._is_executive(speaker):
            return 'executive'
        
        # Check if analyst
        analyst_indicators = [
            'analyst', 'research', 'capital', 'securities', 'bank', 
            'morgan', 'goldman', 'barclays', 'jpmorgan', 'credit suisse'
        ]
        
        if any(indicator in speaker_lower for indicator in analyst_indicators):
            return 'analyst'
        
        # Heuristic: shorter segments are often questions from analysts
        if len(content.split()) < 50:
            return 'analyst'
        
        return 'executive'  # Default to executive for longer responses
    
    def _extract_executive_content(self, text: str) -> str:
        """Extract executive content when speaker patterns fail"""
        # Look for paragraphs that contain executive language/topics
        paragraphs = text.split('\n\n')
        
        executive_content = []
        for para in paragraphs:
            if len(para.split()) > 30:  # Substantial content
                para_lower = para.lower()
                
                # Look for business/financial language typical of executive remarks
                executive_indicators = [
                    'revenue', 'quarter', 'growth', 'performance', 'results',
                    'business', 'market', 'customers', 'products', 'outlook',
                    'datacenter', 'gaming', 'automotive', 'ai', 'artificial intelligence'
                ]
                
                indicator_count = sum(1 for indicator in executive_indicators if indicator in para_lower)
                
                if indicator_count >= 2:  # At least 2 business terms
                    executive_content.append(para.strip())
        
        return '\n\n'.join(executive_content[:3])  # Return first 3 meaningful paragraphs
    
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
