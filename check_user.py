from app import db, User, app

with app.app_context():
	print("\n📋 Registered Users:")
	users = User.query.all()
	if users:
		for user in users:
			print(f"ID: {user.id}, Email: {user.email}, Admin: {user.is_admin}")
		else:
			print("No users found.")

