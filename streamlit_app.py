import streamlit as st
import yfinance as yf
import pandas as pd

# Setup
st.set_page_config(page_title="Analyst Bot", layout="wide")
st.title("📈 Top 20 Analyst Scorer")

# Input Section
tickers_input = st.text_area("Enter Tickers (comma separated)", "TSLA, NVDA, AMD, PLTR, MSFT, META, AMZN, NFLX, AAPL, GOOGL")
target_beta = st.sidebar.slider("Min Beta", 1.0, 2.5, 1.3)

def get_data(tickers):
    results = []
    t_list = [t.strip().upper() for t in tickers.split(",")]
    for t in t_list:
        try:
            s = yf.Ticker(t).info
            beta = s.get('beta', 0)
            de = s.get('debtToEquity', 100) / 100
            margin = s.get('operatingMargins', 0)
            peg = s.get('pegRatio', 5)
            
            # Simple 100-point score
            score = 0
            if beta >= target_beta: score += 25
            if de < 1.0: score += 25
            if margin > 0.15: score += 25
            if peg < 1.5: score += 25
            
            results.append({"Ticker": t, "Score": score, "Beta": beta, "D/E": de, "Margin": f"{margin*100:.1f}%"})
        except: continue
    return pd.DataFrame(results)

if st.button("Run Analysis"):
    df = get_data(tickers_input)
    if not df.empty:
        st.dataframe(df.sort_values("Score", ascending=False).head(20))
