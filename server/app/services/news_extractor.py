import requests
from newspaper import Article
from typing import Dict
from datetime import datetime
import json
import re

class NewsExtractor:
    @staticmethod
    def extract_content(url: str) -> Dict:
        try:
            article = Article(url)
            article.download()
            article.parse()
            
            title = article.title or "No title available"
            content = article.text or "No content available"
            image_url = None
            
            if article.top_image:
                image_url = article.top_image
            elif article.images:
                image_url = article.images[0]
            
            # Enhanced date extraction
            publish_date = NewsExtractor._extract_publish_date(article)
            
            # Extract meta information
            meta_keywords = NewsExtractor._extract_meta_keywords(article)
            meta_lang = NewsExtractor._extract_meta_lang(article)
            
            return {
                "title": title,
                "content": content,
                "publish_date": publish_date,
                "image_url": image_url,
                "meta_keywords": meta_keywords,
                "meta_lang": meta_lang,
                "success": True
            }
            
        except Exception as e:
            return {
                "error": f"Failed to extract content: {str(e)}",
                "success": False
            }
    
    @staticmethod
    def _extract_publish_date(article: Article) -> datetime:
        """Enhanced date extraction from article metadata"""
        # Try the standard publish_date first
        if article.publish_date:
            if isinstance(article.publish_date, datetime):
                return article.publish_date
            elif isinstance(article.publish_date, str):
                try:
                    return datetime.fromisoformat(article.publish_date.replace('Z', '+00:00'))
                except:
                    pass
        
        # Try to extract from article metadata
        try:
            # Check for common date meta tags
            date_fields = ['datePublished', 'dateCreated', 'uploadDate', 'publishedTime']
            
            # Get the article's HTML and parse for meta tags
            if hasattr(article, 'html') and article.html:
                html_content = article.html
                
                # Look for JSON-LD structured data
                json_ld_pattern = r'<script type="application/ld\+json">(.*?)</script>'
                json_ld_matches = re.findall(json_ld_pattern, html_content, re.DOTALL)
                
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
                    match = re.search(meta_pattern, html_content)
                    if match:
                        date_str = match.group(1)
                        try:
                            return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                        except:
                            continue
                            
        except Exception as e:
            print(f"Error extracting date from metadata: {e}")
        
        return None
    
    @staticmethod
    def _extract_meta_keywords(article: Article) -> str:
        """Extract meta keywords from article"""
        try:
            if hasattr(article, 'html') and article.html:
                html_content = article.html
                
                # Look for keywords in JSON-LD
                json_ld_pattern = r'<script type="application/ld\+json">(.*?)</script>'
                json_ld_matches = re.findall(json_ld_pattern, html_content, re.DOTALL)
                
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
                match = re.search(meta_pattern, html_content)
                if match:
                    keywords_str = match.group(1)
                    keywords_list = [kw.strip() for kw in keywords_str.split(',')]
                    return json.dumps(keywords_list)
                    
        except Exception as e:
            print(f"Error extracting meta keywords: {e}")
        
        return None
    
    @staticmethod
    def _extract_meta_lang(article: Article) -> str:
        """Extract meta language from article"""
        try:
            if hasattr(article, 'html') and article.html:
                html_content = article.html
                
                # Look for lang attribute in html tag
                lang_pattern = r'<html[^>]*lang=["\']([^"\']+)["\']'
                match = re.search(lang_pattern, html_content)
                if match:
                    return match.group(1)
                
                # Look for meta language tag
                meta_pattern = r'<meta[^>]*http-equiv=["\']content-language["\'][^>]*content=["\']([^"\']+)["\']'
                match = re.search(meta_pattern, html_content)
                if match:
                    return match.group(1)
                    
        except Exception as e:
            print(f"Error extracting meta language: {e}")
        
        return None 