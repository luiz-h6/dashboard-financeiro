import pandas as pd
from db import get_db

def get_dashboard_data(user_id):
    conn = get_db()
    cursor = conn.cursor()
    
    # 1. PROCESSAMENTO DOS SALDOS
    cursor.execute("SELECT * FROM view_account_balances WHERE user_id = ?", (user_id,))
    accounts_data = [dict(r) for r in cursor.fetchall()]
        
    df_accounts = pd.DataFrame(accounts_data)
    total_balance = 0.0
    if not df_accounts.empty:
        df_accounts['current_balance'] = df_accounts['current_balance'].astype(float)
        total_balance = df_accounts['current_balance'].sum()

    # 2. PROCESSAMENTO DO FLUXO DE CAIXA E INDICADORES
    cursor.execute("SELECT * FROM view_monthly_cashflow WHERE user_id = ? ORDER BY month_year", (user_id,))
    cashflow_data = [dict(r) for r in cursor.fetchall()]
        
    df_cashflow = pd.DataFrame(cashflow_data)
    
    if not df_cashflow.empty:
        df_cashflow['total_income'] = df_cashflow['total_income'].astype(float)
        df_cashflow['total_expense'] = df_cashflow['total_expense'].astype(float)
        df_cashflow['net_balance'] = df_cashflow['net_balance'].astype(float)
        
        df_cashflow['savings_rate_pct'] = df_cashflow.apply(
            lambda row: round((row['net_balance'] / row['total_income'] * 100), 2) if row['total_income'] > 0 else 0,
            axis=1
        )
        
        df_cashflow['expense_growth_pct'] = df_cashflow['total_expense'].pct_change() * 100
        df_cashflow.fillna(0, inplace=True)
        df_cashflow['expense_growth_pct'] = df_cashflow['expense_growth_pct'].round(2)

    # 3. PROCESSAMENTO DE GASTOS ESSENCIAIS VS NÃO ESSENCIAIS
    cursor.execute("SELECT * FROM view_essential_vs_non_essential WHERE user_id = ? ORDER BY month_year", (user_id,))
    essential_data = [dict(r) for r in cursor.fetchall()]
        
    df_essential = pd.DataFrame(essential_data)
    
    if not df_essential.empty:
        df_essential['essential_expenses'] = df_essential['essential_expenses'].astype(float)
        df_essential['non_essential_expenses'] = df_essential['non_essential_expenses'].astype(float)
        
        df_essential['total_monthly'] = df_essential['essential_expenses'] + df_essential['non_essential_expenses']
        df_essential['essential_ratio_pct'] = df_essential.apply(
            lambda r: round((r['essential_expenses'] / r['total_monthly'] * 100), 2) if r['total_monthly'] > 0 else 0,
            axis=1
        )

    # 4. PROCESSAMENTO DE GASTOS POR CATEGORIA E BUDGETS
    cursor.execute("SELECT * FROM view_expenses_by_category WHERE user_id = ?", (user_id,))
    category_data = [dict(r) for r in cursor.fetchall()]
    df_categories = pd.DataFrame(category_data)
    
    cursor.execute("SELECT * FROM budgets WHERE user_id = ?", (user_id,))
    budgets_data = [dict(r) for r in cursor.fetchall()]
    df_budgets = pd.DataFrame(budgets_data)

    cat_summary_list = []
    if not df_categories.empty:
        df_categories['total_amount'] = df_categories['total_amount'].astype(float)
        
        # Agrupa os gastos totais globais por categoria (simplificado para o dashboard)
        df_cat_summary = df_categories.groupby('category_name').agg({'total_amount': 'sum', 'category_id': 'first'}).reset_index()
        df_cat_summary = df_cat_summary.sort_values(by='total_amount', ascending=False)
        
        for _, row in df_cat_summary.iterrows():
            cat_id = row['category_id']
            spent = row['total_amount']
            budget_limit = 0
            if not df_budgets.empty:
                b_row = df_budgets[(df_budgets['category_id'] == cat_id) & (df_budgets['month_year'].isnull())]
                if not b_row.empty:
                    budget_limit = float(b_row.iloc[0]['amount'])
                    
            cat_summary_list.append({
                "category_name": row['category_name'],
                "total_amount": spent,
                "budget_limit": budget_limit,
                "budget_pct": round((spent / budget_limit * 100), 2) if budget_limit > 0 else 0
            })
    
    # 5. FORECASTING (PROJEÇÃO)
    # Lógica: Pega despesas de 'status' = 'pending' ou datas futuras (para simplificar, pegamos todas as transações futuras)
    import datetime
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    cursor.execute("SELECT type, SUM(amount) as total FROM transactions WHERE user_id=? AND date > ? GROUP BY type", (user_id, today_str))
    future_data = cursor.fetchall()
    future_incomes = 0
    future_expenses = 0
    for r in future_data:
        if r['type'] == 'income': future_incomes += r['total']
        elif r['type'] == 'expense': future_expenses += r['total']
        
    forecasting = {
        "future_incomes": future_incomes,
        "future_expenses": future_expenses,
        "projected_balance": total_balance + future_incomes - future_expenses
    }

    return {
        "summary": {
            "total_current_balance": total_balance
        },
        "forecasting": forecasting,
        "accounts": df_accounts.to_dict(orient="records") if not df_accounts.empty else [],
        "cashflow": df_cashflow.to_dict(orient="records") if not df_cashflow.empty else [],
        "essential_vs_non_essential": df_essential.to_dict(orient="records") if not df_essential.empty else [],
        "expenses_by_category": cat_summary_list
    }
