import pytest
from app import create_app, db
from app.models import User, Symptom, Rule, Diagnosis, Recommendation
from app.admin.routes import admin_required

@pytest.fixture
def app():
    app = create_app()
    app.config.update({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "WTF_CSRF_ENABLED": False
    })

    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db.session

def test_admin_required_decorator(app, client):
    # Create a regular user
    user = User(username='patient', email='patient@example.com')
    user.set_password('password')
    db.session.add(user)
    db.session.commit()

    with client.session_transaction() as sess:
        from flask_login import login_user
        login_user(user, sess)

    # Try to access admin dashboard
    response = client.get('/admin/dashboard')
    assert response.status_code == 403

    # Create an admin user
    admin = User(username='admin', email='admin@example.com', role='admin')
    admin.set_password('adminpassword')
    db.session.add(admin)
    db.session.commit()

    # Log in as admin
    with client.session_transaction() as sess:
        from flask_login import login_user
        login_user(admin, sess)

    # Access admin dashboard
    response = client.get('/admin/dashboard')
    assert response.status_code == 200
