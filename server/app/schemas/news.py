from pydantic import BaseModel, HttpUrl, ConfigDict
from datetime import datetime
from typing import Optional

class NewsBase(BaseModel):
    url: HttpUrl

class NewsCreate(NewsBase):
    pass

class NewsResponse(NewsBase):
    id: int
    title: Optional[str]
    content: Optional[str]
    publish_date: Optional[datetime]
    image_url: Optional[str]
    processed_image_url: Optional[str]
    video_url: Optional[str]
    processed_video_url: Optional[str]
    created_at: datetime
    user_id: int
    
    model_config = ConfigDict(from_attributes=True)