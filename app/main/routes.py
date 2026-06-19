from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from app import db
from app.main import bp
from app.models import Symptom, Diagnosis, User
from app.services.inference_engine import InferenceEngine
import json
from flask_wtf import FlaskForm
from wtforms import SubmitField
from wtforms.validators import ValidationError

class SymptomCheckForm(FlaskForm):
    submit = SubmitField('Analyze Symptoms')

@bp.route('/')
@bp.route('/index')
def index():
    return render_template('index.html', title='Home')

@bp.route('/symptom_checker', methods=['GET', 'POST'])
@login_required
def symptom_checker():
    form = SymptomCheckForm()
    if form.validate_on_submit():
        selected_symptom_ids = request.form.getlist('symptoms')
        if not selected_symptom_ids:
            flash('Please select at least one symptom.')
            return redirect(url_for('main.symptom_checker'))
        
        # Convert to integers
        selected_symptom_ids = [int(sid) for sid in selected_symptom_ids]
        
        # Run Inference Engine
        engine = InferenceEngine(selected_symptom_ids)
        result, explanation, matching_symptoms = engine.evaluate()
        advice = engine.get_advice(result)
        
        # Save diagnosis
        diagnosis = Diagnosis(
            user_id=current_user.id,
            result=result,
            symptoms_present=json.dumps(selected_symptom_ids),
            explanation=explanation
        )
        db.session.add(diagnosis)
        db.session.commit()
        
        return render_template('diagnosis_result.html', 
                               result=result, 
                               explanation=explanation, 
                               advice=advice, 
                               title='Diagnosis Result')
    
    symptoms = Symptom.query.all()
    return render_template('symptom_checker.html', form=form, symptoms=symptoms, title='Symptom Checker')

@bp.route('/history')
@login_required
def history():
    diagnoses = Diagnosis.query.filter_by(user_id=current_user.id).order_by(Diagnosis.timestamp.desc()).all()
    return render_template('history.html', diagnoses=diagnoses, title='My History')
