import sqlite3

conn = sqlite3.connect('noteapp.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS jobs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    judul TEXT NOT NULL,
    pasal TEXT NOT NULL,
    isi TEXT NOT NULL,
    penjelasan TEXT NOT NULL
)
''')

conn.commit()
conn.close()

print("✅ jobs table created successfully!")

conn = sqlite3.connect('database.db')
conn.execute('''
CREATE TABLE IF NOT EXISTS jobs (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  judul TEXT NOT NULL,
  pasal TEXT NOT NULL,
  isi TEXT NOT NULL,
  penjelasan TEXT NOT NULL
)
''')
conn.commit()
conn.close()

print("✅ jobs table created.")


conn = sqlite3.connect('your_database.db')
c = conn.cursor()

c.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

conn.commit()
conn.close()

print("✅ users table created successfully in noteapp.db")


