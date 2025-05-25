import os
from flask import Flask, render_template, request, redirect, url_for, flash, send_from_directory, jsonify, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.urls import url_parse
from datetime import datetime
import mimetypes
import uuid
import pandas as pd
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from models import db, init_db, User, Specimen, Test, Result, ActionLog
from forms import LoginForm, RegistrationForm, SpecimenForm, TestForm, SearchForm, PasswordResetForm

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY') or 'dev-key-for-valve-tracker'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///valve_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'png', 'jpg', 'jpeg', 'gif', 'csv', 'xlsx'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize database
init_db(app)

# Initialize login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Helper functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def get_file_type(filename):
    ext = filename.rsplit('.', 1)[1].lower()
    if ext in ['pdf']:
        return 'PDF'
    elif ext in ['png', 'jpg', 'jpeg', 'gif']:
        return 'Image'
    elif ext in ['csv', 'xlsx']:
        return 'Data'
    return 'Other'

def log_action(action_type, target_type, target_id, details=None):
    if current_user.is_authenticated:
        log = ActionLog(
            user_id=current_user.id,
            action_type=action_type,
            target_type=target_type,
            target_id=target_id,
            details=details,
            ip_address=request.remote_addr
        )
        db.session.add(log)
        db.session.commit()

# Routes
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/dashboard')
@login_required
def dashboard():
    # Get counts for dashboard stats
    total_specimens = Specimen.query.count()
    specimens_in_testing = Specimen.query.filter_by(status='In Testing').count()
    specimens_passed = Specimen.query.filter_by(status='Passed').count()
    specimens_failed = Specimen.query.filter_by(status='Failed').count()
    
    # Get recent specimens
    recent_specimens = Specimen.query.order_by(Specimen.created_at.desc()).limit(5).all()
    
    # Get recent activity
    recent_activity = ActionLog.query.order_by(ActionLog.timestamp.desc()).limit(10).all()
    
    return render_template('dashboard.html', 
                          total_specimens=total_specimens,
                          specimens_in_testing=specimens_in_testing,
                          specimens_passed=specimens_passed,
                          specimens_failed=specimens_failed,
                          recent_specimens=recent_specimens,
                          recent_activity=recent_activity)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'danger')
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        log_action('Login', 'User', user.id, 'User logged in')
        
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('dashboard')
        
        flash(f'Welcome, {user.username}!', 'success')
        return redirect(next_page)
    
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    log_action('Logout', 'User', current_user.id, 'User logged out')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if not current_user.is_authenticated or not current_user.is_admin():
        abort(403)
        
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        
        log_action('Create', 'User', user.id, f'Created new user: {user.username}')
        flash(f'User {form.username.data} has been registered!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('register.html', form=form)

@app.route('/specimens')
@login_required
def specimen_list():
    search_form = SearchForm(request.args)
    
    # Base query
    query = Specimen.query
    
    # Apply filters if provided
    if search_form.search.data:
        search_term = f"%{search_form.search.data}%"
        query = query.filter(
            (Specimen.valve_id.like(search_term)) |
            (Specimen.name.like(search_term)) |
            (Specimen.type.like(search_term))
        )
    
    if search_form.status.data and search_form.status.data != 'All':
        query = query.filter_by(status=search_form.status.data)
        
    if search_form.type.data and search_form.type.data != 'All':
        query = query.filter_by(type=search_form.type.data)
    
    # Sort
    sort_by = request.args.get('sort_by', 'created_at')
    sort_dir = request.args.get('sort_dir', 'desc')
    
    if sort_dir == 'desc':
        query = query.order_by(getattr(Specimen, sort_by).desc())
    else:
        query = query.order_by(getattr(Specimen, sort_by).asc())
    
    # Get unique types for filter dropdown
    types = [t[0] for t in db.session.query(Specimen.type).distinct()]
    
    # Execute query
    specimens = query.all()
    
    return render_template('specimens.html', 
                          specimens=specimens, 
                          search_form=search_form,
                          types=types,
                          sort_by=sort_by,
                          sort_dir=sort_dir)

@app.route('/specimens/add', methods=['GET', 'POST'])
@login_required
def specimen_add():
    form = SpecimenForm()
    
    if form.validate_on_submit():
        specimen = Specimen(
            valve_id=form.valve_id.data,
            name=form.name.data,
            type=form.type.data,
            status=form.status.data,
            notes=form.notes.data
        )
        db.session.add(specimen)
        db.session.commit()
        
        log_action('Create', 'Specimen', specimen.id, f'Created new specimen: {specimen.valve_id}')
        flash(f'Specimen {specimen.valve_id} has been added!', 'success')
        return redirect(url_for('specimen_list'))
    
    return render_template('specimen_add.html', form=form)

@app.route('/specimens/<int:id>')
@login_required
def specimen_detail(id):
    specimen = Specimen.query.get_or_404(id)
    results = Result.query.filter_by(specimen_id=id).order_by(Result.uploaded_at.desc()).all()
    tests = Test.query.filter_by(specimen_id=id).order_by(Test.assigned_date.desc()).all()
    
    return render_template('specimen_detail.html', 
                          specimen=specimen, 
                          results=results,
                          tests=tests)

@app.route('/specimens/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def specimen_edit(id):
    specimen = Specimen.query.get_or_404(id)
    form = SpecimenForm(obj=specimen)
    
    if form.validate_on_submit():
        old_status = specimen.status
        
        specimen.valve_id = form.valve_id.data
        specimen.name = form.name.data
        specimen.type = form.type.data
        specimen.status = form.status.data
        specimen.notes = form.notes.data
        specimen.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        details = f'Updated specimen: {specimen.valve_id}'
        if old_status != specimen.status:
            details += f' (Status changed from {old_status} to {specimen.status})'
            
        log_action('Update', 'Specimen', specimen.id, details)
        flash(f'Specimen {specimen.valve_id} has been updated!', 'success')
        return redirect(url_for('specimen_detail', id=specimen.id))
    
    return render_template('specimen_edit.html', form=form, specimen=specimen)

@app.route('/specimens/<int:id>/delete', methods=['POST'])
@login_required
def specimen_delete(id):
    if not current_user.is_admin():
        flash('Only administrators can delete specimens.', 'danger')
        return redirect(url_for('specimen_list'))
        
    specimen = Specimen.query.get_or_404(id)
    valve_id = specimen.valve_id
    
    # Delete associated files
    for result in specimen.results:
        try:
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], result.file))
        except:
            pass
    
    db.session.delete(specimen)
    db.session.commit()
    
    log_action('Delete', 'Specimen', id, f'Deleted specimen: {valve_id}')
    flash(f'Specimen {valve_id} has been deleted!', 'success')
    return redirect(url_for('specimen_list'))

@app.route('/specimens/<int:id>/add_test', methods=['GET', 'POST'])
@login_required
def add_test(id):
    specimen = Specimen.query.get_or_404(id)
    form = TestForm()
    
    if form.validate_on_submit():
        test = Test(
            specimen_id=specimen.id,
            test_type=form.test_type.data,
            description=form.description.data,
            due_date=form.due_date.data,
            status='Pending'
        )
        db.session.add(test)
        
        # Update specimen status if it's still in 'Received' state
        if specimen.status == 'Received':
            specimen.status = 'In Testing'
            
        db.session.commit()
        
        log_action('Create', 'Test', test.id, f'Added test to specimen {specimen.valve_id}: {test.test_type}')
        flash(f'Test has been assigned to {specimen.valve_id}!', 'success')
        return redirect(url_for('specimen_detail', id=specimen.id))
    
    return render_template('test_add.html', form=form, specimen=specimen)

@app.route('/tests/<int:id>/update_status', methods=['POST'])
@login_required
def update_test_status(id):
    test = Test.query.get_or_404(id)
    new_status = request.form.get('status')
    
    if new_status in ['Pending', 'In Progress', 'Completed', 'Cancelled']:
        old_status = test.status
        test.status = new_status
        db.session.commit()
        
        log_action('Update', 'Test', test.id, f'Updated test status from {old_status} to {new_status}')
        flash(f'Test status updated to {new_status}!', 'success')
    
    return redirect(url_for('specimen_detail', id=test.specimen_id))

@app.route('/results/upload/<int:specimen_id>', methods=['POST'])
@login_required
def upload_result(specimen_id):
    specimen = Specimen.query.get_or_404(specimen_id)
    test_id = request.form.get('test_id')
    notes = request.form.get('notes', '')
    
    if 'result_file' not in request.files:
        flash('No file selected', 'danger')
        return redirect(url_for('specimen_detail', id=specimen_id))
    
    file = request.files['result_file']
    
    if file.filename == '':
        flash('No file selected', 'danger')
        return redirect(url_for('specimen_detail', id=specimen_id))
    
    if not allowed_file(file.filename):
        flash('File type not allowed. Allowed types: PDF, images, CSV, Excel', 'danger')
        return redirect(url_for('specimen_detail', id=specimen_id))
    
    # Generate unique filename
    filename = secure_filename(file.filename)
    file_ext = filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{file_ext}"
    
    # Save file
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(filepath)
    
    # Create result record
    result = Result(
        specimen_id=specimen_id,
        test_id=test_id if test_id else None,
        file=unique_filename,
        file_type=get_file_type(filename),
        notes=notes,
        user_id=current_user.id
    )
    db.session.add(result)
    
    # Update test status if applicable
    if test_id:
        test = Test.query.get(test_id)
        if test and test.status != 'Completed':
            test.status = 'Completed'
    
    db.session.commit()
    
    log_action('Upload', 'Result', result.id, f'Uploaded {result.file_type} file for specimen {specimen.valve_id}')
    flash('Result file uploaded successfully!', 'success')
    return redirect(url_for('specimen_detail', id=specimen_id))

@app.route('/uploads/<filename>')
@login_required
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/results/<int:id>/delete', methods=['POST'])
@login_required
def delete_result(id):
    result = Result.query.get_or_404(id)
    specimen_id = result.specimen_id
    
    # Delete file
    try:
        os.remove(os.path.join(app.config['UPLOAD_FOLDER'], result.file))
    except:
        pass
    
    db.session.delete(result)
    db.session.commit()
    
    log_action('Delete', 'Result', id, f'Deleted result file for specimen {result.specimen_id}')
    flash('Result file deleted successfully!', 'success')
    return redirect(url_for('specimen_detail', id=specimen_id))

@app.route('/reports')
@login_required
def reports():
    return render_template('reports.html')

@app.route('/reports/generate', methods=['POST'])
@login_required
def generate_report():
    report_type = request.form.get('report_type')
    date_from = request.form.get('date_from')
    date_to = request.form.get('date_to')
    format_type = request.form.get('format', 'csv')
    
    # Base query
    query = Specimen.query
    
    # Apply date filters if provided
    if date_from:
        query = query.filter(Specimen.created_at >= date_from)
    if date_to:
        query = query.filter(Specimen.created_at <= date_to)
    
    # Different report types
    if report_type == 'status_summary':
        # Status summary report
        results = db.session.query(
            Specimen.status, 
            db.func.count(Specimen.id)
        ).group_by(Specimen.status).all()
        
        data = [['Status', 'Count']]
        for status, count in results:
            data.append([status, count])
            
        filename = f"status_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    elif report_type == 'type_summary':
        # Type summary report
        results = db.session.query(
            Specimen.type, 
            db.func.count(Specimen.id)
        ).group_by(Specimen.type).all()
        
        data = [['Valve Type', 'Count']]
        for type_, count in results:
            data.append([type_, count])
            
        filename = f"type_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    elif report_type == 'detailed':
        # Detailed specimen report
        specimens = query.all()
        
        data = [['ID', 'Valve ID', 'Name', 'Type', 'Status', 'Created', 'Updated', 'Notes']]
        for s in specimens:
            data.append([
                s.id,
                s.valve_id,
                s.name,
                s.type,
                s.status,
                s.created_at.strftime('%Y-%m-%d %H:%M'),
                s.updated_at.strftime('%Y-%m-%d %H:%M'),
                s.notes or ''
            ])
            
        filename = f"detailed_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    else:
        flash('Invalid report type', 'danger')
        return redirect(url_for('reports'))
    
    # Generate report in requested format
    if format_type == 'csv':
        # CSV format
        output = BytesIO()
        df = pd.DataFrame(data[1:], columns=data[0])
        df.to_csv(output, index=False)
        output.seek(0)
        
        log_action('Generate', 'Report', 0, f'Generated {report_type} report in CSV format')
        
        return send_file(
            output,
            as_attachment=True,
            download_name=f"{filename}.csv",
            mimetype='text/csv'
        )
        
    elif format_type == 'pdf':
        # PDF format
        output = BytesIO()
        doc = SimpleDocTemplate(output, pagesize=letter)
        elements = []
        
        # Add title
        styles = getSampleStyleSheet()
        title = f"Heart Valve Tracker - {report_type.replace('_', ' ').title()} Report"
        elements.append(Paragraph(title, styles['Title']))
        
        # Add date range if provided
        if date_from or date_to:
            date_range = f"Period: {date_from or 'All'} to {date_to or 'Present'}"
            elements.append(Paragraph(date_range, styles['Normal']))
            elements.append(Paragraph(" ", styles['Normal']))  # Spacer
        
        # Create table
        table = Table(data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        
        elements.append(table)
        
        # Add generation info
        generation_info = f"Generated by: {current_user.username} on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        elements.append(Paragraph(" ", styles['Normal']))  # Spacer
        elements.append(Paragraph(generation_info, styles['Normal']))
        
        # Build PDF
        doc.build(elements)
        output.seek(0)
        
        log_action('Generate', 'Report', 0, f'Generated {report_type} report in PDF format')
        
        return send_file(
            output,
            as_attachment=True,
            download_name=f"{filename}.pdf",
            mimetype='application/pdf'
        )
    
    flash('Invalid format type', 'danger')
    return redirect(url_for('reports'))

@app.route('/activity')
@login_required
def activity_log():
    if not current_user.is_admin():
        flash('Only administrators can view the activity log.', 'danger')
        return redirect(url_for('dashboard'))
        
    page = request.args.get('page', 1, type=int)
    logs = ActionLog.query.order_by(ActionLog.timestamp.desc()).paginate(
        page=page, per_page=50, error_out=False)
    
    return render_template('activity_log.html', logs=logs)

@app.route('/profile')
@login_required
def profile():
    # Get user's recent activity
    recent_activity = ActionLog.query.filter_by(user_id=current_user.id).order_by(
        ActionLog.timestamp.desc()).limit(10).all()
    
    # Get user's recent uploads
    recent_uploads = Result.query.filter_by(user_id=current_user.id).order_by(
        Result.uploaded_at.desc()).limit(5).all()
    
    return render_template('profile.html', 
                          user=current_user,
                          recent_activity=recent_activity,
                          recent_uploads=recent_uploads)

@app.route('/profile/password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = PasswordResetForm()
    
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash('Current password is incorrect', 'danger')
            return redirect(url_for('change_password'))
            
        current_user.set_password(form.new_password.data)
        db.session.commit()
        
        log_action('Update', 'User', current_user.id, 'Changed password')
        flash('Your password has been updated!', 'success')
        return redirect(url_for('profile'))
    
    return render_template('change_password.html', form=form)

@app.route('/users')
@login_required
def user_list():
    if not current_user.is_admin():
        flash('Only administrators can view the user list.', 'danger')
        return redirect(url_for('dashboard'))
        
    users = User.query.all()
    return render_template('users.html', users=users)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# Helper function for send_file (used in report generation)
def send_file(bytes_io, as_attachment, download_name, mimetype):
    response = app.response_class(
        bytes_io.getvalue(),
        mimetype=mimetype
    )
    if as_attachment:
        response.headers.set('Content-Disposition', 'attachment', filename=download_name)
    return response

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
