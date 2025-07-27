"""
Debug script to test the scraper directly
"""
import requests
from bs4 import BeautifulSoup

url = "https://www.fool.com/earnings/call-transcripts/2024/11/20/nvidia-nvda-q3-2025-earnings-call-transcript/"

print(f"Fetching: {url}")
response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
print(f"Status code: {response.status_code}")

soup = BeautifulSoup(response.content, 'html.parser')

# Debug: Check page structure
print("\nChecking page structure...")

# Try to find the article content
selectors_to_try = [
    "div[class*='article']",
    "div[class*='content']", 
    "div[class*='body']",
    "main",
    "article",
    "div[data-id='article-content']"
]

for selector in selectors_to_try:
    elements = soup.select(selector)
    if elements:
        print(f"\nFound {len(elements)} elements with selector: {selector}")
        for i, elem in enumerate(elements[:3]):
            text_preview = elem.get_text(strip=True)[:200]
            print(f"  Element {i}: {text_preview}...")

# Check for any divs with substantial text
print("\nLooking for divs with substantial text...")
all_divs = soup.find_all('div')
for div in all_divs:
    text = div.get_text(strip=True)
    if len(text) > 5000:
        print(f"\nFound large div with {len(text)} chars")
        print(f"Classes: {div.get('class', 'No classes')}")
        print(f"ID: {div.get('id', 'No ID')}")
        print(f"Preview: {text[:300]}...")
        break

# Check if there's a paywall or login requirement
if 'sign in' in response.text.lower() or 'subscribe' in response.text.lower():
    print("\n⚠️  Page may require login or subscription")