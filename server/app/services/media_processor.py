from PIL import Image, ImageDraw, ImageFont
import moviepy.editor as mp
import requests
from io import BytesIO
import os
import uuid

class MediaProcessor:
    @staticmethod
    def add_watermark(image_url: str, watermark_text: str) -> str:
        try:
            response = requests.get(image_url)
            img = Image.open(BytesIO(response.content))
            
            draw = ImageDraw.Draw(img)
            
            width, height = img.size
            try:
                font = ImageFont.truetype("arial.ttf", size=int(height/20))
            except:
                font = ImageFont.load_default()
            
            bbox = font.getbbox(watermark_text)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            x = width - text_width - 10
            y = height - text_height - 10
            
            draw.text((x, y), watermark_text, fill=(255, 255, 255, 128), font=font)
            
            filename = f"watermarked_{uuid.uuid4().hex}.jpg"
            filepath = f"static/images/{filename}"
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            img.save(filepath)
            
            return filepath
            
        except Exception as e:
            print(f"Watermark error: {e}")
            return image_url
    
    @staticmethod
    def add_video_intro(video_url: str, intro_path: str) -> str:
        try:
            intro = mp.VideoFileClip(intro_path)
            main_video = mp.VideoFileClip(video_url)
            
            final_video = mp.concatenate_videoclips([intro, main_video])
            
            filename = f"intro_added_{uuid.uuid4().hex}.mp4"
            filepath = f"static/videos/{filename}"
            
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            final_video.write_videofile(filepath)
            
            return filepath
            
        except Exception as e:
            print(f"Video processing error: {e}")
            return video_url