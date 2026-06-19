from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import login_required, current_user
from functools import wraps

from app import db
from app.admin import bp
from app.models import Symptom, Rule, User, Diagnosis, Recommendation
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SelectMultipleField, SubmitField
from wtforms.validators import DataRequired, Length

def admin_required(f):
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

class RuleForm(FlaskForm):

    rule_name = StringField('Rule Name', validators=[DataRequired(), Length(max=100)])
    conclusion = StringField('Conclusion', validators=[DataRequired(), Length(max=100)])
    min_count = IntegerField('Minimum Matching Symptoms', default=1, validators=[DataRequired()])
    symptom_ids = SelectMultipleField('Select Symptoms', coerce=int, validators=[DataRequired()])
    priority = IntegerField('Priority', default=0)
    submit = SubmitField('Save Rule')

@bp.route('/dashboard')
@admin_required
def dashboard():
    symptoms_count = Symptom.query.count()
    rules_count = Rule.query.count()
    diagnoses_count = Diagnosis.query.count()
    users_count = User.query.count()
    return render_template('admin/dashboard.html', 
                           symptoms_count=symptoms_count,
                           rules_count=rules_count,
                           diagnoses_count=diagnoses_count,
                           users_count=users_count,
                           title='Admin Dashboard')

@bp.route('/symptoms', methods=['GET', 'POST'])
@admin_required
def manage_symptoms():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        category = request.form.get('category')
        symptom = Symptom(name=name, description=description, category=category)
        db.session.add(symptom)
        db.session.commit()
        flash('Symptom added successfully.')
        return redirect(url_for('admin.manage_symptoms'))
    symptoms = Symptom.query.all()
    return render_template('admin/symptoms.html', symptoms=symptoms, title='Manage Symptoms')

@bp.route('/rules', methods=['GET', 'POST'])
@admin_required
def manage_rules():
    form = RuleForm()
    symptoms = Symptom.query.all()
    
    # For the multi-select field
    form.symptom_ids.choices = [(s.id, s.name) for s in symptoms]

    if form.validate_on_submit():
        conditions = {
            "symptom_ids": form.symptom_ids.data,
            "min_count": form.min_count.data
        }
        rule = Rule(rule_name=form.rule_name.data, conclusion=form.conclusion.data)
        rule.set_conditions(conditions)
        db.session.add(rule)
        db.session.commit()
        flash('Rule added successfully.')
        return redirect(url_for('admin.manage_rules'))
    
    rules = Rule.query.all()
    return render_template('admin/rules.html', rules=rules, form=form, symptoms=symptoms, title='Manage Rules')

@bp.route('/recommendations', methods=['GET', 'POST'])
@admin_required
def manage_recommendations():
    if request.method == 'POST':
        diagnosis_result = request.form.get('diagnosis_result')
        advice_text = request.form.get('advice_text')
        rec = Recommendation.query.filter_by(diagnosis_result=diagnosis_result).first()
        if rec:
            rec.advice_text = advice_text
        else:
            rec = Recommendation(diagnosis_result=diagnosis_result, advice_text=advice_text)
            db.session.add(rec)
        db.session.commit()
        flash('Recommendation updated.')
        return redirect(url_for('admin.manage_recommendations'))
    recs = Recommendation.query.all()
    return render_template('admin/recommendations.html', recs=recs, title='Manage Recommendations')
