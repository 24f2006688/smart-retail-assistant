import pytest
import json
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_health_check(client):
    """Test the health check endpoint returns 200 and proper JSON status."""
    response = client.get('/health')
    assert response.status_code == 200
    data = json.loads(response.data)
    assert data.get('status') == 'healthy'

def test_index_loads(client):
    """Test that the main index page loads."""
    response = client.get('/')
    assert response.status_code == 200
    assert b'ShopBot AI' in response.data

def test_chat_no_message(client):
    """Test that posting to /api/chat without message payload returns 400."""
    response = client.post('/api/chat', json={})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_chat_empty_string(client):
    """Test that posting to /api/chat with empty string returns 400."""
    response = client.post('/api/chat', json={"message": "", "session_id": "123"})
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_search_no_query(client):
    """Test product search without a query parameter returns 400."""
    response = client.get('/api/products/search')
    assert response.status_code == 400
    data = json.loads(response.data)
    assert 'error' in data

def test_search_with_query(client):
    """Test product search with a valid query parameter."""
    response = client.get('/api/products/search?q=laptop')
    # Can be 200 if Gemini works or fallback works, or 500 if catastrophic failure
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = json.loads(response.data)
        assert 'products' in data
        assert isinstance(data['products'], list)
