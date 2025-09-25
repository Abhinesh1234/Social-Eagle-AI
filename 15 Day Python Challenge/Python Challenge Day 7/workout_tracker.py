import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="🏋️ Gym Workout Logger", layout="wide")

st.title("🏋️ Gym Workout Logger")
st.caption("Log your sets, reps & weights — track weekly progress like a pro!")

# --- Initialize Session State ---
if "workout_log" not in st.session_state:
    st.session_state.workout_log = pd.DataFrame(
        columns=["Date", "Exercise", "Sets", "Reps", "Weight (kg)", "Total Volume"]
    )

# --- Sidebar Input Form ---
st.sidebar.header("➕ Add New Workout")
with st.sidebar.form("workout_form", clear_on_submit=True):
    exercise = st.text_input("Exercise Name", placeholder="e.g., Bench Press")
    sets = st.number_input("Sets", min_value=1, max_value=20, value=3)
    reps = st.number_input("Reps", min_value=1, max_value=100, value=10)
    weight = st.number_input("Weight (kg)", min_value=0.0, max_value=500.0, value=20.0, step=2.5)
    submitted = st.form_submit_button("Log Workout")

    if submitted and exercise:
        total_volume = sets * reps * weight
        new_entry = {
            "Date": datetime.now().strftime("%Y-%m-%d"),
            "Exercise": exercise.title(),
            "Sets": sets,
            "Reps": reps,
            "Weight (kg)": weight,
            "Total Volume": total_volume,
        }
        st.session_state.workout_log = pd.concat(
            [st.session_state.workout_log, pd.DataFrame([new_entry])],
            ignore_index=True
        )
        st.success(f"✅ Logged {exercise} - {sets}×{reps} @ {weight}kg")

# --- Show Workout History ---
st.subheader("📋 Workout History")
if not st.session_state.workout_log.empty:
    st.dataframe(st.session_state.workout_log, use_container_width=True)

    # Download Option
    csv = st.session_state.workout_log.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Download Log as CSV", data=csv, file_name="workout_log.csv", mime="text/csv")

    # --- Weekly Progress Visualization ---
    st.subheader("📈 Weekly Progress")
    df = st.session_state.workout_log.copy()
    df["Date"] = pd.to_datetime(df["Date"])
    df["Week"] = df["Date"].dt.strftime("%Y-%W")  # Year-Week format

    progress = df.groupby(["Week", "Exercise"])["Total Volume"].sum().reset_index()

    fig = px.bar(
        progress,
        x="Week",
        y="Total Volume",
        color="Exercise",
        barmode="group",
        title="Weekly Training Volume",
        text_auto=True
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No workouts logged yet. Use the sidebar to add your first workout! 💪")
