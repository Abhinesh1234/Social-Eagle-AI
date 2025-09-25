import streamlit as st
import random
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="🪨📄✂️ Rock • Paper • Scissors", layout="wide")

# -------------------- Setup --------------------
CHOICES = {
    "Rock ✊": "rock",
    "Paper ✋": "paper",
    "Scissors ✌️": "scissors",
}
EMOJI_FOR = {"rock": "✊", "paper": "✋", "scissors": "✌️"}

RULES = {
    ("rock", "scissors"): "win",
    ("paper", "rock"): "win",
    ("scissors", "paper"): "win",
    ("scissors", "rock"): "lose",
    ("rock", "paper"): "lose",
    ("paper", "scissors"): "lose",
}

# -------------------- State --------------------
def init_state():
    if "score" not in st.session_state:
        st.session_state.score = {"win": 0, "lose": 0, "draw": 0}
    if "streak" not in st.session_state:
        st.session_state.streak = {"type": None, "count": 0}
    if "history" not in st.session_state:
        st.session_state.history = pd.DataFrame(columns=["Time", "You", "Computer", "Result"])
    if "last_result" not in st.session_state:
        st.session_state.last_result = None

init_state()

# -------------------- Helpers --------------------
def judge(user, comp):
    if user == comp:
        return "draw"
    return RULES.get((user, comp), "lose" if RULES.get((comp, user)) == "win" else "draw")

def update_streak(outcome):
    t = st.session_state.streak["type"]
    c = st.session_state.streak["count"]
    if outcome == "draw":
        # draws break a streak
        st.session_state.streak = {"type": None, "count": 0}
    else:
        if t == outcome:
            st.session_state.streak["count"] = c + 1
        else:
            st.session_state.streak = {"type": outcome, "count": 1}

def record_game(user_choice, comp_choice, result):
    row = {
        "Time": datetime.now().strftime("%H:%M:%S"),
        "You": user_choice,
        "Computer": comp_choice,
        "Result": result.capitalize(),
    }
    st.session_state.history = pd.concat([st.session_state.history, pd.DataFrame([row])], ignore_index=True)

def reset_rounds(hard=False):
    st.session_state.history = st.session_state.history.iloc[0:0]
    st.session_state.score = {"win": 0, "lose": 0, "draw": 0}
    st.session_state.last_result = None
    st.session_state.streak = {"type": None, "count": 0}
    if hard:
        # nothing extra now, reserved for future profile reset
        pass

# -------------------- Header --------------------
st.title("🪨📄✂️ Rock • Paper • Scissors")
st.caption("Pick your move, see the computer respond, and keep score!")

left, right = st.columns([7, 5], gap="large")

# -------------------- LEFT: Play Area --------------------
with left:
    st.subheader("🎮 Make Your Move")
    c1, c2, c3 = st.columns(3)
    clicked = None
    with c1:
        if st.button("✊ Rock", use_container_width=True):
            clicked = "rock"
    with c2:
        if st.button("✋ Paper", use_container_width=True):
            clicked = "paper"
    with c3:
        if st.button("✌️ Scissors", use_container_width=True):
            clicked = "scissors"

    if clicked:
        comp = random.choice(list(EMOJI_FOR.keys()))
        result = judge(clicked, comp)
        st.session_state.score[result] += 1
        update_streak(result)
        st.session_state.last_result = (clicked, comp, result)
        record_game(clicked, comp, result)
        if result == "win":
            st.balloons()

    # Show last round outcome
    st.markdown("---")
    st.subheader("🔎 Last Round")
    if st.session_state.last_result:
        u, c, r = st.session_state.last_result
        emoji_u = EMOJI_FOR[u]
        emoji_c = EMOJI_FOR[c]
        badge = {"win": "🏆 **You Win!**", "lose": "😵 **You Lose!**", "draw": "🤝 **Draw!**"}[r]
        st.markdown(f"**You:** {emoji_u}  vs  **Computer:** {emoji_c}")
        if r == "win":
            st.success(badge)
        elif r == "lose":
            st.error(badge)
        else:
            st.info(badge)
    else:
        st.caption("No moves yet — choose Rock, Paper, or Scissors above.")

    # Quick tips
    with st.expander("💡 Game Rules"):
        st.write("- Rock beats Scissors")
        st.write("- Paper beats Rock")
        st.write("- Scissors beats Paper")
        st.write("- Same move = Draw")

# -------------------- RIGHT: Score & Analytics --------------------
with right:
    st.subheader("📊 Scoreboard")
    col_a, col_b, col_c = st.columns(3)
    col_a.metric("Wins", st.session_state.score["win"])
    col_b.metric("Losses", st.session_state.score["lose"])
    col_c.metric("Draws", st.session_state.score["draw"])

    # Streak
    t = st.session_state.streak["type"]
    c = st.session_state.streak["count"]
    if t and c > 1:
        st.success(f"🔥 Streak: {c} {t.upper()}s in a row")
    elif t and c == 1:
        st.info(f"Streak started: 1 {t.upper()}")

    st.markdown("---")
    st.subheader("📜 Match History")
    if not st.session_state.history.empty:
        st.dataframe(st.session_state.history, use_container_width=True, height=260)

        # Download CSV
        csv_bytes = st.session_state.history.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download History (CSV)", data=csv_bytes, file_name="rps_history.csv", mime="text/csv")

        # Analytics pie
        st.markdown("#### 📈 Results Breakdown")
        counts = st.session_state.history["Result"].value_counts().reset_index()
        counts.columns = ["Result", "Count"]
        fig = px.pie(counts, names="Result", values="Count", title="Win/Lose/Draw Share", hole=0.35)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Play at least one round to see history & analytics.")

    st.markdown("---")
    col_r1, col_r2 = st.columns(2)
    if col_r1.button("🔁 Reset Score & History", type="primary"):
        reset_rounds()
        st.rerun()
    if col_r2.button("🎲 Play Random Round"):
        # one-click random play for quick testing
        clicked = random.choice(["rock", "paper", "scissors"])
        comp = random.choice(list(EMOJI_FOR.keys()))
        result = judge(clicked, comp)
        st.session_state.score[result] += 1
        update_streak(result)
        st.session_state.last_result = (clicked, comp, result)
        record_game(clicked, comp, result)
        st.rerun()

# -------------------- Footer --------------------
st.markdown("---")
st.caption("Tip: Use the right panel to download your match history and view results analytics.")
