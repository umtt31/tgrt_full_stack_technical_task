import sys
import traceback
from datetime import datetime

def debug_article(url: str):
    """Debug function to examine article object structure"""
    try:
        # Try to import newspaper
        try:
            from newspaper import Article
            print("✓ newspaper library imported successfully")
        except ImportError as e:
            print(f"✗ Failed to import newspaper: {e}")
            print("Please install newspaper3k: pip install newspaper3k")
            return
        
        print(f"\n=== Testing URL: {url} ===")
        
        article = Article(url)
        print("✓ Article object created")
        
        article.download()
        print("✓ Article downloaded")
        
        article.parse()
        print("✓ Article parsed")
        
        print("\n=== Basic Article Info ===")
        print(f"Title: {article.title}")
        print(f"Text Length: {len(article.text) if article.text else 0}")
        print(f"Top Image: {article.top_image}")
        print(f"Number of Images: {len(article.images) if article.images else 0}")
        
        print("\n=== Date Information ===")
        print(f"Publish Date: {article.publish_date}")
        print(f"Publish Date Type: {type(article.publish_date)}")
        
        # Test enhanced extraction
        print("\n=== Enhanced Extraction Test ===")
        try:
            from app.services.news_extractor import NewsExtractor
            extracted = NewsExtractor.extract_content(url)
            
            if extracted["success"]:
                print(f"✓ Enhanced Title: {extracted['title']}")
                print(f"✓ Enhanced Publish Date: {extracted['publish_date']}")
                print(f"✓ Meta Keywords: {extracted['meta_keywords']}")
                print(f"✓ Meta Language: {extracted['meta_lang']}")
            else:
                print(f"✗ Enhanced extraction failed: {extracted['error']}")
        except Exception as e:
            print(f"✗ Error testing enhanced extraction: {e}")
        
        # Check for alternative date fields
        print("\n=== Checking for Alternative Date Fields ===")
        date_attrs = ['publish_date', 'published', 'date', 'pub_date', 'published_date']
        for attr in date_attrs:
            if hasattr(article, attr):
                value = getattr(article, attr)
                print(f"{attr}: {value} (type: {type(value)})")
        
        # Test date parsing
        print("\n=== Date Parsing Test ===")
        publish_date = article.publish_date
        if publish_date:
            print(f"Original publish_date: {publish_date}")
            print(f"Type: {type(publish_date)}")
            
            if isinstance(publish_date, str):
                try:
                    parsed_date = datetime.fromisoformat(publish_date.replace('Z', '+00:00'))
                    print(f"✓ Parsed as datetime: {parsed_date}")
                except Exception as e:
                    print(f"✗ Failed to parse as datetime: {e}")
                    # Try alternative parsing
                    try:
                        from dateutil import parser
                        parsed_date = parser.parse(publish_date)
                        print(f"✓ Parsed with dateutil: {parsed_date}")
                    except ImportError:
                        print("dateutil not available for alternative parsing")
                    except Exception as e2:
                        print(f"✗ Alternative parsing also failed: {e2}")
            elif isinstance(publish_date, datetime):
                print(f"✓ Already datetime: {publish_date}")
        else:
            print("✗ No publish_date found")
            
        # Print all available attributes
        print("\n=== All Available Attributes ===")
        for attr in dir(article):
            if not attr.startswith('_'):
                try:
                    value = getattr(article, attr)
                    if not callable(value):
                        print(f"{attr}: {value}")
                except Exception as e:
                    print(f"{attr}: Error accessing - {e}")
                    
    except Exception as e:
        print(f"✗ Error during debugging: {e}")
        print("Full traceback:")
        traceback.print_exc()

if __name__ == "__main__":
    # Test with the Turkish news URL
    test_url = "https://www.haber7.com/dunya/haber/3551186-emekli-generalden-israili-sarsan-iddia-turkiye-israille-savasa-hazirlaniyor"
    debug_article(test_url) 