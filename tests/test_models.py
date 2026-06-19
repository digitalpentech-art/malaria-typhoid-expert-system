import pytest
from app import create_app, db
from app.models import User, Symptom, Rule, Diagnosis, Recommendation

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
def runner(app):
    return app.test_cli_runner()

@pytest.fixture
def db_session(app):
    with app.app_context():
        yield db.session

def test_user_creation(db_session):
    user = User(username='testuser', email='test@example.com')
    user.set_password('testpassword')
    db_session.add(user)
    db_session.commit()

    retrieved_user = User.query.filter_by(username='testuser').first()
    assert retrieved_user is not None
    assert retrieved_user.email == 'test@example.com'
    assert retrieved_user.check_password('testpassword')
    assert not retrieved_user.check_password('wrongpassword')

def test_symptom_creation(db_session):
    symptom = Symptom(name='Fever', description='High body temperature', category='General')
    db_session.add(symptom)
    db_session.commit()

    retrieved_symptom = Symptom.query.filter_by(name='Fever').first()
    assert retrieved_symptom is not None
    assert retrieved_symptom.category == 'General'

def test_rule_creation(db_session):
    rule = Rule(rule_name='Malaria Rule', conclusion='Malaria')
    rule.set_conditions({'symptom_ids': [1, 2], 'min_count': 2})
    db_session.add(rule)
    db_session.commit()

    retrieved_rule = Rule.query.filter_by(rule_name='Malaria Rule').first()
    assert retrieved_rule is not None
    assert retrieved_rule.get_conditions()['min_count'] == 2

def test_diagnosis_creation(db_session):
    user = User(username='patient', email='patient@example.com')
    user.set_password('password')
    db_session.add(user)
    db_session.commit()

    diagnosis = Diagnosis(user_id=user.id, result='Malaria', symptoms_present='[1, 2]', explanation='High fever and chills')
    db_session.add(diagnosis)
    db_session.commit()

    retrieved_diagnosis = Diagnosis.query.filter_by(user_id=user.id).first()
    assert retrieved_diagnosis is not None
    assert retrieved_diagnosis.result == 'Malaria'
    assert retrieved_diagnosis.get_symptoms() == [1, 2]
