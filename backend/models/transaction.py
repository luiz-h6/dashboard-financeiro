from db import get_db

import datetime
from dateutil.relativedelta import relativedelta

def create_transaction(data):
    conn = get_db()
    cursor = conn.cursor()
    sql = """
        INSERT INTO transactions 
        (user_id, account_id, category_id, type, amount, date, description, is_essential, is_fixed, status, installment_number, total_installments, parent_transaction_id, transfer_account_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """
    
    total_installments = int(data.get('total_installments', 1))
    base_date = datetime.datetime.strptime(data['date'], "%Y-%m-%d").date()
    amount_per_installment = round(float(data['amount']) / total_installments, 2)
    
    first_id = None
    
    for i in range(total_installments):
        installment_date = base_date + relativedelta(months=i)
        desc = data.get('description', '')
        if total_installments > 1:
            desc = f"{data.get('description', '')} ({i+1}/{total_installments})"
            
        cursor.execute(sql, (
            data['user_id'], data['account_id'], data.get('category_id'), data['type'], 
            amount_per_installment, installment_date.strftime("%Y-%m-%d"), desc, 
            data.get('is_essential', 0), data.get('is_fixed', 0),
            data.get('status', 'paid'), i+1, total_installments,
            first_id, data.get('transfer_account_id')
        ))
        
        if i == 0:
            first_id = cursor.lastrowid
            
    conn.commit()
    return first_id

def get_transactions(user_id, month=None, year=None):
    conn = get_db()
    cursor = conn.cursor()
    query = "SELECT * FROM transactions WHERE user_id = ?"
    params = [user_id]
    
    # SQLite não tem função MONTH()/YEAR() nativa fácil sem strftime, vamos usar substr ou like
    # Mas como a data é ISO (YYYY-MM-DD), podemos usar LIKE ou strftime
    if month and year:
        month_str = str(month).zfill(2)
        query += " AND strftime('%m', date) = ? AND strftime('%Y', date) = ?"
        params.extend([month_str, str(year)])
        
    query += " ORDER BY date DESC"
    cursor.execute(query, tuple(params))
    return [dict(row) for row in cursor.fetchall()]

def update_transaction(transaction_id, user_id, data):
    conn = get_db()
    cursor = conn.cursor()
    sql = """
        UPDATE transactions 
        SET account_id=?, category_id=?, type=?, amount=?, date=?, description=?, 
            is_essential=?, is_fixed=?, status=?, transfer_account_id=?
        WHERE id=? AND user_id=?
    """
    cursor.execute(sql, (
        data['account_id'], data['category_id'], data['type'], data['amount'], data['date'], 
        data.get('description'), data.get('is_essential', 0), data.get('is_fixed', 0), data.get('status', 'paid'), 
        data.get('transfer_account_id'), transaction_id, user_id
    ))
    conn.commit()
    return cursor.rowcount

def delete_transaction(transaction_id, user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions WHERE id=? AND user_id=?", (transaction_id, user_id))
    conn.commit()
    return cursor.rowcount
