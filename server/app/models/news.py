from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class NewsArticle(Base):
    __tablename__ = "news_articles"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    title = Column(String)
    content = Column(Text)
    publish_date = Column(DateTime)
    image_url = Column(String)
    processed_image_url = Column(String)
    video_url = Column(String)
    processed_video_url = Column(String)
    meta_keywords = Column(Text)
    meta_lang = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="news_articles")