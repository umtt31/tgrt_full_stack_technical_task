import pytest
from fastapi.testclient import TestClient
from app.main import app
from tests.test_auth import override_get_db, setup_database
from unittest.mock import patch, MagicMock

client = TestClient(app)

def get_auth_token():
    # Register and login user
    client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    
    login_response = client.post(
        "/api/auth/token",
        data={
            "username": "testuser",
            "password": "testpassword"
        }
    )
    return login_response.json()["access_token"]

@patch('app.services.news_extractor.NewsExtractor.extract_content')
def test_extract_news_success(mock_extract, setup_database):
    token = get_auth_token()
    
    # Mock successful extraction
    mock_extract.return_value = {
        "title": "Test News Title",
        "content": "Test news content",
        "publish_date": None,
        "image_url": "https://example.com/image.jpg",
        "success": True
    }
    
    response = client.post(
        "/api/news/extract",
        json={"url": "https://example.com/news"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test News Title"
    assert data["url"] == "https://example.com/news"

@patch('app.services.news_extractor.NewsExtractor.extract_content')
def test_extract_news_failure(mock_extract, setup_database):
    token = get_auth_token()
    
    # Mock failed extraction
    mock_extract.return_value = {
        "error": "Failed to extract content",
        "success": False
    }
    
    response = client.post(
        "/api/news/extract",
        json={"url": "https://invalid-url"},
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 400

def test_extract_news_unauthorized(setup_database):
    response = client.post(
        "/api/news/extract",
        json={"url": "https://example.com/news"}
    )
    assert response.status_code == 401

def test_get_user_news(setup_database):
    token = get_auth_token()
    
    # Get empty news list
    response = client.get(
        "/api/news/",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    assert response.json() == []

@patch('app.services.news_extractor.NewsExtractor.extract_content')
def test_delete_news(mock_extract, setup_database):
    token = get_auth_token()
    
    # Mock successful extraction
    mock_extract.return_value = {
        "title": "Test News",
        "content": "Content",
        "publish_date": None,
        "image_url": None,
        "success": True
    }
    
    # Add news
    add_response = client.post(
        "/api/news/extract",
        json={"url": "https://example.com/news"},
        headers={"Authorization": f"Bearer {token}"}
    )
    news_id = add_response.json()["id"]
    
    # Delete news
    delete_response = client.delete(
        f"/api/news/{news_id}",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert delete_response.status_code == 200
    assert "deleted successfully" in delete_response.json()["message"]

def test_delete_nonexistent_news(setup_database):
    token = get_auth_token()
    
    response = client.delete(
        "/api/news/999",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 404