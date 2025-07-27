"""
Strategic Focuses Extraction using lightweight approach
"""
import os
import re
import logging
from typing import List, Dict
from collections import Counter
import requests

logging.basicConfig(level=logging.INFO)


class StrategicAnalyzer:
    """Extract strategic focuses from earnings transcripts"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        
        # Key themes to look for in NVIDIA context
        self.nvidia_themes = {
            'ai_datacenter': ['data center', 'datacenter', 'ai infrastructure', 'gpu compute', 'h100', 'h200', 'hopper', 'blackwell'],
            'gaming': ['gaming', 'geforce', 'rtx', 'gamers', 'gaming gpu'],
            'automotive': ['automotive', 'drive', 'self-driving', 'autonomous vehicle'],
            'professional_vis': ['professional visualization', 'quadro', 'workstation', 'content creation'],
            'ai_software': ['cuda', 'ai software', 'nvidia ai', 'inference', 'training', 'llm', 'large language model'],
            'partnerships': ['partnership', 'collaboration', 'customer', 'hyperscaler', 'cloud provider'],
            'supply_chain': ['supply', 'demand', 'capacity', 'manufacturing', 'production'],
            'innovation': ['innovation', 'research', 'development', 'next generation', 'roadmap']
        }
    
    def extract_focuses(self, transcript_data: Dict) -> List[Dict]:
        """Extract strategic focuses from transcript"""
        if not transcript_data:
            return []
        
        full_text = transcript_data.get('full_text', '')
        if not full_text:
            return []
        
        # Try OpenAI API if available
        if self.openai_api_key and self.openai_api_key != 'your_api_key_here':
            return self._extract_with_llm(full_text)
        else:
            # Fallback to keyword-based extraction
            return self._extract_with_keywords(full_text)
    
    def _extract_with_llm(self, text: str) -> List[Dict]:
        """Extract focuses using OpenAI API"""
        try:
            # Truncate text to reduce tokens
            max_chars = 8000
            truncated_text = text[:max_chars] if len(text) > max_chars else text
            
            prompt = f"""Analyze this NVIDIA earnings call transcript and identify 3-5 key strategic focuses or initiatives. 
For each focus, provide:
1. A short title (2-4 words)
2. A brief description (1-2 sentences)
3. The importance level (high/medium)

Focus on major themes like AI growth, data center expansion, new products, partnerships, etc.

Transcript excerpt:
{truncated_text}

Return as a simple list with format:
- Title: Description (Importance)"""

            headers = {
                'Authorization': f'Bearer {self.openai_api_key}',
                'Content-Type': 'application/json'
            }
            
            data = {
                'model': 'gpt-3.5-turbo',
                'messages': [
                    {'role': 'system', 'content': 'You are a financial analyst specializing in tech companies.'},
                    {'role': 'user', 'content': prompt}
                ],
                'max_tokens': 300,
                'temperature': 0.3
            }
            
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                return self._parse_llm_response(content)
            else:
                self.logger.error(f"OpenAI API error: {response.status_code}")
                return self._extract_with_keywords(text)
                
        except Exception as e:
            self.logger.error(f"Error with LLM extraction: {e}")
            return self._extract_with_keywords(text)
    
    def _parse_llm_response(self, response: str) -> List[Dict]:
        """Parse LLM response into structured format"""
        focuses = []
        lines = response.strip().split('\n')
        
        for line in lines:
            if line.strip().startswith('-'):
                # Parse format: - Title: Description (Importance)
                match = re.match(r'-\s*([^:]+):\s*([^(]+)(?:\((\w+)\))?', line)
                if match:
                    title = match.group(1).strip()
                    description = match.group(2).strip()
                    importance = match.group(3).strip().lower() if match.group(3) else 'medium'
                    
                    focuses.append({
                        'title': title,
                        'description': description,
                        'importance': importance if importance in ['high', 'medium', 'low'] else 'medium'
                    })
        
        return focuses[:5]  # Limit to 5 focuses
    
    def _extract_with_keywords(self, text: str) -> List[Dict]:
        """Fallback keyword-based extraction"""
        text_lower = text.lower()
        theme_scores = {}
        
        # Count occurrences of theme keywords
        for theme, keywords in self.nvidia_themes.items():
            score = sum(text_lower.count(keyword.lower()) for keyword in keywords)
            if score > 0:
                theme_scores[theme] = score
        
        # Sort by score and take top themes
        top_themes = sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        
        # Convert to structured format
        focuses = []
        theme_descriptions = {
            'ai_datacenter': ('AI Data Center Growth', 'Expansion of AI infrastructure and data center business'),
            'gaming': ('Gaming Business', 'GeForce RTX and gaming GPU developments'),
            'automotive': ('Automotive AI', 'Self-driving and automotive AI platform progress'),
            'professional_vis': ('Professional Visualization', 'Workstation and content creation solutions'),
            'ai_software': ('AI Software Platform', 'CUDA ecosystem and AI software stack development'),
            'partnerships': ('Strategic Partnerships', 'Key customer and partner collaborations'),
            'supply_chain': ('Supply Chain', 'Manufacturing capacity and supply-demand dynamics'),
            'innovation': ('Technology Innovation', 'Next-generation product development and roadmap')
        }
        
        for theme, score in top_themes:
            if theme in theme_descriptions:
                title, description = theme_descriptions[theme]
                importance = 'high' if score > 10 else 'medium'
                
                focuses.append({
                    'title': title,
                    'description': description,
                    'importance': importance,
                    'keyword_count': score
                })
        
        # If no themes found, return generic focuses
        if not focuses:
            focuses = [
                {
                    'title': 'Business Performance',
                    'description': 'Overall business results and financial performance',
                    'importance': 'high'
                },
                {
                    'title': 'Market Outlook',
                    'description': 'Future market opportunities and growth projections',
                    'importance': 'medium'
                }
            ]
        
        return focuses