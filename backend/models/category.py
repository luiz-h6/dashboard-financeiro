from db import get_db

def create_category(data):
    conn = get_db()
    cursor = conn.cursor()
    sql = "INSERT INTO categories (user_id, name, type, color) VALUES (?, ?, ?, ?)"
    cursor.execute(sql, (data.get('user_id'), data['name'], data['type'], data.get('color', '#000000')))
    conn.commit()
    return cursor.lastrowid

def get_categories(user_id=None):
    conn = get_db()
    cursor = conn.cursor()
    if user_id:
        cursor.execute("SELECT * FROM categories WHERE user_id = ? OR user_id IS NULL", (user_id,))
    else:
        cursor.execute("SELECT * FROM categories WHERE user_id IS NULL")
    return [dict(row) for row in cursor.fetchall()]

def update_category(category_id, user_id, data):
    conn = get_db()
    cursor = conn.cursor()
    sql = "UPDATE categories SET name=?, type=?, color=? WHERE id=? AND user_id=?"
    cursor.execute(sql, (data['name'], data['type'], data['color'], category_id, user_id))
    conn.commit()
    return cursor.rowcount

def delete_category(category_id, user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM categories WHERE id=? AND user_id=?", (category_id, user_id))
    conn.commit()
    return cursor.rowcount
