"""
Quarter-over-Quarter Tone Change Analysis with LLM Enhancement
"""
import logging
import os
import json
from typing import List, Dict

try:
    import requests
except ImportError:
    requests = None

logging.basicConfig(level=logging.INFO)


class ToneAnalyzer:
    """Analyze tone changes across quarters using both quantitative and LLM-based approaches"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.use_llm = (self.openai_api_key and 
                       self.openai_api_key != 'your_api_key_here' and 
                       requests is not None)
        
        if self.use_llm:
            self.logger.info("ToneAnalyzer initialized with LLM capabilities")
        else:
            self.logger.info("ToneAnalyzer initialized with basic analysis only")
    
    def analyze_tone_changes(self, quarterly_results: List[Dict]) -> Dict:
        """Analyze tone changes across quarters using enhanced LLM approach"""
        if len(quarterly_results) < 2:
            return {
                'overall_trend': 'insufficient_data',
                'changes': [],
                'summary': 'Need at least 2 quarters for tone change analysis.'
            }
        
        # Sort by year and quarter
        sorted_results = sorted(quarterly_results, 
                              key=lambda x: (x['year'], x['quarter']))
        
        changes = []
        
        for i in range(1, len(sorted_results)):
            prev = sorted_results[i-1]
            curr = sorted_results[i]
            
            # Basic quantitative analysis
            basic_change = self._analyze_basic_change(prev, curr)
            
            # Enhanced LLM analysis if available
            if self.use_llm:
                llm_analysis = self._analyze_with_llm(prev, curr)
                # Merge LLM insights with basic analysis
                change_data = {**basic_change, **llm_analysis}
            else:
                change_data = basic_change
            
            changes.append(change_data)
        
        # Determine overall trend with LLM enhancement
        if self.use_llm and len(changes) > 0:
            overall_analysis = self._analyze_overall_trend_llm(changes, sorted_results)
            overall_trend = overall_analysis.get('trend', self._determine_overall_trend(changes))
            summary = overall_analysis.get('summary', self._generate_summary(overall_trend, changes))
        else:
            overall_trend = self._determine_overall_trend(changes)
            summary = self._generate_summary(overall_trend, changes)
        
        return {
            'overall_trend': overall_trend,
            'changes': changes,
            'summary': summary,
            'analysis_method': 'llm_enhanced' if self.use_llm else 'basic'
        }
    
    def _analyze_basic_change(self, prev: Dict, curr: Dict) -> Dict:
        """Basic quantitative tone change analysis"""
        # Calculate sentiment changes
        prev_mgmt_sentiment = prev['management_sentiment']['sentiment']
        curr_mgmt_sentiment = curr['management_sentiment']['sentiment']
        
        prev_qa_sentiment = prev['qa_sentiment']['sentiment']
        curr_qa_sentiment = curr['qa_sentiment']['sentiment']
        
        # Determine change direction
        mgmt_change = self._calculate_change(prev_mgmt_sentiment, curr_mgmt_sentiment)
        qa_change = self._calculate_change(prev_qa_sentiment, curr_qa_sentiment)
        
        # Calculate confidence-weighted scores
        prev_score = self._calculate_weighted_score(prev)
        curr_score = self._calculate_weighted_score(curr)
        score_change = curr_score - prev_score
        
        return {
            'from_quarter': f"Q{prev['quarter']} {prev['year']}",
            'to_quarter': f"Q{curr['quarter']} {curr['year']}",
            'management_tone_change': mgmt_change,
            'qa_tone_change': qa_change,
            'overall_change': 'improving' if score_change > 0.1 else 
                            'deteriorating' if score_change < -0.1 else 'stable',
            'score_change': round(score_change, 3)
        }
    
    def _analyze_with_llm(self, prev: Dict, curr: Dict) -> Dict:
        """Enhanced LLM-based tone analysis comparing two quarters"""
        try:
            # Extract key excerpts for comparison
            prev_excerpts = self._extract_key_excerpts(prev)
            curr_excerpts = self._extract_key_excerpts(curr)
            
            # Build comparison prompt
            prompt = self._build_tone_comparison_prompt(prev, curr, prev_excerpts, curr_excerpts)
            
            # Call OpenAI API
            response = self._call_openai_api(prompt)
            
            if response:
                self.logger.info(f"Raw OpenAI response: {response[:500]}...")  # Log first 500 chars
                
                # Clean the response - remove markdown code blocks if present
                cleaned_response = response.strip()
                if cleaned_response.startswith('```json'):
                    cleaned_response = cleaned_response[7:]  # Remove ```json
                if cleaned_response.startswith('```'):
                    cleaned_response = cleaned_response[3:]  # Remove ```
                if cleaned_response.endswith('```'):
                    cleaned_response = cleaned_response[:-3]  # Remove trailing ```
                cleaned_response = cleaned_response.strip()
                
                analysis = json.loads(cleaned_response)
                return {
                    'tone_shift_description': analysis.get('tone_shift', 'No significant change detected'),
                    'confidence_changes': analysis.get('confidence_changes', 'Unable to assess'),
                    'key_topics_evolved': analysis.get('key_topics', []),
                    'strategic_messaging_shift': analysis.get('strategic_shift', 'No notable shift'),
                    'language_style_changes': analysis.get('language_changes', 'Similar style maintained'),
                    'forward_looking_tone': analysis.get('forward_tone', 'Consistent outlook'),
                    'llm_confidence': analysis.get('analysis_confidence', 'medium')
                }
            else:
                return {'llm_analysis': 'LLM analysis failed - using basic analysis only'}
                
        except Exception as e:
            self.logger.error(f"LLM tone analysis failed: {e}")
            return {'llm_analysis': f'LLM analysis error: {str(e)}'}
    
    def _extract_key_excerpts(self, quarter_data: Dict) -> Dict:
        """Extract key text excerpts for LLM analysis"""
        # Get first few sentences from management remarks and Q&A
        mgmt_text = ""
        qa_text = ""
        
        self.logger.info(f"Extracting excerpts for Q{quarter_data['quarter']} {quarter_data['year']}")
        self.logger.info(f"Available keys in quarter_data: {list(quarter_data.keys())}")
        
        # Extract from transcript if available
        if 'transcript_data' in quarter_data:
            transcript = quarter_data['transcript_data']
            self.logger.info(f"Found transcript_data with keys: {list(transcript.keys())}")
            
            if 'prepared_remarks' in transcript:
                mgmt_segments = transcript['prepared_remarks'][:3]  # First 3 segments
                mgmt_text = " ".join([seg.get('content', '') for seg in mgmt_segments])[:1000]
                self.logger.info(f"Extracted management text length: {len(mgmt_text)}")
            
            if 'qa_session' in transcript:
                qa_segments = transcript['qa_session'][:5]  # First 5 Q&A exchanges
                qa_text = " ".join([seg.get('content', '') for seg in qa_segments])[:1000]
                self.logger.info(f"Extracted QA text length: {len(qa_text)}")
        else:
            self.logger.warning("No transcript_data found in quarter_data")
        
        return {
            'management_excerpt': mgmt_text,
            'qa_excerpt': qa_text,
            'quarter': f"Q{quarter_data['quarter']} {quarter_data['year']}"
        }
    
    def _build_tone_comparison_prompt(self, prev: Dict, curr: Dict, prev_excerpts: Dict, curr_excerpts: Dict) -> str:
        """Build detailed prompt for LLM tone comparison"""
        return f"""
You are an expert financial analyst specializing in earnings call tone analysis. Compare the tone, confidence, and messaging between these two NVIDIA earnings quarters:

**PREVIOUS QUARTER ({prev_excerpts['quarter']}):**
Management Tone: {prev['management_sentiment']['sentiment']} (confidence: {prev['management_sentiment']['confidence']:.2f})
Q&A Tone: {prev['qa_sentiment']['sentiment']} (confidence: {prev['qa_sentiment']['confidence']:.2f})

Management Excerpt: "{prev_excerpts['management_excerpt'][:500]}..."
Q&A Excerpt: "{prev_excerpts['qa_excerpt'][:500]}..."

**CURRENT QUARTER ({curr_excerpts['quarter']}):**
Management Tone: {curr['management_sentiment']['sentiment']} (confidence: {curr['management_sentiment']['confidence']:.2f})
Q&A Tone: {curr['qa_sentiment']['sentiment']} (confidence: {curr['qa_sentiment']['confidence']:.2f})

Management Excerpt: "{curr_excerpts['management_excerpt'][:500]}..."
Q&A Excerpt: "{curr_excerpts['qa_excerpt'][:500]}..."

Analyze the tone evolution between these quarters and provide insights in JSON format:
{{
    "tone_shift": "Detailed description of how the overall tone changed",
    "confidence_changes": "How confidence levels evolved (more assertive, cautious, etc.)",
    "key_topics": ["List", "of", "topics", "that", "show", "notable", "tone", "shifts"],
    "strategic_shift": "Changes in strategic messaging or priorities",
    "language_changes": "Evolution in language style (more technical, accessible, aggressive, etc.)",
    "forward_tone": "Changes in forward-looking statements and guidance tone",
    "analysis_confidence": "high|medium|low - your confidence in this analysis"
}}

Focus on nuanced changes in:
1. Executive confidence and certainty
2. Defensive vs. offensive positioning
3. Technical depth and specificity
4. Cautionary language vs. bold statements
5. Market outlook and competitive positioning
"""
    
    def _analyze_overall_trend_llm(self, changes: List[Dict], all_quarters: List[Dict]) -> Dict:
        """Use LLM to analyze overall trend across all quarters"""
        try:
            # Build comprehensive trend analysis prompt
            prompt = self._build_trend_analysis_prompt(changes, all_quarters)
            
            response = self._call_openai_api(prompt)
            
            if response:
                # Clean the response - remove markdown code blocks if present
                cleaned_response = response.strip()
                if cleaned_response.startswith('```json'):
                    cleaned_response = cleaned_response[7:]  # Remove ```json
                if cleaned_response.startswith('```'):
                    cleaned_response = cleaned_response[3:]  # Remove ```
                if cleaned_response.endswith('```'):
                    cleaned_response = cleaned_response[:-3]  # Remove trailing ```
                cleaned_response = cleaned_response.strip()
                
                return json.loads(cleaned_response)
            else:
                return {}
                
        except Exception as e:
            self.logger.error(f"LLM trend analysis failed: {e}")
            return {}
    
    def _build_trend_analysis_prompt(self, changes: List[Dict], all_quarters: List[Dict]) -> str:
        """Build prompt for overall trend analysis"""
        quarters_summary = []
        for q in all_quarters:
            quarters_summary.append(
                f"Q{q['quarter']} {q['year']}: Management {q['management_sentiment']['sentiment']} "
                f"({q['management_sentiment']['confidence']:.2f}), "
                f"Q&A {q['qa_sentiment']['sentiment']} ({q['qa_sentiment']['confidence']:.2f})"
            )
        
        changes_summary = []
        for change in changes:
            changes_summary.append(
                f"{change['from_quarter']} → {change['to_quarter']}: "
                f"Mgmt {change['management_tone_change']}, Q&A {change['qa_tone_change']}, "
                f"Score Δ {change['score_change']}"
            )
        
        return f"""
You are analyzing NVIDIA's earnings call tone evolution across multiple quarters. 

**QUARTERLY PROGRESSION:**
{chr(10).join(quarters_summary)}

**QUARTER-TO-QUARTER CHANGES:**
{chr(10).join(changes_summary)}

Provide a comprehensive trend analysis in JSON format:
{{
    "trend": "consistently_improving|consistently_deteriorating|generally_improving|generally_deteriorating|mixed|volatile",
    "summary": "Detailed 2-3 sentence narrative explaining the overall tone evolution and what it suggests about NVIDIA's business trajectory",
    "key_patterns": ["Notable", "patterns", "in", "tone", "evolution"],
    "business_implications": "What these tone changes suggest about NVIDIA's market position and confidence",
    "confidence_in_analysis": "high|medium|low"
}}

Consider:
1. Consistency vs. volatility in tone
2. Management vs. Q&A alignment or divergence
3. Confidence trends over time
4. Strategic messaging evolution
5. Market cycle indicators in tone
"""
    
    def _call_openai_api(self, prompt: str) -> str:
        """Call OpenAI API for analysis"""
        if requests is None:
            self.logger.error("requests library not available for OpenAI API calls")
            return None
            
        try:
            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-4o-mini',  # More cost-effective option
                'messages': [
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.3,  # Lower temperature for more consistent analysis
                'max_tokens': 1000
            }
            
            self.logger.info(f"Making OpenAI API call with prompt length: {len(prompt)}")
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            self.logger.info(f"OpenAI API response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                self.logger.info(f"OpenAI API response content length: {len(content) if content else 0}")
                return content
            else:
                self.logger.error(f"OpenAI API error: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            self.logger.error(f"OpenAI API call failed: {e}")
            return None
    
    def _calculate_change(self, prev_sentiment: str, curr_sentiment: str) -> str:
        """Calculate sentiment change direction"""
        sentiment_values = {'negative': -1, 'neutral': 0, 'positive': 1}
        
        prev_val = sentiment_values.get(prev_sentiment, 0)
        curr_val = sentiment_values.get(curr_sentiment, 0)
        
        diff = curr_val - prev_val
        
        if diff > 0:
            return 'improving'
        elif diff < 0:
            return 'deteriorating'
        else:
            return 'stable'
        """Calculate sentiment change direction"""
        sentiment_values = {'negative': -1, 'neutral': 0, 'positive': 1}
        
        prev_val = sentiment_values.get(prev_sentiment, 0)
        curr_val = sentiment_values.get(curr_sentiment, 0)
        
        diff = curr_val - prev_val
        
        if diff > 0:
            return 'improving'
        elif diff < 0:
            return 'deteriorating'
        else:
            return 'stable'
    
    def _calculate_weighted_score(self, result: Dict) -> float:
        """Calculate confidence-weighted sentiment score"""
        mgmt_scores = result['management_sentiment']['scores']
        qa_scores = result['qa_sentiment']['scores']
        
        # Weight management remarks slightly higher
        mgmt_weight = 0.6
        qa_weight = 0.4
        
        mgmt_score = (mgmt_scores['positive'] - mgmt_scores['negative'])
        qa_score = (qa_scores['positive'] - qa_scores['negative'])
        
        return (mgmt_score * mgmt_weight) + (qa_score * qa_weight)
    
    def _determine_overall_trend(self, changes: List[Dict]) -> str:
        """Determine the overall trend from changes"""
        if not changes:
            return 'no_data'
        
        # Count improving vs deteriorating
        improving = sum(1 for c in changes if c['overall_change'] == 'improving')
        deteriorating = sum(1 for c in changes if c['overall_change'] == 'deteriorating')
        
        # Check last two quarters for recent trend
        recent_changes = changes[-2:] if len(changes) >= 2 else changes
        recent_positive = all(c['score_change'] > 0 for c in recent_changes)
        recent_negative = all(c['score_change'] < 0 for c in recent_changes)
        
        if recent_positive and improving > deteriorating:
            return 'consistently_improving'
        elif recent_negative and deteriorating > improving:
            return 'consistently_deteriorating'
        elif improving > deteriorating:
            return 'generally_improving'
        elif deteriorating > improving:
            return 'generally_deteriorating'
        else:
            return 'mixed'
    
    def _generate_summary(self, trend: str, changes: List[Dict]) -> str:
        """Generate a human-readable summary"""
        summaries = {
            'consistently_improving': "NVIDIA's tone has been consistently improving across recent quarters, showing growing confidence.",
            'consistently_deteriorating': "NVIDIA's tone has shown consistent deterioration, indicating potential concerns.",
            'generally_improving': "Overall, NVIDIA's tone has been improving, though with some fluctuations.",
            'generally_deteriorating': "NVIDIA's tone has generally deteriorated over the analyzed period.",
            'mixed': "NVIDIA's tone has shown mixed signals with no clear directional trend.",
            'no_data': "Insufficient data to determine tone changes."
        }
        
        return summaries.get(trend, "Unable to determine clear tone trend.")