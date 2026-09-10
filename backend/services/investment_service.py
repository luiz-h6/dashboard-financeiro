import yfinance as yf
from db import get_db

def get_live_quotes(tickers):
    """
    Busca as cotações atuais para uma lista de símbolos usando yfinance.
    """
    quotes = {}
    if not tickers:
        return quotes
        
    try:
        # yfinance permite buscar múltiplos tickers de uma vez
        data = yf.download(tickers, period="1d", progress=False)
        
        # Se for apenas 1 ticker, o formato do DataFrame é diferente de múltiplos
        if len(tickers) == 1:
            ticker = tickers[0]
            if not data.empty and 'Close' in data:
                quotes[ticker] = float(data['Close'].iloc[-1])
        else:
            if not data.empty and 'Close' in data:
                for ticker in tickers:
                    # Tenta obter o último fechamento
                    try:
                        quotes[ticker] = float(data['Close'][ticker].iloc[-1])
                    except:
                        quotes[ticker] = None
    except Exception as e:
        print(f"Erro ao buscar cotações: {e}")
        
    return quotes

def sync_investment_prices(user_id):
    """
    Busca os investimentos do usuário, pega os símbolos, busca na API e atualiza o banco de dados.
    """
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, symbol FROM investments WHERE user_id = ? AND symbol IS NOT NULL AND symbol != ''", (user_id,))
    investments = [dict(row) for row in cursor.fetchall()]
        
    if not investments:
        return {"message": "No investments with symbols found.", "updated": 0}
        
    # Extrai lista única de tickers
    tickers = list(set([inv['symbol'] for inv in investments]))
    
    # Busca na API
    live_quotes = get_live_quotes(tickers)
    
    updated_count = 0
    # Atualiza no banco
    for inv in investments:
        ticker = inv['symbol']
        if ticker in live_quotes and live_quotes[ticker] is not None:
            current_price = live_quotes[ticker]
            cursor.execute(
                "UPDATE investments SET current_price = ? WHERE id = ?", 
                (current_price, inv['id'])
            )
            updated_count += 1
            
    conn.commit()
    return {"message": "Prices synced successfully.", "updated": updated_count, "quotes": live_quotes}
