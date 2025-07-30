import requests
from newspaper import Article
from typing import Dict
from datetime import datetime

class NewsExtractor:
    @staticmethod
    def extract_content(url: str) -> Dict:
        try:
            article = Article(url)
            article.download()
            article.parse()

            print(article)
            
            title = article.title or "No title available"
            content = article.text or "No content available"
            publish_date = article.publish_date
            image_url = None
            
            if article.top_image:
                image_url = article.top_image
            elif article.images:
                image_url = article.images[0]
            
            formatted_date = None
            if publish_date:
                if isinstance(publish_date, str):
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