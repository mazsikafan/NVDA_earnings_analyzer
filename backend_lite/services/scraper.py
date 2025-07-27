"""
Lightweight Motley Fool Earnings Call Transcript Scraper
"""
import re
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)


class MotleyFoolScraper:
    """Simplified scraper for Motley Fool earnings transcripts"""
    
    BASE_URL = "https://www.fool.com"
    NVIDIA_QUOTE_URL = "https://www.fool.com/quote/nasdaq/nvidia/nvda/"
    RATE_LIMIT_DELAY = 1.0
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.logger = logging.getLogger(__name__)
    
    def find_transcript_urls(self, ticker: str, num_quarters: int = 4) -> List[str]:
        """Find earnings call transcript URLs for NVIDIA"""
        self.logger.info(f"Searching for {ticker} transcript URLs")
        
        try:
            # Get NVIDIA quote page
            response = self.session.get(self.NVIDIA_QUOTE_URL, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find transcript links
            transcript_urls = []
            
            # Look for earnings call transcript links
            for link in soup.find_all('a', href=True):
                href = link['href']
                text = link.get_text(strip=True).lower()
                
                if 'earnings-call-transcript' in href and ('nvidia' in text or 'nvda' in text):
                    full_url = href if href.startswith('http') else self.BASE_URL + href
                    if full_url not in transcript_urls:
                        transcript_urls.append(full_url)
            
            # Also check the transcripts section
            transcripts_section = soup.find('section', {'data-testid': 'transcripts'})
            if transcripts_section:
                for link in transcripts_section.find_all('a', href=True):
                    href = link['href']
                    if 'earnings-call-transcript' in href:
                        full_url = href if href.startswith('http') else self.BASE_URL + href
                        if full_url not in transcript_urls:
                            transcript_urls.append(full_url)
            
            # Sort by date (most recent first)
            transcript_urls = transcript_urls[:num_quarters]
            
            self.logger.info(f"Found {len(transcript_urls)} transcript URLs")
            return transcript_urls
            
        except Exception as e:
            self.logger.error(f"Error finding transcript URLs: {e}")
            # Return some example URLs as fallback
            return [
                "https://www.fool.com/earnings/call-transcripts/2024/11/20/nvidia-nvda-q3-2025-earnings-call-transcript/",
                "https://www.fool.com/earnings/call-transcripts/2024/08/28/nvidia-nvda-q2-2025-earnings-call-transcript/",
                "https://www.fool.com/earnings/call-transcripts/2024/05/22/nvidia-nvda-q1-2025-earnings-call-transcript/",
                "https://www.fool.com/earnings/call-transcripts/2024/02/21/nvidia-nvda-q4-2024-earnings-call-transcript/"
            ][:num_quarters]
    
    def scrape_transcript(self, url: str) -> Optional[Dict]:
        """Scrape a single transcript"""
        self.logger.info(f"Scraping transcript from: {url}")
        
        try:
            time.sleep(self.RATE_LIMIT_DELAY)
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract title
            title = soup.find('h1')
            title_text = title.get_text(strip=True) if title else "Unknown Title"
            
            # Extract quarter and year from title
            quarter_match = re.search(r'Q(\d)\s+(\d{4})', title_text)
            if quarter_match:
                quarter = int(quarter_match.group(1))
                year = int(quarter_match.group(2))
            else:
                # Try alternate format
                date_match = re.search(r'(\d{4})', title_text)
                year = int(date_match.group(1)) if date_match else datetime.now().year
                quarter = 1  # Default
            
            # Extract article content - try multiple selectors
            article = None
            
            # First try the specific article body selector
            article = soup.select_one("div[class*='article-body']")
            
            if not article:
                # Try other selectors
                selectors = [
                    ('div', {'class': 'tailwind-article-body'}),
                    ('article', {}),
                    ('div', {'class': 'article-content'}),
                    ('main', {})
                ]
                
                for tag, attrs in selectors:
                    article = soup.find(tag, attrs)
                    if article:
                        break
            
            if not article:
                # Try to find any large text block
                all_divs = soup.find_all('div')
                for div in all_divs:
                    text = div.get_text(strip=True)
                    if len(text) > 5000 and 'earnings call' in text.lower():
                        article = div
                        break
            
            if not article:
                self.logger.error("Could not find article content")
                return None
            
            # Get all text content
            full_text = article.get_text(separator='\n', strip=True)
            
            # Clean up the text
            full_text = re.sub(r'\n{3,}', '\n\n', full_text)
            full_text = re.sub(r'[ \t]+', ' ', full_text)
            
            return {
                'url': url,
                'title': title_text,
                'quarter': quarter,
                'year': year,
                'full_text': full_text,
                'scraped_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Error scraping transcript: {e}")
            return None