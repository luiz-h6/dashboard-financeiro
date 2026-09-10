from db import get_db

def set_budget(data):
    conn = get_db()
    cursor = conn.cursor()
    
    # Verifica se já existe orçamento para a categoria no mês (ou global)
    sql_check = "SELECT id FROM budgets WHERE user_id=? AND category_id=? AND (month_year=? OR (month_year IS NULL AND ? IS NULL))"
    cursor.execute(sql_check, (data['user_id'], data['category_id'], data.get('month_year'), data.get('month_year')))
    row = cursor.fetchone()
    
    if row:
        sql = "UPDATE budgets SET amount=? WHERE id=?"
        cursor.execute(sql, (data['amount'], row['id']))
        conn.commit()
        return row['id']
    else:
        sql = "INSERT INTO budgets (user_id, category_id, amount, month_year) VALUES (?, ?, ?, ?)"
        cursor.execute(sql, (data['user_id'], data['category_id'], data['amount'], data.get('month_year')))
        conn.commit()
        return cursor.lastrowid

def get_budgets(user_id, month_year=None):
    conn = get_db()
    cursor = conn.cursor()
    if month_year:
        sql = """
            SELECT b.*, c.name as category_name, c.color 
            FROM budgets b 
            JOIN categories c ON b.category_id = c.id 
            WHERE b.user_id=? AND (b.month_year=? OR b.month_year IS NULL)
        """
        cursor.execute(sql, (user_id, month_year))
    else:
        sql = """
            SELECT b.*, c.name as category_name, c.color 
            FROM budgets b 
            JOIN categories c ON b.category_id = c.id 
            WHERE b.user_id=?
        """
        cursor.execute(sql, (user_id,))
        
    return [dict(row) for row in cursor.fetchall()]

def delete_budget(budget_id, user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM budgets WHERE id=? AND user_id=?", (budget_id, user_id))
    conn.commit()
    return cursor.rowcount
