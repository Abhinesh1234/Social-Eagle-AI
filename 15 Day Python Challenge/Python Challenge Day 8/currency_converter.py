import streamlit as st
import requests
import pandas as pd
import datetime
import matplotlib.pyplot as plt

st.set_page_config(page_title="💱 Currency Converter", layout="centered")

st.title("💱 Currency Converter")

# --- Utility: fetch rates via Frankfurter ---
@st.cache_data(ttl=3600)
def fetch_rates(base: str, symbols: list[str] = None):
    """Fetch latest exchange rates from Frankfurter with given base and target symbols."""
    url = "https://api.frankfurter.dev/v1/latest"
    params = {"base": base}
    if symbols:
        params["symbols"] = ",".join(symbols)
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

@st.cache_data(ttl=3600)
def fetch_timeseries(base: str, target: str, days: int = 7):
    """Fetch time series (last `days`) for base->target."""
    end = datetime.date.today()
    start = end - datetime.timedelta(days=days)
    url = f"https://api.frankfurter.dev/v1/{start.isoformat()}..{end.isoformat()}"
    params = {"base": base, "symbols": target}
    resp = requests.get(url, params=params)
    resp.raise_for_status()
    return resp.json()

# --- UI: Select currencies & amount ---
all_rates = fetch_rates("USD")  # base USD gives a dictionary of “rates” keys
all_currencies = sorted([all_rates["base"]] + list(all_rates["rates"].keys()))

col1, col2 = st.columns([2, 1])
with col1:
    from_currency = st.selectbox("From", all_currencies, index=all_currencies.index("USD"))
    to_currency = st.selectbox("To", all_currencies, index=all_currencies.index("INR") if "INR" in all_currencies else 0)
with col2:
    amount = st.number_input("Amount", min_value=0.0, value=1.0, format="%.4f")

# --- Conversion logic ---
if from_currency and to_currency:
    rates_data = fetch_rates(from_currency, symbols=[to_currency])
    rate = rates_data["rates"].get(to_currency)

    if rate is None:
        st.error("Conversion rate not available.")
    else:
        converted = amount * rate
        st.markdown(f"### {amount:.4f} **{from_currency}** = **{converted:.4f} {to_currency}**")
        st.caption(f"Rate: 1 {from_currency} = {rate:.6f} {to_currency}")

        # --- Show small trend over last 7 days ---
        ts = fetch_timeseries(from_currency, to_currency, days=7)
        rates_ts = ts["rates"]

        # Convert to pandas Series with datetime index
        df_ts = pd.Series({date: rates_ts[date][to_currency] for date in sorted(rates_ts.keys())})
        df_ts.index = pd.to_datetime(df_ts.index)  # ✅ fix: convert index to datetime

        st.subheader("📈 Last 7 Days Rate Trend")
        fig, ax = plt.subplots()
        df_ts.plot(kind="line", marker="o", ax=ax)
        ax.set_ylabel(f"Rate ({to_currency} per {from_currency})")
        ax.set_xlabel("Date")
        ax.grid(True, alpha=0.3)

        # nicer x-axis labels
        ax.set_xticks(df_ts.index)
        ax.set_xticklabels(df_ts.index.strftime("%b %d"), rotation=45)

        st.pyplot(fig)

# --- Footer ---
st.markdown("---")
st.caption("Rates provided by [Frankfurter API](https://api.frankfurter.dev) — free, no API key required.")
