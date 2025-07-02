from app import db, User, app

with app.app_context():
	email = input("Enter email to delete: ").strip()
	user = User.query.filter_by(email=email).first()
	if user:
		db.session.delete(user)
		db.session.commit()
		print("✅ User deleted.")
	else:
		print("❌ User not found.")
