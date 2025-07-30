#!/usr/bin/env python3
"""
Test script for advanced news extraction
"""

import sys
import os
import asyncio

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

async def test_advanced_extraction():
    """Test the advanced news extraction with the Turkish news URL"""
    try:
        from app.services.advanced_extractor import AdvancedNewsExtractor
        
        # Test URL from the user's example
        test_url = "https://www.haber7.com/dunya/haber/3551186-emekli-generalden-israili-sarsan-iddia-turkiye-israille-savasa-hazirlaniyor"
        
        print("Testing advanced news extraction...")
        print(f"URL: {test_url}")
        print("-" * 50)
        
        result = await AdvancedNewsExtractor.extract_with_metadata(test_url)
        
        if result["success"]:
            print("✓ Advanced extraction successful!")
            print(f"Title: {result['title']}")
            print(f"Content Length: {len(result['content'])} characters")
            print(f"Publish Date: {result['publish_date']}")
            print(f"Image URL: {result['image_url']}")
            print(f"Meta Keywords: {result.get('meta_keywords')}")
            print(f"Meta Language: {result.get('meta_lang')}")
            print(f"Language (detected): {result.get('language')}")
            print(f"Word Count: {result.get('word_count')}")
            print(f"Reading Time: {result.get('reading_time')} minutes")
            print(f"Tags: {result.get('tags')}")
            
            # Show enhanced metadata
            if result.get('og_data'):
                print(f"Open Graph Data: {len(result['og_data'])} items")
                for key, value in list(result['og_data'].items())[:3]:  # Show first 3
                    print(f"  {key}: {value}")
            
            if result.get('structured_data'):
                print(f"Structured Data: {len(result['structured_data'])} items")
        else:
            print("✗ Advanced extraction failed!")
            print(f"Error: {result['error']}")
            
    except Exception as e:
        print(f"✗ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_advanced_extraction()) 