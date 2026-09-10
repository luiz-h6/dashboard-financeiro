import os
import sqlite3
import datetime
import random

DATABASE = os.path.join(os.path.dirname(__file__), 'finance.db')

def seed_data():
    if not os.path.exists(DATABASE):
        print("Banco de dados não encontrado.")
        return

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    # 1. Inserir Usuário de Teste
    cursor.execute("INSERT OR IGNORE INTO users (id, name, email, password_hash) VALUES (1, 'Luiz', 'luiz@email.com', 'hash123')")

    # 2. Inserir Contas
    cursor.execute("INSERT OR IGNORE INTO accounts (id, user_id, name, account_type, initial_balance) VALUES (1, 1, 'Conta Corrente Nu', 'checking', 2500.00)")
    cursor.execute("INSERT OR IGNORE INTO accounts (id, user_id, name, account_type, initial_balance) VALUES (2, 1, 'Poupança Caixa', 'savings', 10000.00)")
    
    # 3. Inserir Categorias
    cursor.execute("INSERT OR IGNORE INTO categories (id, user_id, name, type, color) VALUES (1, 1, 'Salário', 'income', '#10b981')")
    cursor.execute("INSERT OR IGNORE INTO categories (id, user_id, name, type, color) VALUES (2, 1, 'Alimentação', 'expense', '#ef4444')")
    cursor.execute("INSERT OR IGNORE INTO categories (id, user_id, name, type, color) VALUES (3, 1, 'Moradia', 'expense', '#f59e0b')")
    cursor.execute("INSERT OR IGNORE INTO categories (id, user_id, name, type, color) VALUES (4, 1, 'Lazer', 'expense', '#3b82f6')")
    cursor.execute("INSERT OR IGNORE INTO categories (id, user_id, name, type, color) VALUES (5, 1, 'Transporte', 'expense', '#8b5cf6')")

    # 4. Inserir Investimentos (para testar API)
    cursor.execute("INSERT OR IGNORE INTO investments (id, user_id, account_id, name, type, symbol, quantity, average_price) VALUES (1, 1, 2, 'Petrobras', 'variable_income', 'PETR4.SA', 100, 32.50)")
    cursor.execute("INSERT OR IGNORE INTO investments (id, user_id, account_id, name, type, symbol, quantity, average_price) VALUES (2, 1, 2, 'Bitcoin', 'crypto', 'BTC-USD', 0.05, 300000.00)")

    # 5. Gerar Transações Mock (últimos 3 meses)
    # Limpar transações antigas para não duplicar se rodar várias vezes
    cursor.execute("DELETE FROM transactions")
    
    hoje = datetime.date.today()
    
    for i in range(3):
        mes_atual = hoje.replace(day=1) - datetime.timedelta(days=30 * i)
        ano = mes_atual.year
        mes = mes_atual.month
        
        # Salário
        data_salario = f"{ano}-{mes:02d}-05"
        cursor.execute("INSERT INTO transactions (user_id, account_id, category_id, type, amount, date, description, is_essential) VALUES (1, 1, 1, 'income', 8500.00, ?, 'Salário Mensal', 1)", (data_salario,))
        
        # Aluguel (Moradia)
        data_aluguel = f"{ano}-{mes:02d}-10"
        cursor.execute("INSERT INTO transactions (user_id, account_id, category_id, type, amount, date, description, is_essential) VALUES (1, 1, 3, 'expense', 2200.00, ?, 'Aluguel + Condomínio', 1)", (data_aluguel,))
        
        # Supermercado (Alimentação)
        data_mercado = f"{ano}-{mes:02d}-15"
        cursor.execute("INSERT INTO transactions (user_id, account_id, category_id, type, amount, date, description, is_essential) VALUES (1, 1, 2, 'expense', 1150.00, ?, 'Supermercado Mensal', 1)", (data_mercado,))
        
        # Uber (Transporte)
        data_transporte = f"{ano}-{mes:02d}-20"
        cursor.execute("INSERT INTO transactions (user_id, account_id, category_id, type, amount, date, description, is_essential) VALUES (1, 1, 5, 'expense', 350.00, ?, 'Uber e Metrô', 0)", (data_transporte,))
        
        # Ifood/Cinema (Lazer)
        data_lazer = f"{ano}-{mes:02d}-25"
        cursor.execute("INSERT INTO transactions (user_id, account_id, category_id, type, amount, date, description, is_essential) VALUES (1, 1, 4, 'expense', 600.00, ?, 'iFood e Cinema', 0)", (data_lazer,))

    conn.commit()
    conn.close()
    print("Dados fictícios inseridos com sucesso!")

if __name__ == '__main__':
    seed_data()
