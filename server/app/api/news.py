from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.user import User
from app.models.news import NewsArticle
from app.schemas.news import NewsCreate, NewsResponse
from app.services.auth import AuthService
from app.services.news_extractor import NewsExtractor
from app.services.media_processor import MediaProcessor
from app.config import settings

router = APIRouter()

@router.post("/extract", response_model=NewsResponse)
async def extract_news(
    news_data: NewsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    # Extract content
    extracted = NewsExtractor.extract_content(str(news_data.url))
    
    if not extracted["success"]:
        raise HTTPException(status_code=400, detail=extracted["error"])
    
    # Create news article
    db_news = NewsArticle(
        url=str(news_data.url),
        title=extracted["title"],
        content=extracted["content"],
        publish_date=extracted["publish_date"] if extracted["publish_date"] else None,
        image_url=extracted["image_url"],
        user_id=current_user.id
    )
    
    # Process media if available
    if extracted["image_url"]:
        processed_image = MediaProcessor.add_watermark(
            extracted["image_url"], 
            settings.WATERMARK_TEXT
        )
        db_news.processed_image_url = processed_image
    
    db.add(db_news)
    db.commit()
    db.refresh(db_news)
    
    return db_news

@router.get("/", response_model=List[NewsResponse])
async def get_user_news(
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    return db.query(NewsArticle).filter(NewsArticle.user_id == current_user.id).all()

@router.get("/{news_id}", response_model=NewsResponse)
async def get_news_detail(
    news_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    news = db.query(NewsArticle).filter(
        NewsArticle.id == news_id,
        NewsArticle.user_id == current_user.id
    ).first()
    
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    return news

@router.delete("/{news_id}")
async def delete_news(
    news_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(AuthService.get_current_user)
):
    news = db.query(NewsArticle).filter(
        NewsArticle.id == news_id,
        NewsArticle.user_id == current_user.id
    ).first()
    
    if not news:
        raise HTTPException(status_code=404, detail="News not found")
    
    db.delete(news)
    db.commit()
    
    return {"message": "News deleted successfully"}