from db import get_db

def create_account(data):
    conn = get_db()
    cursor = conn.cursor()
    sql = "INSERT INTO accounts (user_id, name, account_type, initial_balance, credit_limit, closing_day, due_day) VALUES (?, ?, ?, ?, ?, ?, ?)"
    cursor.execute(sql, (
        data['user_id'], data['name'], data['account_type'], data.get('initial_balance', 0.0),
        data.get('credit_limit'), data.get('closing_day'), data.get('due_day')
    ))
    conn.commit()
    return cursor.lastrowid

def get_accounts(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts WHERE user_id = ?", (user_id,))
    return [dict(row) for row in cursor.fetchall()]

def get_account_by_id(account_id, user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM accounts WHERE id = ? AND user_id = ?", (account_id, user_id))
    row = cursor.fetchone()
    return dict(row) if row else None

def update_account(account_id, user_id, data):
    conn = get_db()
    cursor = conn.cursor()
    sql = "UPDATE accounts SET name=?, account_type=?, initial_balance=?, credit_limit=?, closing_day=?, due_day=? WHERE id=? AND user_id=?"
    cursor.execute(sql, (
        data['name'], data['account_type'], data.get('initial_balance', 0.0),
        data.get('credit_limit'), data.get('closing_day'), data.get('due_day'),
        account_id, user_id
    ))
    conn.commit()
    return cursor.rowcount

def delete_account(account_id, user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM accounts WHERE id=? AND user_id=?", (account_id, user_id))
    conn.commit()
    return cursor.rowcount
