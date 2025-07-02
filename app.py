from flask import Flask, render_template, request, redirect, url_for, flash, session, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from email.mime.text import MIMEText
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from functools import wraps
import smtplib
import os
import sqlite3

def get_db_connection():
	conn = sqlite3.connect('database.db')
	conn.row_factory = sqlite3.Row  # So you can access data like job['judul']
	return conn

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///law_assist.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_PERMANENT'] = False  # Expire session on browser close

# Mail config (optional)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'afrialdosiagian@gmail.com'
app.config['MAIL_PASSWORD'] = 'xkbz bxjv ohfm zchl'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # e.g. 30 minutes
app.config['SESSION_PERMANENT'] = True  # Needed for timed expiry
app.secret_key = 'your_secret_key'  # Must be set for session to work!

db = SQLAlchemy(app)
mail = Mail(app)

# Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class LegalCase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    case = db.Column(db.String(50))
    date = db.Column(db.String(20))
    ktp = db.Column(db.String(50))
    email = db.Column(db.String(100))
    phone = db.Column(db.String(20))

# Routes
def block_page():
	with open("index.html") as f:
		return render_template_string(f.read())

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	email = request.form['email']
	password = request.form['password']
	user = User.query.filter_by(email=email).first()
	if user and check_password_hash(user.password, password):
		session['user_id'] = user.id
		session['is_admin'] = user.is_admin
		flash('Login successful!')
		return redirect(url_for('dashboard'))
	flash('Invalid credentials')
	return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
	if 'user_id' not in session:
		flash('Please log in first.')
		return redirect(url_for('index'))

	user = User.query.get(session['user_id'])
	user_cases = LegalCase.query.filter_by(email=user.email).all()
	return render_template('dashboard.html', user=user, user_cases=user_cases)

@app.route('/register')
def register():
	return render_template('register.html')

@app.route('/register', methods=['POST'])
def register_post():
	email = request.form['email']
	password = generate_password_hash(request.form['password'])
	user = User(email=email, password=password)
	db.session.add(user)
	db.session.commit()
	flash('Registration successful')
	return redirect(url_for('index'))

@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/news')
def news():
	return render_template('news.html')

@app.route('/peraturan')
def peraturan():
	return render_template('peraturan.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
	if request.method == 'POST':
		email = request.form['email']
		user = User.query.filter_by(email=email).first()
		if user:
			try:
				msg = Message('Password Reset Request', sender=app.config['MAIL_USERNAME'], recipients=[email])
				msg.body = f"Your password cannot be retrieved for security. Please contact admin or register again."
				mail.send(msg)
				flash('Reset instructions sent to your email.')
			except Exception as e:
				print("Mail send error:", e)
				flash('Error sending email.')
		else:
			flash('Email not found.')
	return render_template('forgot_password.html')

@app.route('/jobs')
def jobs():
	if not session.get('user_id'):
		flash("Please log in first.")
		return redirect(url_for('index'))

	user_id = session.get('user_id')
	user = User.query.get(user_id)
	jobs = LegalCase.query.filter_by(email=user.email).all()  # assuming jobs are matched by email

	return render_template('jobs.html', user=user, jobs=jobs)

@app.route('/verify_token', methods=['POST'])
def verify_token():
	token = request.form.get('token', '').strip()

	if not token:
		return redirect(url_for('jobs', error='empty_token'))

    # ✅ Replace this with your actual crew token
	valid_token = 'mycrew123'

	if token != valid_token:
		return redirect(url_for('jobs', error='invalid_token'))
	session['is_crew'] = True
	return redirect(url_for('jobs'))

@app.route('/crew_dashboard', methods=['GET', 'POST'])
def crew_dashboard():
	if not session.get('is_crew'):
		return redirect(url_for('jobs', error='unauthorized'))

	conn = get_db_connection()

	if request.method == 'POST':
		judul = request.form['judul']
		pasal = request.form['pasal']
		isi = request.form['isi']
		penjelasan = request.form['penjelasan']

		conn.execute('INSERT INTO jobs (judul, pasal, isi, penjelasan) VALUES (?, ?, ?, ?)',
			(judul, pasal, isi, penjelasan))
		conn.commit()

	jobs = conn.execute('SELECT * FROM jobs').fetchall()
	conn.close()

	return render_template('crew_dashboard.html', jobs=jobs)

def send_email(subject, recipient, body):
	sender_email = "youremail@gmail.com"
	sender_password = "yourpassword"

	msg = MIMEText(body)
	msg['Subject'] = subject
	msg['From'] = sender_email
	msg['To'] = recipient

	with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
		smtp.login(sender_email, sender_password)
		smtp.send_message(msg)

@app.route('/submit-case', methods=['POST'])
def submit_case():
	case = LegalCase(
		name=request.form['name'],
		case=request.form['case'],
		date=request.form['date'],
		ktp=request.form['ktp'],
		email=request.form['email'],
		phone=request.form['phone']
		)
	db.session.add(case)
	db.session.commit()

    # Send email to admin (optional)
	try:
		msg = Message('You Have Job', sender=app.config['MAIL_USERNAME'], recipients=['afrialdosiagian@gmail.com'])
		msg.body = f"New Case Submitted:\nName: {case.name}\nCase: {case.case}\nPhone: {case.phone}"
		mail.send(msg)
	except Exception as e:
		print("Email failed:", e)

	flash("Thanks, we'll clear your problem and fix it all.")
	return redirect(url_for('index'))

@app.route('/edit_job/<int:job_id>', methods=['GET', 'POST'])
def edit_job(job_id):
	conn = get_db_connection()
	job = conn.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()

	if request.method == 'POST':
		judul = request.form['judul']
		pasal = request.form['pasal']
		isi = request.form['isi']
		penjelasan = request.form['penjelasan']
		conn.execute('UPDATE jobs SET judul=?, pasal=?, isi=?, penjelasan=? WHERE id=?',
			(judul, pasal, isi, penjelasan, job_id))
		conn.commit()
		conn.close()
		flash("✅ Correction saved")
		return redirect(url_for('crew_dashboard'))

	return render_template('edit_job.html', job=job)

@app.route('/share_job/<int:job_id>', methods=['POST'])
def share_job(job_id):
	conn = get_db_connection()
	job = conn.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()
	conn.close()

    # send_email function you already use
	body = f"""
	📚 Judul: {job['judul']}
	📌 Pasal: {job['pasal']}
	📄 Isi: {job['isi']}
	🧾 Penjelasan: {job['penjelasan']}
	"""
	send_email("Crew Submission", "afrialdosiagian@gmail.com", body)
	flash("✅ Job shared via email")
	return redirect(url_for('crew_dashboard'))

@app.route('/admin')
def admin():
	if not session.get('is_admin'):
		flash('Unauthorized access')
		return redirect(url_for('index'))
	users = User.query.all()
	cases = LegalCase.query.all()
	return render_template('admin.html', users=users, cases=cases)

@app.route('/admin/delete-user/<int:user_id>')
def delete_user(user_id):
	if not session.get('is_admin'):
		flash('Unauthorized')
		return redirect(url_for('index'))
	user = User.query.get_or_404(user_id)
	db.session.delete(user)
	db.session.commit()
	flash('User deleted')
	return redirect(url_for('admin'))

@app.route('/admin/delete-case/<int:case_id>')
def delete_case(case_id):
	if not session.get('is_admin'):
		flash('Unauthorized')
		return redirect(url_for('index'))
	case = LegalCase.query.get_or_404(case_id)
	db.session.delete(case)
	db.session.commit()
	flash('Case deleted')
	return redirect(url_for('admin'))

@app.route('/admin/export-case/<int:case_id>')
def export_case(case_id):
	from fpdf import FPDF
	case = LegalCase.query.get_or_404(case_id)
	pdf = FPDF()
	pdf.add_page()
	pdf.set_font("Arial", size=12)
	pdf.cell(200, 10, txt="Legal Case Details", ln=True, align='C')
	pdf.ln(10)
	pdf.cell(200, 10, txt=f"Name: {case.name}", ln=True)
	pdf.cell(200, 10, txt=f"Case: {case.case}", ln=True)
	pdf.cell(200, 10, txt=f"Date: {case.date}", ln=True)
	pdf.cell(200, 10, txt=f"KTP: {case.ktp}", ln=True)
	pdf.cell(200, 10, txt=f"Email: {case.email}", ln=True)
	pdf.cell(200, 10, txt=f"Phone: {case.phone}", ln=True)
	pdf_path = f"case_{case_id}.pdf"
	pdf.output(pdf_path)
	return redirect(url_for('admin'))

@app.route('/logout')
def logout():
	session.clear()
	flash('You have been logged out.')
	return redirect(url_for('index'))

# Create DB tables
with app.app_context():
	db.create_all()

if __name__ == '__main__':
	app.run(debug=True,  port=5001)





