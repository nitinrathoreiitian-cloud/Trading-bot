import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Growth Sniper Bot", layout="wide")
st.title("🎯 Stock Sniper: Entry, Exit & Stop-Loss")

# Sidebar
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
        
        # Risk Management Logic
        max_inv = budget * 0.10
        shares = int(max_inv / price)
        
        # Calculations for Exit Points
        # Stop Loss at 7% below current price
        stop_loss = price * 0.93 
        # Profit Target at 15% above current price
        target = price * 1.15
        
        action = "HOLD"
        if rsi < 35: action = "🔥 BUY (Deep)"
        elif rsi < 45: action = "✅ BUY (Entry)"
        elif rsi > 70: action = "🚨 SELL (Profit)"
            
        return {
            "Ticker": ticker,
            "Price": round(price, 2),
            "RSI": round(rsi, 1),
            "Action": action,
            "Stop Loss": round(stop_loss, 2),
            "Profit Target": round(target, 2),
            "Shares": shares
        }
    except: return None

if st.button("Scan Market & Set Targets"):
    results = []
    t_list = [t.strip().upper() for t in tickers_input.split(",")]
    
    with st.spinner('Calculating Trade Targets...'):
        for t in t_list:
            res = get_stock_signal(t)
            if res: results.append(res)
    
    if results:
        df = pd.DataFrame(results)
        st.dataframe(df.sort_values("RSI"), use_container_width=True)
        
        # Summary for Mobile
        st.subheader("🚀 Active Trade Plans")
        buys = df[df['Action'].str.contains("BUY")]
        for _, row in buys.iterrows():
            with st.expander(f"PLAN: {row['Ticker']} at ${row['Price']}"):
                st.write(f"**Action:** {row['Action']}")
                st.write(f"**Amount:** Buy {row['Shares']} shares")
                st.error(f"**Stop Loss:** Sell if price hits ${row['Stop Loss']}")
                st.success(f"**Profit Target:** Sell if price hits ${row['Profit Target']}")
                st.info("💡 Also Sell if RSI hits 70, even if target price isn't met.")
