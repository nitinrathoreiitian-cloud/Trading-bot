import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Growth Sniper Bot", layout="wide")
st.title("🎯 High-Beta Stock Watchlist (Expanded)")

# Expanded Watchlist
default_list = "TSLA, NVDA, AMD, PLTR, MSFT, COIN, MSTR, SMCI, ARM, SNOW, SHOP, SQ, META, GOOGL, AMZN, AVGO, NET, HOOD, SOFI, AI"
tickers_input = st.sidebar.text_area("Watchlist", default_list)
budget = st.sidebar.number_input("Your Total Budget ($)", value=10000)

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_stock_signal(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        if len(hist) < 15: return None
        
        price = hist['Close'].iloc[-1]
        rsi = calculate_rsi(hist['Close']).iloc[-1]
        
        # Risk Management: Max 10% of budget per stock
        max_investment = budget * 0.10
        shares_to_buy = int(max_investment / price)
        
        # Signals
        action = "HOLD"
        color = "white"
        if rsi < 35: 
            action = "🔥 BUY (Deep Dip)"
        elif rsi < 45: 
            action = "✅ BUY (Entry)"
        elif rsi > 70: 
            action = "🚨 SELL (Profit)"
            
        return {
            "Ticker": ticker,
            "Price": round(price, 2),
            "RSI": round(rsi, 1),
            "Action": action,
            "Shares": shares_to_buy,
            "Investment": f"${int(shares_to_buy * price):,}"
        }
    except: return None

if st.button("Scan Market"):
    results = []
    t_list = [t.strip().upper() for t in tickers_input.split(",")]
    
    with st.spinner('Scanning 20+ High-Beta Stocks...'):
        for t in t_list:
            res = get_stock_signal(t)
            if res: results.append(res)
    
    if results:
        df = pd.DataFrame(results)
        # Sort so the best buys are at the top
        st.dataframe(df.sort_values("RSI"), use_container_width=True)
        
        # Mobile Summary
        st.subheader("💡 Today's Best Setups")
        buys = df[df['Action'].str.contains("BUY")]
        if not buys.empty:
            for _, row in buys.iterrows():
                st.success(f"**{row['Ticker']}**: RSI {row['RSI']} - Buy {row['Shares']} shares (~{row['Investment']})")
        else:
            st.info("No deep dips found today. Patience is key!")
