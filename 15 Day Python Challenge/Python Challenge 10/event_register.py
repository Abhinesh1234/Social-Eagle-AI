import streamlit as st
import pandas as pd
import datetime
import os
import re
import plotly.express as px
import plotly.graph_objects as go

# -------------------- Config --------------------
st.set_page_config(page_title="🎉 Event Registration System", layout="wide")
CSV_PATH = "event_registrations.csv"
ADMIN_PASSCODE = "letmein"

# -------------------- Helpers --------------------
def init_storage():
    if "registrations" not in st.session_state:
        st.session_state.registrations = pd.DataFrame(
            columns=["Timestamp", "Name", "Email", "Event"]
        )
    # Load CSV once if present
    if os.path.exists(CSV_PATH) and not st.session_state.registrations.shape[0]:
        try:
            df = pd.read_csv(CSV_PATH)
            # ensure columns
            needed = ["Timestamp", "Name", "Email", "Event"]
            if all(col in df.columns for col in needed):
                st.session_state.registrations = df[needed].copy()
        except Exception:
            pass

def save_csv():
    if not st.session_state.registrations.empty:
        st.session_state.registrations.to_csv(CSV_PATH, index=False)

def valid_email(email: str) -> bool:
    # simple email pattern
    return bool(re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email.strip()))

def already_registered(email: str) -> bool:
    if st.session_state.registrations.empty:
        return False
    return email.strip().lower() in st.session_state.registrations["Email"].str.lower().values

def add_registration(name, email, event_choice):
    new_entry = {
        "Timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Name": name.strip(),
        "Email": email.strip(),
        "Event": event_choice
    }
    st.session_state.registrations = pd.concat(
        [st.session_state.registrations, pd.DataFrame([new_entry])],
        ignore_index=True
    )
    save_csv()

def event_counts_df():
    if st.session_state.registrations.empty:
        return pd.DataFrame(columns=["Event", "Count"])
    vc = st.session_state.registrations["Event"].value_counts().reset_index()
    vc.columns = ["Event", "Count"]
    return vc

def daily_trend_df():
    if st.session_state.registrations.empty:
        return pd.DataFrame(columns=["Date", "Count"])
    df = st.session_state.registrations.copy()
    df["Date"] = pd.to_datetime(df["Timestamp"]).dt.date
    trend = df.groupby("Date").size().reset_index(name="Count")
    return trend

# -------------------- App Title --------------------
st.title("🎉 Event Registration System")
st.caption("Left: Register users · Right: Live stats for organizers")

init_storage()

# -------------------- Layout: Two Columns --------------------
left, right = st.columns(2, gap="large")

# -------------------- LEFT: User Registration --------------------
with left:
    st.subheader("📝 Register Now")
    st.markdown("Fill in your details and choose your event. You’ll see your spot reflected instantly in the live stats ➡️")

    with st.form("reg_form", clear_on_submit=True):
        name = st.text_input("Full Name", placeholder="e.g., Priya Kumar")
        email = st.text_input("Email Address", placeholder="e.g., priya@example.com")
        event_choice = st.selectbox(
            "Select Event",
            ["Tech Talk 💻", "Workshop 🛠️", "Music Night 🎶", "Startup Pitch 🚀"],
            index=0
        )
        agree = st.checkbox("I confirm my details are correct")
        submitted = st.form_submit_button("Register 🎟️")

        if submitted:
            # validations
            if not name.strip():
                st.error("Please enter your name.")
            elif not email.strip():
                st.error("Please enter your email.")
            elif not valid_email(email):
                st.error("Please enter a valid email (e.g., name@example.com).")
            elif already_registered(email):
                st.warning("This email has already registered. Duplicate registration is not allowed.")
            elif not agree:
                st.info("Please confirm your details are correct.")
            else:
                add_registration(name, email, event_choice)
                st.success(f"✅ Registered **{name}** for **{event_choice}**")
                st.balloons()

    # Quick glance card
    total_regs = len(st.session_state.registrations)
    st.markdown("### 🎟️ Quick Glance")
    st.metric("Total Registrations", total_regs)

# -------------------- RIGHT: Admin / Organizer Statistics --------------------
with right:
    st.subheader("📊 Admin / Organizer Panel")

    with st.expander("🔐 Admin Controls", expanded=True):
        admin_pass = st.text_input("Enter admin passcode to enable actions (export/clear):", type="password")
        admin_unlocked = (admin_pass == ADMIN_PASSCODE)
        if admin_unlocked:
            st.success("Admin actions unlocked.")
        else:
            st.info("Enter the passcode to unlock Export / Clear actions.")

    # Live totals
    total_regs = len(st.session_state.registrations)
    colA, colB = st.columns(2)
    with colA:
        st.metric("Total Registrations", total_regs)
    with colB:
        unique_events = st.session_state.registrations["Event"].nunique() if total_regs else 0
        st.metric("Active Events", unique_events)

    # Per-event breakdown: progress + bar chart
    counts = event_counts_df()
    if total_regs > 0:
        st.markdown("#### 📌 Per-Event Breakdown")
        for _, row in counts.iterrows():
            st.write(f"**{row['Event']}** — {row['Count']} registrations")
            st.progress(row["Count"] / total_regs)

        # Plotly bar
        fig_bar = px.bar(
            counts,
            x="Event",
            y="Count",
            title="Registrations by Event",
            text="Count"
        )
        fig_bar.update_traces(textposition="outside")
        fig_bar.update_layout(yaxis_title="Count", xaxis_title="", margin=dict(t=60, b=20))
        st.plotly_chart(fig_bar, use_container_width=True)

        # Daily trend line
        st.markdown("#### 📈 Daily Registration Trend")
        trend = daily_trend_df()
        if not trend.empty:
            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(x=trend["Date"], y=trend["Count"], mode="lines+markers", name="Registrations"))
            fig_line.update_layout(xaxis_title="Date", yaxis_title="Count", margin=dict(t=40, b=20))
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("No trend yet—start registering to see the curve!")

        # Top event highlight
        top_row = counts.sort_values("Count", ascending=False).iloc[0]
        st.success(f"🏆 Most Popular: **{top_row['Event']}** with **{top_row['Count']}** registrations")

    else:
        st.info("No registrations yet. Stats will appear here as people register.")

    st.markdown("---")

    # Export + Danger Zone (only if unlocked)
    if total_regs > 0:
        csv = st.session_state.registrations.to_csv(index=False).encode("utf-8")
        st.download_button(
            "⬇️ Download CSV (All Registrations)",
            data=csv,
            file_name="event_registrations.csv",
            mime="text/csv",
            disabled=not admin_unlocked,
            help=None if admin_unlocked else "Enter admin passcode to enable"
        )

    # Danger zone
    st.markdown("### ⚠️ Danger Zone")
    if st.button("Clear ALL registrations", type="primary", disabled=not admin_unlocked):
        st.session_state.registrations = st.session_state.registrations.iloc[0:0]
        # also clear CSV
        if os.path.exists(CSV_PATH):
            try:
                os.remove(CSV_PATH)
            except Exception:
                pass
        st.warning("All registrations cleared.")
        st.rerun()
