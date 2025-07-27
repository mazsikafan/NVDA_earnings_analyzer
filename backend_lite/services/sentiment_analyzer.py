"""
Lightweight FinBERT Sentiment Analysis
"""
import logging
from typing import List, Dict
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification

logging.basicConfig(level=logging.INFO)


class SentimentAnalyzer:
    """FinBERT-based sentiment analysis for financial text"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.model = None
        self.tokenizer = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self._load_models()
    
    def _load_models(self):
        """Load FinBERT model"""
        try:
            # Load FinBERT for both management and Q&A sentiment
            self.logger.info("Loading FinBERT model...")
            model_name = "ProsusAI/finbert"
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            self.model.to(self.device)
            self.model.eval()
            self.logger.info("FinBERT model loaded successfully")
            
        except Exception as e:
            self.logger.error(f"Error loading model: {e}")
            # Fallback to mock sentiment
            self.model = None
    
    def analyze_management(self, segments: List[Dict]) -> Dict:
        """Analyze sentiment of management remarks"""
        if not segments:
            return {'sentiment': 'neutral', 'confidence': 0.0}
        
        # Filter out segments that are too short or likely boilerplate
        meaningful_segments = [
            seg for seg in segments 
            if seg['word_count'] > 50 and 
            not self._is_boilerplate(seg['content'])
        ]
        
        if not meaningful_segments:
            # Fallback to original segments if filtering removed everything
            meaningful_segments = segments[:3]
        
        # Combine meaningful management remarks (limit to avoid token overflow)
        combined_text = ' '.join([seg['content'] for seg in meaningful_segments[:3]])
        
        # Further clean the text
        combined_text = self._clean_for_sentiment(combined_text)
        
        return self._analyze_text(combined_text, "Management Remarks")
    
    def analyze_qa(self, segments: List[Dict]) -> Dict:
        """Analyze sentiment of Q&A session using FinBERT"""
        if not segments:
            return {'sentiment': 'neutral', 'confidence': 0.0}
        
        # Focus on substantial executive responses
        executive_responses = [
            seg for seg in segments 
            if seg.get('speaker_type') == 'executive' and 
            seg['word_count'] > 30 and
            not self._is_boilerplate(seg['content'])
        ]
        
        if not executive_responses:
            # Fallback to any responses if no executive ones found
            executive_responses = [seg for seg in segments if seg['word_count'] > 30][:3]
        
        if not executive_responses:
            return {'sentiment': 'neutral', 'confidence': 0.0}
        
        # Combine meaningful Q&A responses (limit to avoid token overflow)
        combined_text = ' '.join([seg['content'] for seg in executive_responses[:3]])
        
        # Clean the text
        combined_text = self._clean_for_sentiment(combined_text)
        
        return self._analyze_qa_text(combined_text)
    
    def _is_boilerplate(self, text: str) -> bool:
        """Check if text is likely boilerplate/metadata rather than meaningful content"""
        text_lower = text.lower()
        boilerplate_indicators = [
            'the motley fool',
            'earnings call',
            'conference operator',
            'good afternoon',
            'welcome everyone',
            'my name is',
            'operator',
            'image source'
        ]
        
        # If text is too short or contains too many boilerplate indicators
        if len(text.split()) < 20:
            return True
            
        boilerplate_count = sum(1 for indicator in boilerplate_indicators if indicator in text_lower)
        return boilerplate_count > 1
    
    def _clean_for_sentiment(self, text: str) -> str:
        """Clean text specifically for sentiment analysis"""
        # Remove remaining metadata patterns
        import re
        
        # Remove patterns that don't contribute to sentiment
        patterns_to_remove = [
            r'\([A-Z]{2,5}\s*[+-]?\d*\.?\d*%?\)',  # Stock symbols and changes
            r'Q\d+\s+\d{4}',  # Quarter references
            r'\b\d{1,2}:\d{2}\s*[ap]\.?m\.?\b',  # Times
            r'\b[A-Z][a-z]+\s+\d{1,2},\s+\d{4}\b',  # Dates
        ]
        
        for pattern in patterns_to_remove:
            text = re.sub(pattern, ' ', text, flags=re.IGNORECASE)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    def _analyze_text(self, text: str, section_name: str) -> Dict:
        """Analyze sentiment of text using FinBERT"""
        if not self.model:
            # Fallback mock sentiment
            return self._mock_sentiment(text)
        
        try:
            # Truncate text to model's max length
            max_length = 512
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, 
                                  max_length=max_length, padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                
            # FinBERT labels: [positive, negative, neutral]
            probs = predictions[0].cpu().numpy()
            sentiment_labels = ['positive', 'negative', 'neutral']
            max_idx = probs.argmax()
            
            sentiment = sentiment_labels[max_idx]
            confidence = float(probs[max_idx])
            
            self.logger.info(f"{section_name} sentiment: {sentiment} (confidence: {confidence:.2f})")
            
            return {
                'sentiment': sentiment,
                'confidence': confidence,
                'scores': {
                    'positive': float(probs[0]),
                    'negative': float(probs[1]),
                    'neutral': float(probs[2])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error in sentiment analysis: {e}")
            return self._mock_sentiment(text)
    
    def _analyze_qa_text(self, text: str) -> Dict:
        """Analyze Q&A sentiment using FinBERT"""
        if not self.model:
            # Fallback mock sentiment
            return self._mock_sentiment(text)
        
        try:
            # Truncate text to model's max length
            max_length = 512
            inputs = self.tokenizer(text, return_tensors="pt", truncation=True, 
                                   max_length=max_length, padding=True)
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
                
            # FinBERT labels: [positive, negative, neutral]
            probs = predictions[0].cpu().numpy()
            sentiment_labels = ['positive', 'negative', 'neutral']
            max_idx = probs.argmax()
            
            sentiment = sentiment_labels[max_idx]
            confidence = float(probs[max_idx])
            
            self.logger.info(f"Q&A Session sentiment (FinBERT): {sentiment} (confidence: {confidence:.2f})")
            
            return {
                'sentiment': sentiment,
                'confidence': confidence,
                'scores': {
                    'positive': float(probs[0]),
                    'negative': float(probs[1]),
                    'neutral': float(probs[2])
                }
            }
            
        except Exception as e:
            self.logger.error(f"Error in Q&A sentiment analysis: {e}")
            return self._mock_sentiment(text)
    
    def _mock_sentiment(self, text: str) -> Dict:
        """Fallback mock sentiment based on keywords"""
        text_lower = text.lower()
        
        positive_words = ['strong', 'growth', 'increase', 'record', 'excellent', 'outperform']
        negative_words = ['decline', 'challenge', 'difficult', 'concern', 'risk', 'weakness']
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            sentiment = 'positive'
            confidence = min(0.6 + (pos_count * 0.05), 0.9)
        elif neg_count > pos_count:
            sentiment = 'negative'
            confidence = min(0.6 + (neg_count * 0.05), 0.9)
        else:
            sentiment = 'neutral'
            confidence = 0.5
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'scores': {
                'positive': confidence if sentiment == 'positive' else (1 - confidence) / 2,
                'negative': confidence if sentiment == 'negative' else (1 - confidence) / 2,
                'neutral': confidence if sentiment == 'neutral' else (1 - confidence) / 2
            }
        }