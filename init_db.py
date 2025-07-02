import sqlite3

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

