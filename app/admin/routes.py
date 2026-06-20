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

@bp.route('/symptoms/delete/<int:symptom_id>', methods=['POST'])
@admin_required
def delete_symptom(symptom_id):
    symptom = db.session.get(Symptom, symptom_id)
    if not symptom:
        abort(404)
    
    # Check if symptom is used in any rule conditions
    rules = Rule.query.all()
    is_used = False
    using_rules = []
    for rule in rules:
        try:
            conds = rule.get_conditions()
            if symptom_id in conds.get('symptom_ids', []):
                is_used = True
                using_rules.append(rule.rule_name)
        except Exception:
            pass
            
    if is_used:
        flash(f'Cannot delete symptom "{symptom.name}" because it is currently used in the following rules: {", ".join(using_rules)}. Please modify or delete those rules first.', 'danger')
    else:
        db.session.delete(symptom)
        db.session.commit()
        flash(f'Symptom "{symptom.name}" has been deleted successfully.', 'success')
        
    return redirect(url_for('admin.manage_symptoms'))

@bp.route('/rules/delete/<int:rule_id>', methods=['POST'])
@admin_required
def delete_rule(rule_id):
    rule = db.session.get(Rule, rule_id)
    if not rule:
        abort(404)
    
    rule_name = rule.rule_name
    db.session.delete(rule)
    db.session.commit()
    flash(f'Rule "{rule_name}" has been deleted successfully.', 'success')
    return redirect(url_for('admin.manage_rules'))

@bp.route('/rules/edit/<int:rule_id>', methods=['GET', 'POST'])
@admin_required
def edit_rule(rule_id):
    rule = db.session.get(Rule, rule_id)
    if not rule:
        abort(404)
    
    form = RuleForm()
    symptoms = Symptom.query.all()
    form.symptom_ids.choices = [(s.id, s.name) for s in symptoms]

    if form.validate_on_submit():
        conditions = {
            "symptom_ids": form.symptom_ids.data,
            "min_count": form.min_count.data
        }
        rule.rule_name = form.rule_name.data
        rule.conclusion = form.conclusion.data
        rule.priority = form.priority.data
        rule.set_conditions(conditions)
        db.session.commit()
        flash('Rule updated successfully.', 'success')
        return redirect(url_for('admin.manage_rules'))

    # Pre-populate form
    form.rule_name.data = rule.rule_name
    form.conclusion.data = rule.conclusion
    form.priority.data = rule.priority
    form.symptom_ids.data = rule.get_conditions().get('symptom_ids', [])

    return render_template('admin/edit_rule.html', form=form, rule=rule, title='Edit Rule')

@bp.route('/symptoms/edit/<int:symptom_id>', methods=['GET', 'POST'])
@admin_required
def edit_symptom(symptom_id):
    symptom = db.session.get(Symptom, symptom_id)
    if not symptom:
        abort(404)

    if request.method == 'POST':
        symptom.name = request.form.get('name')
        symptom.description = request.form.get('description')
        symptom.category = request.form.get('category')
        db.session.commit()
        flash('Symptom updated successfully.', 'success')
        return redirect(url_for('admin.manage_symptoms'))

    return render_template('admin/edit_symptom.html', symptom=symptom, title='Edit Symptom')

@bp.route('/recommendations/edit/<int:rec_id>', methods=['GET', 'POST'])
@admin_required
def edit_recommendation(rec_id):
    rec = db.session.get(Recommendation, rec_id)
    if not rec:
        abort(404)

    if request.method == 'POST':
        rec.advice_text = request.form.get('advice_text')
        db.session.commit()
        flash('Recommendation updated successfully.', 'success')
        return redirect(url_for('admin.manage_recommendations'))

    return render_template('admin/edit_recommendation.html', rec=rec, title='Edit Recommendation')
