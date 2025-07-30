import asyncio
import aiohttp
from typing import Dict, List, Optional
from urllib.parse import urljoin, urlparse
import re
from datetime import datetime
import json
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
                    
                    # Enhanced date extraction from HTML
                    enhanced_publish_date = AdvancedNewsExtractor._extract_publish_date_from_html(html)
                    if enhanced_publish_date and not basic_content.get("publish_date"):
                        basic_content["publish_date"] = enhanced_publish_date
                    
                    # Enhanced meta keywords extraction
                    enhanced_keywords = AdvancedNewsExtractor._extract_meta_keywords_from_html(html)
                    if enhanced_keywords:
                        basic_content["meta_keywords"] = enhanced_keywords
                    
                    # Enhanced language detection
                    enhanced_lang = AdvancedNewsExtractor._extract_meta_lang_from_html(html)
                    if enhanced_lang:
                        basic_content["meta_lang"] = enhanced_lang
                    
                    enhanced_content = {
                        **basic_content,
                        "og_data": og_data,
                        "structured_data": structured_data,
                        "word_count": len(basic_content.get("content", "").split()),
                        "reading_time": AdvancedNewsExtractor._calculate_reading_time(basic_content.get("content", "")),
                        "language": basic_content.get("meta_lang") or AdvancedNewsExtractor._detect_language(basic_content.get("content", "")),
                        "tags": AdvancedNewsExtractor._extract_tags(html)
                    }
                    
                    return enhanced_content
                    
        except Exception as e:
            return {**basic_content, "enhancement_error": str(e)}
    
    @staticmethod
    def _extract_publish_date_from_html(html: str) -> Optional[datetime]:
        """Enhanced date extraction from HTML metadata"""
        try:
            # Check for common date meta tags
            date_fields = ['datePublished', 'dateCreated', 'uploadDate', 'publishedTime']
            
            # Look for JSON-LD structured data
            json_ld_pattern = r'<script type="application/ld\+json">(.*?)</script>'
            json_ld_matches = re.findall(json_ld_pattern, html, re.DOTALL)
            
            for json_ld in json_ld_matches:
                try:
                    data = json.loads(json_ld)
                    if isinstance(data, dict):
                        for field in date_fields:
                            if field in data:
                                date_str = data[field]
                                if isinstance(date_str, str):
                                    return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                except:
                    continue
            
            # Look for meta tags
            for field in date_fields:
                meta_pattern = rf'<meta[^>]*property=["\']{field}["\'][^>]*content=["\']([^"\']+)["\']'
                match = re.search(meta_pattern, html)
                if match:
                    date_str = match.group(1)
                    try:
                        return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                    except:
                        continue
                        
        except Exception as e:
            print(f"Error extracting date from HTML: {e}")
        
        return None
    
    @staticmethod
    def _extract_meta_keywords_from_html(html: str) -> Optional[str]:
        """Extract meta keywords from HTML"""
        try:
            # Look for keywords in JSON-LD
            json_ld_pattern = r'<script type="application/ld\+json">(.*?)</script>'
            json_ld_matches = re.findall(json_ld_pattern, html, re.DOTALL)
            
            for json_ld in json_ld_matches:
                try:
                    data = json.loads(json_ld)
                    if isinstance(data, dict):
                        if 'keywords' in data:
                            keywords = data['keywords']
                            if isinstance(keywords, list):
                                return json.dumps(keywords)
                            elif isinstance(keywords, str):
                                return json.dumps([keywords])
                except:
                    continue
            
            # Look for meta keywords tag
            meta_pattern = r'<meta[^>]*name=["\']keywords["\'][^>]*content=["\']([^"\']+)["\']'
            match = re.search(meta_pattern, html)
            if match:
                keywords_str = match.group(1)
                keywords_list = [kw.strip() for kw in keywords_str.split(',')]
                return json.dumps(keywords_list)
                
        except Exception as e:
            print(f"Error extracting meta keywords from HTML: {e}")
        
        return None
    
    @staticmethod
    def _extract_meta_lang_from_html(html: str) -> Optional[str]:
        """Extract meta language from HTML"""
        try:
            # Look for lang attribute in html tag
            lang_pattern = r'<html[^>]*lang=["\']([^"\']+)["\']'
            match = re.search(lang_pattern, html)
            if match:
                return match.group(1)
            
            # Look for meta language tag
            meta_pattern = r'<meta[^>]*http-equiv=["\']content-language["\'][^>]*content=["\']([^"\']+)["\']'
            match = re.search(meta_pattern, html)
            if match:
                return match.group(1)
                
        except Exception as e:
            print(f"Error extracting meta language from HTML: {e}")
        
        return None
    
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