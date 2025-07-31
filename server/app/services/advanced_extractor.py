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
                    
                    # Extract video URLs
                    video_urls = AdvancedNewsExtractor._extract_video_urls(html, url)
                    if video_urls:
                        basic_content["video_url"] = video_urls[0] if video_urls else None
                    
                    enhanced_content = {
                        **basic_content,
                        "og_data": og_data,
                        "structured_data": structured_data,
                        "word_count": len(basic_content.get("content", "").split()),
                        "reading_time": AdvancedNewsExtractor._calculate_reading_time(basic_content.get("content", "")),
                        "language": basic_content.get("meta_lang") or AdvancedNewsExtractor._detect_language(basic_content.get("content", "")),
                        "tags": AdvancedNewsExtractor._extract_tags(html),
                        "video_urls": video_urls
                    }
                    
                    return enhanced_content
                    
        except Exception as e:
            return {**basic_content, "enhancement_error": str(e)}
    
    @staticmethod
    def _extract_video_urls(html: str, base_url: str) -> List[str]:
        """Extract video URLs from HTML"""
        video_urls = []
        
        try:
            # Look for video tags
            video_pattern = r'<video[^>]*src=["\']([^"\']+)["\'][^>]*>'
            video_matches = re.findall(video_pattern, html, re.IGNORECASE)
            for match in video_matches:
                if match.startswith('http'):
                    video_urls.append(match)
                else:
                    video_urls.append(urljoin(base_url, match))
            
            # Look for source tags inside video
            source_pattern = r'<source[^>]*src=["\']([^"\']+)["\'][^>]*>'
            source_matches = re.findall(source_pattern, html, re.IGNORECASE)
            for match in source_matches:
                if match.startswith('http'):
                    video_urls.append(match)
                else:
                    video_urls.append(urljoin(base_url, match))
            
            # Look for iframe embeds (YouTube, Vimeo, etc.)
            iframe_pattern = r'<iframe[^>]*src=["\']([^"\']+)["\'][^>]*>'
            iframe_matches = re.findall(iframe_pattern, html, re.IGNORECASE)
            for match in iframe_matches:
                if any(domain in match.lower() for domain in ['youtube', 'vimeo', 'dailymotion', 'facebook', 'player']):
                    video_urls.append(match)
            
            # Look for video player divs with data attributes (common in news sites)
            video_player_patterns = [
                r'<div[^>]*class=["\'][^"\']*video-player[^"\']*["\'][^>]*data-src=["\']([^"\']+)["\']',
                r'<div[^>]*class=["\'][^"\']*player[^"\']*["\'][^>]*data-video=["\']([^"\']+)["\']',
                r'<div[^>]*class=["\'][^"\']*video[^"\']*["\'][^>]*data-url=["\']([^"\']+)["\']',
                r'<div[^>]*id=["\'][^"\']*video[^"\']*["\'][^>]*data-src=["\']([^"\']+)["\']',
                # Turkish news site specific patterns
                r'<div[^>]*class=["\'][^"\']*haber-video[^"\']*["\'][^>]*data-src=["\']([^"\']+)["\']',
                r'<div[^>]*class=["\'][^"\']*video-haber[^"\']*["\'][^>]*data-url=["\']([^"\']+)["\']',
                r'<div[^>]*class=["\'][^"\']*video-container[^"\']*["\'][^>]*data-video=["\']([^"\']+)["\']',
            ]
            
            for pattern in video_player_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                for match in matches:
                    if match.startswith('http'):
                        video_urls.append(match)
                    else:
                        video_urls.append(urljoin(base_url, match))
            
            # Look for video elements with specific news site patterns
            news_video_patterns = [
                r'<video[^>]*class=["\'][^"\']*news-video[^"\']*["\'][^>]*src=["\']([^"\']+)["\']',
                r'<video[^>]*class=["\'][^"\']*haber-video[^"\']*["\'][^>]*src=["\']([^"\']+)["\']',
                r'<video[^>]*class=["\'][^"\']*content-video[^"\']*["\'][^>]*src=["\']([^"\']+)["\']',
                r'<video[^>]*class=["\'][^"\']*video-haber[^"\']*["\'][^>]*src=["\']([^"\']+)["\']',
                r'<video[^>]*class=["\'][^"\']*video-content[^"\']*["\'][^>]*src=["\']([^"\']+)["\']',
            ]
            
            for pattern in news_video_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE)
                for match in matches:
                    if match.startswith('http'):
                        video_urls.append(match)
                    else:
                        video_urls.append(urljoin(base_url, match))
            
            # Look for script tags with video data (common in modern news sites)
            script_video_patterns = [
                r'<script[^>]*>.*?["\']video_url["\']\s*:\s*["\']([^"\']+)["\']',
                r'<script[^>]*>.*?["\']videoUrl["\']\s*:\s*["\']([^"\']+)["\']',
                r'<script[^>]*>.*?["\']video["\']\s*:\s*["\']([^"\']+)["\']',
                r'<script[^>]*>.*?video_url\s*=\s*["\']([^"\']+)["\']',
                r'<script[^>]*>.*?videoUrl\s*=\s*["\']([^"\']+)["\']',
            ]
            
            for pattern in script_video_patterns:
                matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
                for match in matches:
                    if match.startswith('http'):
                        video_urls.append(match)
                    else:
                        video_urls.append(urljoin(base_url, match))
            
            # Look for JSON-LD structured data with video
            json_ld_pattern = r'<script type="application/ld\+json">(.*?)</script>'
            json_ld_matches = re.findall(json_ld_pattern, html, re.DOTALL)
            
            for json_ld in json_ld_matches:
                try:
                    data = json.loads(json_ld)
                    if isinstance(data, dict):
                        # Check for video content
                        if 'video' in data:
                            video_data = data['video']
                            if isinstance(video_data, dict) and 'contentUrl' in video_data:
                                video_urls.append(video_data['contentUrl'])
                        elif 'contentUrl' in data and any(ext in data.get('@type', '').lower() for ext in ['video', 'media']):
                            video_urls.append(data['contentUrl'])
                except:
                    continue
            
            # Look for Open Graph video data
            og_video_pattern = r'<meta[^>]*property=["\']og:video["\'][^>]*content=["\']([^"\']+)["\']'
            og_video_matches = re.findall(og_video_pattern, html, re.IGNORECASE)
            for match in og_video_matches:
                video_urls.append(match)
            
            # Look for Twitter video data
            twitter_video_pattern = r'<meta[^>]*name=["\']twitter:player:stream["\'][^>]*content=["\']([^"\']+)["\']'
            twitter_video_matches = re.findall(twitter_video_pattern, html, re.IGNORECASE)
            for match in twitter_video_matches:
                video_urls.append(match)
            
            # Look for common video file extensions in links (but filter out images)
            video_extensions = ['.mp4', '.webm', '.ogg', '.mov', '.avi', '.mkv', '.flv', '.m4v', '.3gp']
            image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.svg', '.ico']
            
            for ext in video_extensions:
                ext_pattern = rf'href=["\']([^"\']*{ext}[^"\']*)["\']'
                ext_matches = re.findall(ext_pattern, html, re.IGNORECASE)
                for match in ext_matches:
                    # Check if URL contains any image extensions (to avoid false positives)
                    if not any(img_ext in match.lower() for img_ext in image_extensions):
                        if match.startswith('http'):
                            video_urls.append(match)
                        else:
                            video_urls.append(urljoin(base_url, match))
            
            # Filter out image files and non-video content
            filtered_videos = []
            for video_url in video_urls:
                # Skip if URL contains image extensions
                if any(img_ext in video_url.lower() for img_ext in image_extensions):
                    continue
                
                # Skip if URL contains common image patterns
                if any(pattern in video_url.lower() for pattern in ['/images/', '/img/', 'image', 'photo', 'picture']):
                    continue
                
                # Skip if URL contains video but is actually an image (common false positive)
                if any(video_ext in video_url.lower() for video_ext in video_extensions):
                    # Double check it's not an image with video extension
                    if not any(img_ext in video_url.lower() for img_ext in image_extensions):
                        filtered_videos.append(video_url)
                else:
                    # For non-extension URLs (embeds), keep them
                    filtered_videos.append(video_url)
            
            # Remove duplicates and filter valid URLs
            unique_videos = []
            for video_url in filtered_videos:
                if video_url not in unique_videos and video_url.strip():
                    unique_videos.append(video_url)
            
            return unique_videos[:5]  # Limit to 5 videos
            
        except Exception as e:
            print(f"Error extracting video URLs: {e}")
            return []
    
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