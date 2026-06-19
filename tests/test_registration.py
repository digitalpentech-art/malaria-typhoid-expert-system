import pytest
from app import create_app, db
from app.models import User
from flask_login import login_user

def test_registration_error(app, client):
    # Test registration with valid data
    response = client.post('/auth/register', data={
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'password123'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    user = User.query.filter_by(username='testuser').first()
    assert user is not None
