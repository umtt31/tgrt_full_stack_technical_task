import requests
from newspaper import Article
from typing import Dict, Optional
from datetime import datetime
import re

class NewsExtractor:
    @staticmethod
    def extract_content(url: str) -> Dict:
        """
        Extract content from a news URL using newspaper3k
        
        Returns:
            Dict with either success or error information
        """
        try:
            # Download and parse the article
            article = Article(url)
            article.download()
            article.parse()
            
            # Extract basic information
            title = article.title or "No title available"
            content = article.text or "No content available"
            publish_date = article.publish_date
            image_url = None
            
            # Try to get the main image
            if article.top_image:
                image_url = article.top_image
            elif article.images:
                image_url = article.images[0]
            
            # Format publish date
            formatted_date = None
            if publish_date:
                if isinstance(publish_date, str):
                    # Try to parse string date
                    try:
                        publish_date = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
                    except:
                        pass
                if isinstance(publish_date, datetime):
                    formatted_date = publish_date
            
            return {
                "title": title,
                "content": content,
                "publish_date": formatted_date,
                "image_url": image_url,
                "success": True
            }
            
        except Exception as e:
            return {
                "error": f"Failed to extract content: {str(e)}",
                "success": False
            } 