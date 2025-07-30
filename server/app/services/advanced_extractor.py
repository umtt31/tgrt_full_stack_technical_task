import asyncio
import aiohttp
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime
from app.services.news_extractor import NewsExtractor

class AdvancedNewsExtractor(NewsExtractor):
    @staticmethod
    async def extract_with_metadata(url: str) -> Dict:
        basic_content = NewsExtractor.extract_content(url)
        
        if not basic_content["success"]:
            return basic_content
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    html = await response.text()
                    
                    og_data = AdvancedNewsExtractor._extract_og_metadata(html)
                    
                    structured_data = AdvancedNewsExtractor._extract_structured_data(html)
                    
                    enhanced_content = {
                        **basic_content,
                        "og_data": og_data,
                        "structured_data": structured_data,
                        "word_count": len(basic_content.get("content", "").split()),
                        "reading_time": AdvancedNewsExtractor._calculate_reading_time(basic_content.get("content", "")),
                        "language": AdvancedNewsExtractor._detect_language(basic_content.get("content", "")),
                        "tags": AdvancedNewsExtractor._extract_tags(html)
                    }
                    
                    return enhanced_content
                    
        except Exception as e:
            return {**basic_content, "enhancement_error": str(e)}
    
    @staticmethod
    def _extract_og_metadata(html: str) -> Dict:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        og_data = {}
        og_tags = soup.find_all('meta', property=re.compile(r'^og:'))
        
        for tag in og_tags:
            property_name = tag.get('property', '').replace('og:', '')
            content = tag.get('content', '')
            if property_name and content:
                og_data[property_name] = content
        
        return og_data
    
    @staticmethod
    def _extract_structured_data(html: str) -> List[Dict]:
        import json
        from bs4 import BeautifulSoup
        
        soup = BeautifulSoup(html, 'html.parser')
        scripts = soup.find_all('script', type='application/ld+json')
        
        structured_data = []
        for script in scripts:
            try:
                data = json.loads(script.string)
                structured_data.append(data)
            except (json.JSONDecodeError, AttributeError):
                continue
        
        return structured_data
    
    @staticmethod
    def _calculate_reading_time(content: str, wpm: int = 200) -> int:
        word_count = len(content.split())
        return max(1, round(word_count / wpm))
    
    @staticmethod
    def _detect_language(content: str) -> Optional[str]:
        try:
            from langdetect import detect
            return detect(content)
        except:
            return None
    
    @staticmethod
    def _extract_tags(html: str) -> List[str]:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        
        tags = []
        
        keywords_tag = soup.find('meta', attrs={'name': 'keywords'})
        if keywords_tag and keywords_tag.get('content'):
            tags.extend([tag.strip() for tag in keywords_tag.get('content').split(',')])
        
        tag_elements = soup.find_all(['span', 'a'], class_=re.compile(r'tag|category|keyword', re.I))
        for element in tag_elements:
            text = element.get_text(strip=True)
            if text and len(text) < 30:
                tags.append(text)
        
        return list(set(tags))[:10]