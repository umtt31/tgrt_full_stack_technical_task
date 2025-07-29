from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.api import auth, news, analytics
from app.database import create_tables
import os

app = FastAPI(title="News Content Extractor", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="/app/static"), name="static")

# Ensure database directory exists
os.makedirs("/app/data", exist_ok=True)

create_tables()

app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(news.router, prefix="/api/news", tags=["news"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])

@app.get("/")
async def read_root():
    return {"message": "News Content Extractor API"}