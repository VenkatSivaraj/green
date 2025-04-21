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

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    # VWAP Reclaim
    if prev["Close"] < prev["VWAP"] and latest["Close"] > latest["VWAP"]:
        signals.append("VWAP Reclaim")

    # ORB Breakdown (First 15-min low broken)
    opening_range_low = df.iloc[:3]["Low"].min()  # first 15-min if 5-min bars
    if latest["Close"] < opening_range_low:
        signals.append("ORB Breakdown")

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
