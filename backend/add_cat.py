import sqlite3
conn = sqlite3.connect("finance.db")
conn.execute("INSERT INTO categories (user_id, name, type, color) VALUES (1, 'Assinaturas', 'expense', '#ec4899')")
conn.commit()
