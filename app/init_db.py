from app import db
from app.models import User, Symptom, Rule, Recommendation

def initialize_data():
    """Seeds the database with initial data if empty."""
    
    # 1. Seed Users
    if not User.query.filter_by(username='admin').first():
        admin_user = User(username='admin', email='admin@example.com', role='admin')
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        
        patient_user = User(username='patient', email='patient@example.com', role='patient')
        patient_user.set_password('patient123')
        db.session.add(patient_user)
        db.session.commit()

    # 2. Seed Symptoms
    if Symptom.query.count() == 0:
        symptoms_data = [
            ('Fever', 'High body temperature', 'General'),
            ('Chills', 'Feeling cold and shivering', 'Malaria'),
            ('Sweating', 'Excessive perspiration', 'Malaria'),
            ('Headache', 'Pain in the head', 'Malaria'),
            ('Muscle Pain', 'Aching muscles', 'Malaria'),
            ('Abdominal Pain', 'Pain in the stomach area', 'Typhoid'),
            ('Loss of Appetite', 'Reduced desire to eat', 'Typhoid'),
            ('Weakness', 'Feeling tired or lacking strength', 'Typhoid'),
            ('Diarrhea', 'Frequent loose bowel movements', 'Typhoid'),
            ('Nausea', 'Feeling of wanting to vomit', 'General'),
            ('Vomiting', 'Act of vomiting', 'General'),
            ('Fatigue', 'Extreme tiredness', 'General'),
            ('Constipation', 'Difficulty in bowel movements', 'General'),
            ('Joint Pain', 'Pain in the joints', 'General'),
        ]
        
        for name, desc, cat in symptoms_data:
            s = Symptom(name=name, description=desc, category=cat)
            db.session.add(s)
        db.session.commit()

        # Fetch symptom IDs for rules
        s_map = {s.name: s.id for s in Symptom.query.all()}

        # 3. Seed Rules
        malaria_symptoms = [s_map['Fever'], s_map['Chills'], s_map['Sweating'], s_map['Headache'], s_map['Muscle Pain']]
        rule1 = Rule(rule_name='Malaria Diagnosis Rule', conclusion='Malaria', priority=1)
        rule1.set_conditions({'symptom_ids': malaria_symptoms, 'min_count': 3})
        db.session.add(rule1)

        typhoid_symptoms = [s_map['Fever'], s_map['Abdominal Pain'], s_map['Loss of Appetite'], s_map['Weakness'], s_map['Diarrhea']]
        rule2 = Rule(rule_name='Typhoid Diagnosis Rule', conclusion='Typhoid', priority=1)
        rule2.set_conditions({'symptom_ids': typhoid_symptoms, 'min_count': 3})
        db.session.add(rule2)

        coinfection_symptoms = list(set(malaria_symptoms + typhoid_symptoms))
        rule3 = Rule(rule_name='Co-infection Diagnosis Rule', conclusion='Co-infection', priority=2)
        rule3.set_conditions({'symptom_ids': coinfection_symptoms, 'min_count': 6})
        db.session.add(rule3)
        db.session.commit()

        # 4. Seed Recommendations
        rec1 = Recommendation(diagnosis_result='Malaria', advice_text='Rest, stay hydrated, and consult a doctor immediately for anti-malarial medication.')
        db.session.add(rec1)
        rec2 = Recommendation(diagnosis_result='Typhoid', advice_text='Maintain good hygiene, drink clean water, and consult a doctor for appropriate antibiotics.')
        db.session.add(rec2)
        rec3 = Recommendation(diagnosis_result='Co-infection', advice_text='Urgent medical attention is required. You may need multiple types of treatment for both Malaria and Typhoid.')
        db.session.add(rec3)
        rec4 = Recommendation(diagnosis_result='Unknown', advice_text='We could not determine a specific diagnosis. Please consult a medical professional for accurate testing.')
        db.session.add(rec4)
        db.session.commit()
