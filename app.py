from flask import Flask, render_template, request, redirect, url_for, flash, session, render_template_string
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
from flask import make_response
from io import BytesIO
from email.mime.text import MIMEText
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
from functools import wraps
import smtplib
import urllib.parse
import secrets
import os
import hashlib
from reportlab.pdfgen import canvas
from flask import send_file
import sqlite3
import smtplib
from email.message import EmailMessage
from reportlab.pdfgen import canvas
from flask import send_file
from email.mime.text import MIMEText
from itsdangerous import URLSafeTimedSerializer

def update_user_password(email, new_password):
	hashed_password = generate_password_hash(new_password)
	conn = sqlite3.connect('noteapp.db')  # Replace with your DB name
	cursor = conn.cursor()
	cursor.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_password, email))
	conn.commit()
	conn.close()

def generate_token(email):
	serializer = URLSafeTimedSerializer(app.secret_key)
	return serializer.dumps(email, salt='password-reset-salt')

def confirm_token(token, expiration=3600):
	serializer = URLSafeTimedSerializer(app.secret_key)
	try:
		email = serializer.loads(token, salt='password-reset-salt', max_age=expiration)
	except Exception:
		return None
	return email

def send_reset_email(to_email, reset_link):
	msg = MIMEText(f"Click this link to reset your password: {reset_link}")
	msg['Subject'] = 'Reset Your Password'
	msg['From'] = 'afrialdosiagian@gmail.com'
	msg['To'] = to_email

	with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
		server.login('afrialdosiagian@gmail.com', 'xkbz bxjv ohfm zchl')
		server.send_message(msg)

def get_db_connection():
	conn = sqlite3.connect('noteapp.db')
	conn.row_factory = sqlite3.Row  # So you can access data like job['judul']
	return conn

def get_db_connection():
	conn = sqlite3.connect('noteapp.db')
	conn.row_factory = sqlite3.Row
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
DATABASE = 'your_database.db'

# Temporary storage for reset tokens (or use database)
reset_tokens = {}
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
@app.route('/static/images/Legal_Update.png/business_tax.jpg/data_privacy.png/fintech.png/labor_law.png<path:filename>')
def static_files(filename):
	return send_from_directory('static/images', filename)

@app.route('/journal')
def journal():
	return render_template('journal.html')

@app.route('/repository')
def repository():
	return render_template('repository.html')

@app.route('/undang')
def undang_undang():
        return render_template('undang_undang.html')

@app.route('/putusan')
def putusan():
        return render_template('putusan.html')

@app.route('/perjanjian')
def perjanjian():
        return render_template('perjanjian.html')

@app.route('/doktrin')
def doktrin():
        return render_template('doktrin.html')

@app.route('/legal-public')
def legal_public():
	return render_template('legal_public.html')

@app.route('/legal-privat')
def legal_privat():
	return render_template('legal_privat.html')

@app.route('/legal-bot', methods=['GET', 'POST'])
def legal_bot():
	answer = None
	if request.method == 'POST':
		question = request.form['question']
		# Simulate a basic bot answer for demo
		answer = f"Pertanyaan '{question}' telah diterima. Tim kami akan memberikan jawaban secepatnya."
	return render_template('legal_bot.html', answer=answer)

@app.route('/fgd-legal')
def fgd_legal():
	return render_template('fgd_legal.html')

@app.route('/services')
def services():
	return render_template('services.html')

@app.route('/services/legal')
def legal_service():
	return render_template('services_legal.html')

@app.route('/services/permit')
def permit_service():
	return render_template('services_permit.html')

@app.route('/faqs')
def faqs():
	return render_template('faqs.html')


@app.route('/sidebar')
def sidebar():
	return render_template('sidebar.html')

def block_page():
	with open("index.html") as f:
		return render_template_string(f.read())

@app.route('/')
def index():
	return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'POST':
		email = request.form['email']
		password = hashlib.sha256(request.form['password'].encode()).hexdigest()

		conn = sqlite3.connect('noteapp.db')
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, password))
		user = cursor.fetchone()
		conn.close()

		if user:
			session['user_id'] = user[0]
			session['email'] = user[1]
			return redirect('/dashboard')
		else:
			flash('❌ Invalid login.', 'danger')
	return render_template('login.html')

@app.route('/dashboard')
def dashboard():
	if 'user_id' not in session:
		flash('Please log in first.')
		return redirect(url_for('index'))

	user = User.query.get(session['user_id'])
	user_cases = LegalCase.query.filter_by(email=user.email).all()
	return render_template('dashboard.html', user=user, user_cases=user_cases)

@app.route('/register', methods=['GET', 'POST'])
def register():
	if request.method == 'POST':
		email = request.form['email']
		password = hashlib.sha256(request.form['password'].encode()).hexdigest()

		conn = sqlite3.connect('noteapp.db')
		cursor = conn.cursor()
		try:
			cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
			conn.commit()
			flash("✅ Registered successfully!", "success")
		except sqlite3.IntegrityError:
			flash("❌ Email already registered.", "danger")
			conn.close()
		return redirect('/login')
	return render_template('register.html')


@app.route('/about')
def about():
	return render_template('about.html')

@app.route('/news')
def news():
	return render_template('news.html')

@app.route('/peraturan')
def peraturan():
	return render_template('peraturan.html')

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
	if request.method == 'POST':
		email = request.form['email']
		conn = sqlite3.connect('noteapp.db')
		cursor = conn.cursor()
		cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
		user = cursor.fetchone()
		conn.close()

		if user:
        	    # Continue with sending reset link
			flash("Reset link has been sent!", "success")
		else:
			flash("Email not found.", "danger")
	return render_template("forgot_password.html")


@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password(token):
	if request.method == 'POST':
		password = request.form['password']
		confirm = request.form['confirm_password']
		if password != confirm:
			flash("❌ Passwords do not match.", "danger")
			return redirect(request.url)

		hashed = hashlib.sha256(password.encode()).hexdigest()

		conn = sqlite3.connect('noteapp.db')
		cursor = conn.cursor()
		cursor.execute("UPDATE users SET password = ?, reset_token = NULL WHERE reset_token = ?", (hashed, token))
		conn.commit()
		conn.close()

		flash("✅ Password reset successful!", "success")
		return redirect('/login')

	return render_template('reset_password.html', token=token)


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

def send_email(subject, user, body):
	reset_link = f"http://127.0.0.1:5001/reset-password/{token}"
	msg = MIMEText(f"Click the link to reset your password: {reset_link}")
	sender_email = "afrialdosiagian@gmail.com"
	sender_password = "xkbz bxjv ohfm zchl"

	msg = MIMEText(body)
	msg['Subject'] = subject
	msg['From'] = sender_email
	msg['To'] = user

	with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
		smtp.login('afrialdosiagian@gmail.com', 'xkbz bxjv ohfm zchl')
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

@app.route('/delete_job/<int:job_id>')
def delete_job(job_id):
	conn = get_db_connection()
	conn.execute('DELETE FROM jobs WHERE id = ?', (job_id,))
	conn.commit()
	conn.close()
	flash('Job deleted successfully.')
	return redirect(url_for('crew_dashboard'))


@app.route('/download_pdf/<int:job_id>')
def download_pdf(job_id):
	conn = get_db_connection()
	job = conn.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()
	conn.close()

	if not job:
		return "Job not found", 404

	pdf_path = f"job_{job_id}.pdf"
	c = canvas.Canvas(pdf_path)
	c.setFont("Helvetica", 14)
	c.drawString(72, 800, f"Judul: {job['judul']}")
	c.drawString(72, 780, f"Pasal: {job['pasal']}")
	c.drawString(72, 760, f"Isi: {job['isi'][:100]}")
	c.drawString(72, 740, f"Penjelasan: {job['penjelasan'][:100]}")
	c.save()

	return send_file(pdf_path, as_attachment=True)

@app.route('/share_whatsapp/<int:job_id>')
def share_whatsapp(job_id):
	conn = get_db_connection()
	job = conn.execute('SELECT * FROM jobs WHERE id = ?', (job_id,)).fetchone()
	conn.close()

	if not job:
		return "Job not found", 404

	message = f"""*Legal Draft*\n📘 *{job['judul']}*\n📑 *{job['pasal']}*\n📝 *Isi*: {job['isi']}\n💬 *Penjelasan*: {job['penjelasan']}"""
	encoded_msg = urllib.parse.quote(message)
	whatsapp_url = f"https://wa.me/?text={encoded_msg}"
	return redirect(whatsapp_url)

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
	flash("🔒 Logged out.", "info")
	return redirect('/login')


# Create DB tables
with app.app_context():
	db.create_all()

if __name__ == '__main__':
	app.run(debug=True,  port=5001)






