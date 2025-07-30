#!/usr/bin/env python3
"""
Test script for enhanced news extraction
"""

import sys
import os

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_enhanced_extraction():
    """Test the enhanced news extraction with the Turkish news URL"""
    try:
        from app.services.news_extractor import NewsExtractor
        
        # Test URL from the user's example
        test_url = "https://www.haber7.com/dunya/haber/3551186-emekli-generalden-israili-sarsan-iddia-turkiye-israille-savasa-hazirlaniyor"
        
        print("Testing enhanced news extraction...")
        print(f"URL: {test_url}")
        print("-" * 50)
        
        result = NewsExtractor.extract_content(test_url)
        
        if result["success"]:
            print("✓ Extraction successful!")
            print(f"Title: {result['title']}")
            print(f"Content Length: {len(result['content'])} characters")
            print(f"Publish Date: {result['publish_date']}")
            print(f"Image URL: {result['image_url']}")
            print(f"Meta Keywords: {result['meta_keywords']}")
            print(f"Meta Language: {result['meta_lang']}")
        else:
            print("✗ Extraction failed!")
            print(f"Error: {result['error']}")
            
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_enhanced_extraction() 