from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db, login
import json

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(256))
    role = db.Column(db.String(20), default='patient') # 'patient' or 'admin'
    diagnoses = db.relationship('Diagnosis', backref='patient', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

class Symptom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255))
    category = db.Column(db.String(50)) # e.g., 'General', 'Malaria', 'Typhoid'

    def __repr__(self):
        return f'<Symptom {self.name}>'

class Rule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rule_name = db.Column(db.String(100), unique=True, nullable=False)
    # conditions will store JSON string: {"symptom_ids": [1, 2, 3], "min_count": 3}
    conditions = db.Column(db.Text, nullable=False)
    conclusion = db.Column(db.String(100), nullable=False)
    priority = db.Column(db.Integer, default=0)

    def get_conditions(self):
        return json.loads(self.conditions)

    def set_conditions(self, conditions_dict):
        self.conditions = json.dumps(conditions_dict)

    def __repr__(self):
        return f'<Rule {self.rule_name}>'

class Diagnosis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    result = db.Column(db.String(100), nullable=False)
    symptoms_present = db.Column(db.Text) # JSON string of symptom IDs
    explanation = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    def get_symptoms(self):
        return json.loads(self.symptoms_present) if self.symptoms_present else []

    def __repr__(self):
        return f'<Diagnosis {self.result} for User {self.user_id}>'

class Recommendation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    diagnosis_result = db.Column(db.String(100), unique=True, nullable=False)
    advice_text = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f'<Recommendation for {self.diagnosis_result}>'
