from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.String(20), nullable=False, default='technician')  # 'admin' or 'technician'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    actions = db.relationship('ActionLog', backref='user', lazy='dynamic')
    uploads = db.relationship('Result', backref='uploaded_by', lazy='dynamic')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        return self.role == 'admin'
    
    def __repr__(self):
        return f'<User {self.username}>'

class Specimen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    valve_id = db.Column(db.String(64), unique=True, nullable=False)
    name = db.Column(db.String(128), nullable=False)
    type = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(64), nullable=False, default='Received')
    notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    results = db.relationship('Result', backref='specimen', lazy='dynamic', cascade='all, delete-orphan')
    tests = db.relationship('Test', backref='specimen', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Specimen {self.valve_id}>'
    
    def get_status_color(self):
        status_colors = {
            'Received': 'secondary',
            'In Testing': 'warning',
            'Passed': 'success',
            'Failed': 'danger',
            'On Hold': 'info'
        }
        return status_colors.get(self.status, 'secondary')

class Test(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    specimen_id = db.Column(db.Integer, db.ForeignKey('specimen.id'), nullable=False)
    test_type = db.Column(db.String(64), nullable=False)
    description = db.Column(db.Text)
    assigned_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=True)
    status = db.Column(db.String(64), default='Pending')  # Pending, In Progress, Completed, Cancelled
    
    def __repr__(self):
        return f'<Test {self.test_type} for Specimen {self.specimen_id}>'

class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    specimen_id = db.Column(db.Integer, db.ForeignKey('specimen.id'), nullable=False)
    test_id = db.Column(db.Integer, db.ForeignKey('test.id'), nullable=True)
    file = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(64))  # PDF, Image, CSV, etc.
    notes = db.Column(db.Text)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    def __repr__(self):
        return f'<Result {self.id} for Specimen {self.specimen_id}>'

class ActionLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    action_type = db.Column(db.String(64), nullable=False)  # Create, Update, Delete, Upload, Login, etc.
    target_type = db.Column(db.String(64), nullable=False)  # Specimen, Test, Result, User, etc.
    target_id = db.Column(db.Integer)
    details = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    ip_address = db.Column(db.String(64))
    
    def __repr__(self):
        return f'<ActionLog {self.action_type} on {self.target_type} {self.target_id}>'

def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        
        # Create admin user if none exists
        if not User.query.filter_by(role='admin').first():
            admin = User(username='admin', email='admin@example.com', role='admin')
            admin.set_password('admin123')
            db.session.add(admin)
            
            # Create technician user if none exists
            tech = User(username='technician', email='tech@example.com', role='technician')
            tech.set_password('tech123')
            db.session.add(tech)
            
            db.session.commit()
