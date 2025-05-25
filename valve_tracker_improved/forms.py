from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, SelectField, DateField, FileField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, Optional
from models import User
from datetime import datetime

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[('technician', 'Technician'), ('admin', 'Administrator')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
            
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user is not None:
            raise ValidationError('Please use a different email address.')

class PasswordResetForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    new_password2 = PasswordField('Confirm New Password', validators=[DataRequired(), EqualTo('new_password')])
    submit = SubmitField('Update Password')

class SpecimenForm(FlaskForm):
    valve_id = StringField('Valve ID', validators=[DataRequired(), Length(max=64)])
    name = StringField('Name', validators=[DataRequired(), Length(max=128)])
    type = StringField('Type', validators=[DataRequired(), Length(max=64)])
    status = SelectField('Status', choices=[
        ('Received', 'Received'),
        ('In Testing', 'In Testing'),
        ('Passed', 'Passed'),
        ('Failed', 'Failed'),
        ('On Hold', 'On Hold')
    ])
    notes = TextAreaField('Notes', validators=[Optional(), Length(max=1000)])
    submit = SubmitField('Save')

class TestForm(FlaskForm):
    test_type = SelectField('Test Type', choices=[
        ('Durability', 'Durability Test'),
        ('Pressure', 'Pressure Test'),
        ('Flow', 'Flow Test'),
        ('Fatigue', 'Fatigue Test'),
        ('Biocompatibility', 'Biocompatibility Test'),
        ('Other', 'Other Test')
    ])
    description = TextAreaField('Description', validators=[Optional(), Length(max=500)])
    due_date = DateField('Due Date', validators=[Optional()], format='%Y-%m-%d')
    submit = SubmitField('Assign Test')

class SearchForm(FlaskForm):
    search = StringField('Search', validators=[Optional()])
    status = SelectField('Status', choices=[
        ('All', 'All Statuses'),
        ('Received', 'Received'),
        ('In Testing', 'In Testing'),
        ('Passed', 'Passed'),
        ('Failed', 'Failed'),
        ('On Hold', 'On Hold')
    ])
    type = SelectField('Type', choices=[('All', 'All Types')])
    
    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        # The type choices will be dynamically populated in the route
