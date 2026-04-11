import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Pro Wheel Bot", layout="wide")
st.title("🛡️ The Wheel Strategy & Capital Planner")

# Sidebar
tickers_input = st.sidebar.text_area("Watchlist", "TSLA, NVDA, AMD, PLTR, MSFT, COIN, MSTR")
risk_dist = st.sidebar.slider("Strike Distance (Safety %)", 5, 20, 10)

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_strategy(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1mo")
        if len(hist) < 15: return None
        
        price = hist['Close'].iloc[-1]
        rsi = calculate_rsi(hist['Close']).iloc[-1]
        info = stock.info
        
        # Strategy Logic
        action = "HOLD"
        strike = 0
        capital = 0
        
        if rsi < 40:
            action = "SELL PUT"
            strike = price * (1 - (risk_dist/100))
            capital = strike * 100 # Cash needed to back the put
        elif rsi > 65:
            action = "SELL CALL"
            strike = price * (1 + (risk_dist/100))
            capital = price * 100 # Value of 100 shares you must own
            
        return {
            "Ticker": ticker,
            "Price": f"${price:.2f}",
            "RSI": round(rsi, 1),
            "Action": action,
            "Strike": round(strike, 2),
            "Capital Req.": f"${int(capital):,}",
            "Stop Loss": round(strike * 0.95 if rsi < 40 else strike * 1.05, 2)
        }
    except: return None

if st.button("Calculate Capital & Signals"):
    results = [get_strategy(t.strip().upper()) for t in tickers_input.split(",")]
    results = [r for r in results if r]
    
    if results:
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)
        st.info("💡 'Capital Req' is the cash needed for 1 Put contract or the value of 100 shares for a Covered Call.")
