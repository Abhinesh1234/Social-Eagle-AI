import streamlit as st
from time import perf_counter
import math
import pandas as pd

st.set_page_config(page_title="⏱️ Stopwatch", layout="wide")

# ---- Optional autorefresh (for smooth ticking) ----
# If you install: pip install streamlit-autorefresh
AUTOREFRESH_OK = False
try:
    from streamlit_autorefresh import st_autorefresh
    # refresh every 200ms while the app is open
    st_autorefresh(interval=200, key="tick")
    AUTOREFRESH_OK = True
except Exception:
    pass

# ---------------- Session State ----------------
def _init():
    ss = st.session_state
    ss.setdefault("running", False)            # is stopwatch running?
    ss.setdefault("start_t", None)             # perf_counter() when started
    ss.setdefault("elapsed_fixed", 0.0)        # accumulated time when stopped
    ss.setdefault("laps", [])                  # list of (lap_no, lap_time, delta)
_init()

# ---------------- Helpers ----------------
def now_elapsed() -> float:
    """Current total elapsed time (seconds)."""
    if st.session_state.running and st.session_state.start_t is not None:
        return st.session_state.elapsed_fixed + (perf_counter() - st.session_state.start_t)
    return st.session_state.elapsed_fixed

def fmt(t: float) -> str:
    """Format seconds -> HH:MM:SS.mmm"""
    t = max(0.0, t)
    hours = int(t // 3600)
    minutes = int((t % 3600) // 60)
    seconds = int(t % 60)
    millis = int((t - math.floor(t)) * 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{millis:03d}"

def start():
    if not st.session_state.running:
        st.session_state.running = True
        st.session_state.start_t = perf_counter()

def stop():
    if st.session_state.running:
        st.session_state.elapsed_fixed = now_elapsed()
        st.session_state.running = False
        st.session_state.start_t = None

def reset():
    st.session_state.running = False
    st.session_state.start_t = None
    st.session_state.elapsed_fixed = 0.0
    st.session_state.laps = []

def lap():
    t = now_elapsed()
    laps = st.session_state.laps
    if laps:
        delta = t - laps[-1][1]
    else:
        delta = t
    laps.append((len(laps) + 1, t, delta))

# ---------------- UI ----------------
st.title("⏱️ Stopwatch")
st.caption("Start • Stop • Reset — record laps and export them as CSV.")

left, right = st.columns([7, 5], gap="large")

# -------- LEFT: Big Timer & Progress --------
with left:
    # Big display
    elapsed = now_elapsed()
    big = fmt(elapsed)
    st.markdown(
        f"""
        <div style="
            font-size: 64px; 
            font-weight: 800; 
            letter-spacing: 2px; 
            padding: 12px 16px; 
            border-radius: 16px; 
            background: rgba(255,255,255,0.05); 
            border: 1px solid rgba(255,255,255,0.1);
            text-align:center;">
            {big}
        </div>
        """,
        unsafe_allow_html=True
    )

    # Seconds progress (how far into the current minute)
    sec_in_min = (elapsed % 60.0) / 60.0
    st.progress(min(1.0, sec_in_min))

    # Status chip
    if st.session_state.running:
        st.success("● Running")
    else:
        st.info("■ Stopped")

# -------- RIGHT: Controls & Laps --------
with right:
    st.subheader("🎛️ Controls")

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("▶️ Start", use_container_width=True):
            start()
            st.rerun()
    with c2:
        if st.button("⏸️ Stop", use_container_width=True):
            stop()
            st.rerun()
    with c3:
        if st.button("🔁 Reset", use_container_width=True):
            reset()
            st.rerun()
    with c4:
        if st.button("🏁 Lap", use_container_width=True, disabled=not st.session_state.running):
            lap()
            st.rerun()

    st.markdown("---")
    st.subheader("🏷️ Laps")
    if st.session_state.laps:
        df = pd.DataFrame(st.session_state.laps, columns=["Lap #", "Elapsed (s)", "Lap Delta (s)"])
        # Also show pretty time strings
        df_display = df.copy()
        df_display["Elapsed"] = df_display["Elapsed (s)"].map(fmt)
        df_display["Delta"] = df_display["Lap Delta (s)"].map(fmt)
        df_display = df_display[["Lap #", "Elapsed", "Delta"]]
        st.dataframe(df_display, use_container_width=True, height=260)

        # Export
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        st.download_button("⬇️ Download Laps (CSV)", data=csv_bytes,
                           file_name="laps.csv", mime="text/csv")
    else:
        st.info("No laps yet — press **Lap** while running to record one.")

st.markdown("---")
if AUTOREFRESH_OK:
    st.caption("Live update: **ON** (via streamlit-autorefresh).")
else:
    st.caption("Tip: install `streamlit-autorefresh` for live ticking → `pip install streamlit-autorefresh`.")
