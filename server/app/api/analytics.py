from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from app.database import get_db
from app.models.user import User
from app.models.news import NewsArticle
from app.services.auth import AuthService

router = APIRouter()

@router.get("/stats/overview")
async def get_user_stats(
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    
    total_articles = db.query(NewsArticle).filter(NewsArticle.user_id == current_user.id).count()
    
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    recent_articles = db.query(NewsArticle).filter(
        NewsArticle.user_id == current_user.id,
        NewsArticle.created_at >= thirty_days_ago
    ).count()
    
    articles_with_images = db.query(NewsArticle).filter(
        NewsArticle.user_id == current_user.id,
        NewsArticle.image_url.isnot(None)
    ).count()
    
    latest_article = db.query(NewsArticle).filter(
        NewsArticle.user_id == current_user.id
    ).order_by(desc(NewsArticle.created_at)).first()
    
    return {
        "total_articles": total_articles,
        "recent_articles": recent_articles,
        "articles_with_images": articles_with_images,
        "latest_article_date": latest_article.created_at if latest_article else None
    }

@router.get("/stats/timeline")
async def get_extraction_timeline(
    days: int = Query(30, ge=1, le=365),
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    results = db.query(
        func.date(NewsArticle.created_at).label('date'),
        func.count(NewsArticle.id).label('count')
    ).filter(
        NewsArticle.user_id == current_user.id,
        NewsArticle.created_at >= start_date
    ).group_by(
        func.date(NewsArticle.created_at)
    ).order_by('date').all()
    
    return [{"date": str(result.date), "count": result.count} for result in results]

@router.get("/stats/domains")
async def get_top_domains(
    limit: int = Query(10, ge=1, le=50),
    current_user: User = Depends(AuthService.get_current_user),
    db: Session = Depends(get_db)
):
    
    articles = db.query(NewsArticle.url).filter(
        NewsArticle.user_id == current_user.id
    ).all()
    
    domain_counts = {}
    for article in articles:
        try:
            from urllib.parse import urlparse
            domain = urlparse(article.url).netloc
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
        except:
            continue
    
    sorted_domains = sorted(domain_counts.items(), key=lambda x: x[1], reverse=True)[:limit]
    
    return [{"domain": domain, "count": count} for domain, count in sorted_domains]