from celery import Celery
from app.config import settings
from app.services.media_processor import MediaProcessor
import os

# Initialize Celery
celery_app = Celery(
    "tgrt_full_stack_technical_task",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task
def process_image_watermark(image_url: str, watermark_text: str) -> str:
    """Background task to add watermark to image"""
    try:
        result = MediaProcessor.add_watermark(image_url, watermark_text)
        return result
    except Exception as e:
        print(f"Error processing image: {e}")
        return image_url

@celery_app.task
def process_video_intro(video_url: str, intro_path: str) -> str:
    """Background task to add intro to video"""
    try:
        result = MediaProcessor.add_video_intro(video_url, intro_path)
        return result
    except Exception as e:
        print(f"Error processing video: {e}")
        return video_url

@celery_app.task
def cleanup_temp_files():
    """Background task to clean up temporary media files"""
    try:
        # Clean up files older than 24 hours
        import time
        import glob
        
        current_time = time.time()
        temp_patterns = [
            "static/images/watermarked_*.jpg",
            "static/videos/intro_added_*.mp4"
        ]
        
        for pattern in temp_patterns:
            for file_path in glob.glob(pattern):
                if os.path.isfile(file_path):
                    file_age = current_time - os.path.getmtime(file_path)
                    if file_age > 86400:  # 24 hours
                        os.remove(file_path)
                        print(f"Cleaned up: {file_path}")
    except Exception as e:
        print(f"Error during cleanup: {e}")