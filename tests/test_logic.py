import pytest
from app import create_app, db
from app.models import User, Symptom, Rule, Diagnosis, Recommendation
from app.services.inference_engine import InferenceEngine

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

def test_inference_engine_match(db_session):
    # Set up symptoms
    s1 = Symptom(name='Fever', category='General')
    s2 = Symptom(name='Chills', category='General')
    db_session.add_all([s1, s2])
    db_session.commit()

    # Set up rule
    rule = Rule(rule_name='Malaria Rule', conclusion='Malaria')
    rule.set_conditions({'symptom_ids': [s1.id, s2.id], 'min_count': 2})
    db_session.add(rule)
    db_session.commit()

    # Test match
    engine = InferenceEngine([s1.id, s2.id])
    conclusion, explanation, matching_symptoms = engine.evaluate()

    assert conclusion == 'Malaria'
    assert s1.name in explanation
    assert s2.name in explanation
    assert set(matching_symptoms) == {s1.id, s2.id}

def test_inference_engine_no_match(db_session):
    # Set up symptom
    s1 = Symptom(name='Fever', category='General')
    db_session.add(s1)
    db_session.commit()

    # Set up rule requiring 2 symptoms
    rule = Rule(rule_name='Malaria Rule', conclusion='Malaria')
    rule.set_conditions({'symptom_ids': [s1.id, 999], 'min_count': 2})
    db_session.add(rule)
    db_session.commit()

    # Test no match
    engine = InferenceEngine([s1.id])
    conclusion, explanation, matching_symptoms = engine.evaluate()

    assert conclusion == 'Unknown'
    assert 'No specific diagnosis' in explanation
    assert matching_symptoms == []

def test_get_advice(db_session):
    rec = Recommendation(diagnosis_result='Malaria', advice_text='Drink water and rest.')
    db_session.add(rec)
    db_session.commit()

    advice = InferenceEngine.get_advice('Malaria')
    assert advice == 'Drink water and rest.'

    advice_none = InferenceEngine.get_advice('Unknown')
    assert advice_none == 'Please visit the nearest hospital for a proper medical examination.'
