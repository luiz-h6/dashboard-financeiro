import sqlite3
import os
from flask import g

# O banco de dados SQLite será criado na pasta backend
DATABASE = os.path.join(os.path.dirname(__file__), 'finance.db')

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
            DATABASE,
            detect_types=sqlite3.PARSE_DECLTYPES
        )
        # Permite acessar as colunas pelo nome (como um dicionário)
        g.db.row_factory = sqlite3.Row
    return g.db

def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()
        
def init_app(app):
    app.teardown_appcontext(close_db)

def init_db(app):
    """Executa o script de schema.sql para criar as tabelas no SQLite se não existirem"""
    schema_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'database', 'schema.sql')
    if os.path.exists(schema_path):
        with app.app_context():
            db = get_db()
            with open(schema_path, 'r', encoding='utf-8') as f:
                db.executescript(f.read())
            db.commit()
