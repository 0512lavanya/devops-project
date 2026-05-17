import pytest
from app import create_app, db
from app.models import Donor

@pytest.fixture
def app():
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

def test_health_check(client):
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json == {"status": "healthy"}

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'LifeStream' in response.data

def test_login_redirect(client):
    # Unauthenticated user trying to access dashboard should be redirected to login
    response = client.get('/dashboard')
    assert response.status_code == 302
    assert '/login' in response.headers.get('Location', '')
