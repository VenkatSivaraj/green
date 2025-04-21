import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# --- CONFIG ---
TICKERS = [
    "NVDA", "TSLA", "SOXL", "NFLX", "LLY", "AVGO", "DG", "MARA", "IBIT",
    "PLTR", "AMZN", "AMD", "HOOD", "CLSK", "META", "GOOGL", "MSTR", "SOUN",
    "BABA", "JD", "MSFT", "CMG", "CRM", "RDDT", "OKTA", "AMAT", "LNTH", "TSM"
]

st.set_page_config(layout="wide")
st.title("📡 Real-Time Trade Setup Scanner")
st.write("Scans for VWAP Reclaim and ORB Breakdown setups")

# --- HELPER FUNCTIONS ---
def fetch_intraday(ticker, interval="5m", lookback="1d"):
    try:
        df = yf.download(tickers=ticker, interval=interval, period=lookback, progress=False)
        df.dropna(inplace=True)
        df["VWAP"] = (df["Volume"] * (df["High"] + df["Low"] + df["Close"]) / 3).cumsum() / df["Volume"].cumsum()
        return df
    except:
        return None

def check_setups(df):
    signals = []
    if df is None or df.empty or len(df) < 3:
        return signals

    try:
        latest_close = float(df["Close"].iloc[-1])
        prev_close = float(df["Close"].iloc[-2])
        latest_vwap = float(df["VWAP"].iloc[-1])
        prev_vwap = float(df["VWAP"].iloc[-2])
    except Exception:
        return signals  # in case of NaN or bad data

    # VWAP Reclaim
    if prev_close < prev_vwap and latest_close > latest_vwap:
        signals.append("VWAP Reclaim")

    # ORB Breakdown (First 15-min low broken)
    try:
        opening_range_low = float(df.iloc[:3]["Low"].min())
        if latest_close < opening_range_low:
            signals.append("ORB Breakdown")
    except:
        pass

    return signals

# --- MAIN ---
st.info("Scanning tickers...")

results = []

for ticker in TICKERS:
    df = fetch_intraday(ticker)
    setups = check_setups(df)
    if setups:
        results.append({"Ticker": ticker, "Setups": ", ".join(setups)})

if results:
    st.success(f"Found {len(results)} setups.")
    st.dataframe(pd.DataFrame(results))
else:
    st.warning("No setups found at this moment.")
