import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np

st.set_page_config(page_title="Pro Analyst Bot", layout="wide")
st.title("🚀 High-Beta Signal Bot")

# Sidebar
tickers_input = st.sidebar.text_area("Watchlist", "TSLA, NVDA, AMD, PLTR, MSFT, COIN, MSTR")
target_beta = st.sidebar.slider("Min Beta", 1.0, 2.5, 1.3)

def calculate_rsi(data, window=14):
    delta = data.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def get_signals(ticker):
    try:
        stock = yf.Ticker(ticker)
        # Get History for RSI
        hist = stock.history(period="1mo")
        if len(hist) < 15: return None
        
        current_rsi = calculate_rsi(hist['Close']).iloc[-1]
        info = stock.info
        
        # Fundamentals
        beta = info.get('beta', 0)
        price = info.get('currentPrice', 0)
        
        # Signal Logic
        signal = "WAIT"
        action_color = "white"
        
        if current_rsi < 40 and beta >= target_beta:
            signal = "ENTRY (Sell Put)"
            action_color = "green"
        elif current_rsi > 65:
            signal = "EXIT (Sell Call)"
            action_color = "red"
            
        return {
            "Ticker": ticker,
            "Price": f"${price:.2f}",
            "RSI": round(current_rsi, 1),
            "Beta": round(beta, 2),
            "Signal": signal,
            "Color": action_color
        }
    except: return None

if st.button("Generate Signals"):
    results = []
    t_list = [t.strip().upper() for t in tickers_input.split(",")]
    
    for t in t_list:
        data = get_signals(t)
        if data: results.append(data)
    
    if results:
        df = pd.DataFrame(results)
        
        # Styling the table for mobile
        def color_signal(val):
            color = 'green' if 'ENTRY' in val else 'red' if 'EXIT' in val else 'gray'
            return f'color: {color}; font-weight: bold'

        st.table(df.style.applymap(color_signal, subset=['Signal']))
        
        st.info("💡 Tip: For 'ENTRY' signals, look for Cash-Secured Puts. For 'EXIT' signals, look for Covered Calls.")
