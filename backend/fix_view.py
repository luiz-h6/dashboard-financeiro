import sqlite3

conn = sqlite3.connect('finance.db')
conn.execute('DROP VIEW IF EXISTS view_expenses_by_category')
sql = """
CREATE VIEW view_expenses_by_category AS 
SELECT t.user_id, strftime('%Y-%m', t.date) AS month_year, c.id AS category_id, c.name AS category_name, SUM(t.amount) AS total_amount 
FROM transactions t 
JOIN categories c ON t.category_id = c.id 
WHERE t.type = 'expense' AND t.status = 'paid' 
GROUP BY t.user_id, strftime('%Y-%m', t.date), c.id, c.name;
"""
conn.execute(sql)
conn.commit()
print("View updated.")
