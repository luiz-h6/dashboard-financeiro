-- SQLite Schema

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    account_type TEXT NOT NULL,
    initial_balance REAL DEFAULT 0.00,
    credit_limit REAL,
    closing_day INTEGER,
    due_day INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    color TEXT DEFAULT '#000000',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    account_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    type TEXT NOT NULL,
    amount REAL NOT NULL,
    date DATE NOT NULL,
    description TEXT,
    is_essential BOOLEAN DEFAULT 0,
    is_fixed BOOLEAN DEFAULT 0,
    status TEXT DEFAULT 'paid',
    installment_number INTEGER DEFAULT 1,
    total_installments INTEGER DEFAULT 1,
    parent_transaction_id INTEGER DEFAULT NULL,
    transfer_account_id INTEGER DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE RESTRICT,
    FOREIGN KEY (parent_transaction_id) REFERENCES transactions(id) ON DELETE CASCADE,
    FOREIGN KEY (transfer_account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS investments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    account_id INTEGER,
    name TEXT NOT NULL,
    type TEXT NOT NULL,
    symbol TEXT,
    quantity REAL NOT NULL DEFAULT 1,
    average_price REAL NOT NULL,
    current_price REAL,
    purchase_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS goals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    target_amount REAL NOT NULL,
    current_amount REAL DEFAULT 0.00,
    deadline DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    amount REAL NOT NULL,
    month_year TEXT, -- 'YYYY-MM' ou nulo para budget global da categoria
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
);

-- VIEWS ANALÍTICAS PARA O DASHBOARD (Adaptadas para SQLite)

DROP VIEW IF EXISTS view_monthly_cashflow;
CREATE VIEW view_monthly_cashflow AS
SELECT 
    user_id,
    strftime('%Y-%m', date) AS month_year,
    SUM(CASE WHEN type = 'income' AND status = 'paid' THEN amount ELSE 0 END) AS total_income,
    SUM(CASE WHEN type = 'expense' AND status = 'paid' THEN amount ELSE 0 END) AS total_expense,
    (SUM(CASE WHEN type = 'income' AND status = 'paid' THEN amount ELSE 0 END) - 
     SUM(CASE WHEN type = 'expense' AND status = 'paid' THEN amount ELSE 0 END)) AS net_balance
FROM transactions
GROUP BY user_id, strftime('%Y-%m', date);

DROP VIEW IF EXISTS view_expenses_by_category;
CREATE VIEW view_expenses_by_category AS
SELECT 
    t.user_id,
    strftime('%Y-%m', t.date) AS month_year,
    c.id AS category_id,
    c.name AS category_name,
    SUM(t.amount) AS total_amount
FROM transactions t
JOIN categories c ON t.category_id = c.id
WHERE t.type = 'expense' AND t.status = 'paid'
GROUP BY t.user_id, strftime('%Y-%m', t.date), c.id, c.name;

DROP VIEW IF EXISTS view_essential_vs_non_essential;
CREATE VIEW view_essential_vs_non_essential AS
SELECT 
    user_id,
    strftime('%Y-%m', date) AS month_year,
    SUM(CASE WHEN is_essential = 1 THEN amount ELSE 0 END) AS essential_expenses,
    SUM(CASE WHEN is_essential = 0 THEN amount ELSE 0 END) AS non_essential_expenses
FROM transactions
WHERE type = 'expense' AND status = 'paid'
GROUP BY user_id, strftime('%Y-%m', date);

DROP VIEW IF EXISTS view_account_balances;
CREATE VIEW view_account_balances AS
SELECT 
    a.id AS account_id,
    a.user_id,
    a.name AS account_name,
    a.account_type,
    a.initial_balance,
    COALESCE(t.total_incomes, 0) AS total_incomes,
    COALESCE(t.total_expenses, 0) AS total_expenses,
    COALESCE(t.total_transfer_out, 0) AS total_transfer_out,
    COALESCE(tin.total_transfer_in, 0) AS total_transfer_in,
    (a.initial_balance + 
     COALESCE(t.total_incomes, 0) - 
     COALESCE(t.total_expenses, 0) - 
     COALESCE(t.total_transfer_out, 0) + 
     COALESCE(tin.total_transfer_in, 0)) AS current_balance
FROM accounts a
LEFT JOIN (
    SELECT 
        account_id,
        SUM(CASE WHEN type = 'income' THEN amount ELSE 0 END) AS total_incomes,
        SUM(CASE WHEN type = 'expense' THEN amount ELSE 0 END) AS total_expenses,
        SUM(CASE WHEN type = 'transfer' THEN amount ELSE 0 END) AS total_transfer_out
    FROM transactions
    WHERE status = 'paid'
    GROUP BY account_id
) t ON a.id = t.account_id
LEFT JOIN (
    SELECT 
        transfer_account_id,
        SUM(amount) AS total_transfer_in
    FROM transactions
    WHERE type = 'transfer' AND status = 'paid'
    GROUP BY transfer_account_id
) tin ON a.id = tin.transfer_account_id;
