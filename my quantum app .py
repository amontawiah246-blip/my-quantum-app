import streamlit as st
import yfinance as yf
import pandas_ta as ta
import mplfinance as mpf
from datetime import datetime, timedelta

# 1. Page Configuration
st.set_page_config(page_title="My Trading Bot", layout="wide")

# 2. Sidebar Settings
st.sidebar.header("🛠 Strategy Settings")
ticker = st.sidebar.text_input("Enter Ticker", value="BTC-USD")
timeframe = st.sidebar.selectbox("Select Timeframe", ("1h", "4h", "1d", "1wk"))
period = st.sidebar.slider("Days of Historical Data", 7, 365, 30)

# 3. Data Fetching
@st.cache_data(ttl=300) # Refresh every 5 minutes
def fetch_data(symbol, tf, days):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    df = yf.download(symbol, start=start_date, end=end_date, interval=tf)
    return df

st.title(f"📊 Trading Dashboard: {ticker}")

try:
    df = fetch_data(ticker, timeframe, period)

    if not df.empty:
        # 4. Technical Analysis
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['EMA_20'] = ta.ema(df['Close'], length=20)
        df['EMA_50'] = ta.ema(df['Close'], length=50)

        # 5. Signal Logic
        last_rsi = df['RSI'].iloc[-1]
        last_close = df['Close'].iloc[-1]
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Current Price", f"${last_close:,.2f}")
        col2.metric("RSI (14)", f"{last_rsi:.2f}")
        
        if last_rsi < 30:
            col3.success("SIGNAL: OVERSOLD (BUY)")
        elif last_rsi > 70:
            col3.error("SIGNAL: OVERBOUGHT (SELL)")
        else:
            col3.warning("SIGNAL: NEUTRAL")

        # 6. Charting
        st.subheader("Price Action & Indicators")
        apds = [
            mpf.make_addplot(df['EMA_20'], color='orange', width=1),
            mpf.make_addplot(df['EMA_50'], color='blue', width=1),
            mpf.make_addplot(df['RSI'], panel=1, color='purple', ylabel='RSI')
        ]
        
        fig, axlist = mpf.plot(df, type='candle', style='charles', 
                               addplot=apds, returnfig=True, 
                               figsize=(12, 8), volume=False)
        st.pyplot(fig)

        # 7. Data Table
        with st.expander("View Raw Data"):
            st.dataframe(df.tail(20))
            st.download_button("Download CSV", df.to_csv(), f"{ticker}_data.csv")
    else:
        st.error("No data found. Please check the ticker symbol.")

except Exception as e:
    st.error(f"Error fetching data: {e}")