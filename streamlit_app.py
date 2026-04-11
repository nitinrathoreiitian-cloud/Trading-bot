import streamlit as st
import yfinance as yf
import pandas as pd

# App Setup
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
        hist = stock.history(period="1mo")
        if len(hist) < 15: return None
        
        # Technicals
        current_rsi = calculate_rsi(hist['Close']).iloc[-1]
        
        # Volatility Check
        daily_range = hist['High'].iloc[-1] - hist['Low'].iloc[-1]
        avg_range = (hist['High'] - hist['Low']).tail(10).mean()
        vol_status = "🔥 HIGH" if daily_range > avg_range else "Normal"
        
        info = stock.info
        beta = info.get('beta', 0)
        price = info.get('currentPrice', 0)
        
        # Logic for Entry/Exit
        signal = "HOLD"
        if current_rsi < 40 and beta >= target_beta:
            signal = "ENTRY (Sell Put)"
        elif current_rsi > 65:
            signal = "EXIT (Sell Call)"
            
        return {
            "Ticker": ticker,
            "Price": f"${price:.2f}",
            "RSI": round(current_rsi, 1),
            "Beta": round(beta, 2),
            "Vol": vol_status,
            "Signal": signal
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
        
        # Display as a clean, standard dataframe to avoid Styler errors
        st.dataframe(df, use_container_width=True)
        
        # Manual color indicators for mobile readability
        st.markdown("### 🚦 Signal Summary")
        for index, row in df.iterrows():
            if "ENTRY" in row['Signal']:
                st.success(f"**{row['Ticker']}**: {row['Signal']} (Price: {row['Price']})")
            elif "EXIT" in row['Signal']:
                st.error(f"**{row['Ticker']}**: {row['Signal']} (Price: {row['Price']})")
        
        st.markdown("""
        ---
        ### 💡 Analyst Strategy Notes:
        1. **ENTRY (Sell Put):** Stock is oversold. Premiums are high.
        2. **EXIT (Sell Call):** Stock is overbought. Lock in gains.
        3. **Vol 🔥 HIGH:** The 'Vegas' is high—options are more profitable to sell today.
        """)
