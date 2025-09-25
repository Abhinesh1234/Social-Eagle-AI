import streamlit as st
import random
from typing import List, Optional, Tuple

st.set_page_config(page_title="❌⭕ Tic-Tac-Toe", layout="centered")

# -------------------- Helpers --------------------
WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),        # rows
    (0, 3, 6), (1, 4, 7), (2, 5, 8),        # cols
    (0, 4, 8), (2, 4, 6)                    # diagonals
]

def check_winner(board: List[str]) -> Tuple[Optional[str], Optional[Tuple[int,int,int]]]:
    """Return ('X' or 'O', winning_triplet) or (None, None)."""
    for a, b, c in WIN_LINES:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a], (a, b, c)
    return None, None

def board_full(board: List[str]) -> bool:
    return all(v != "" for v in board)

def available_moves(board: List[str]) -> List[int]:
    return [i for i, v in enumerate(board) if v == ""]

def place_move(idx: int):
    """Place current player's symbol at idx, then evaluate and advance turn."""
    if st.session_state.game_over or st.session_state.board[idx] != "":
        return
    st.session_state.board[idx] = st.session_state.current

    winner, line = check_winner(st.session_state.board)
    if winner:
        st.session_state.winner = winner
        st.session_state.winning_line = line
        st.session_state.game_over = True
        st.session_state.scores[winner] += 1
        st.balloons()
        return
    if board_full(st.session_state.board):
        st.session_state.game_over = True
        st.session_state.winner = None
        st.session_state.winning_line = None
        return

    # Switch turn
    st.session_state.current = "O" if st.session_state.current == "X" else "X"

def computer_move_random():
    """Random move for computer if it's computer's turn."""
    if st.session_state.mode != "Vs Computer (Random)":
        return
    if st.session_state.game_over or st.session_state.current != st.session_state.computer_symbol:
        return
    moves = available_moves(st.session_state.board)
    if not moves:
        return
    idx = random.choice(moves)
    place_move(idx)

def reset_board(hard: bool = False):
    st.session_state.board = [""] * 9
    st.session_state.current = "X"
    st.session_state.game_over = False
    st.session_state.winner = None
    st.session_state.winning_line = None
    if hard:
        st.session_state.scores = {"X": 0, "O": 0}

# -------------------- Session State --------------------
if "board" not in st.session_state:
    st.session_state.board = [""] * 9
if "current" not in st.session_state:
    st.session_state.current = "X"
if "game_over" not in st.session_state:
    st.session_state.game_over = False
if "winner" not in st.session_state:
    st.session_state.winner = None
if "winning_line" not in st.session_state:
    st.session_state.winning_line = None
if "scores" not in st.session_state:
    st.session_state.scores = {"X": 0, "O": 0}
if "mode" not in st.session_state:
    st.session_state.mode = "Two-Player"
if "computer_symbol" not in st.session_state:
    st.session_state.computer_symbol = "O"

# -------------------- UI: Header --------------------
st.title("❌⭕ Tic-Tac-Toe")
st.caption("Play with a friend or vs a random computer. Highlighted line shows who won!")

# -------------------- Sidebar Controls --------------------
with st.sidebar:
    st.header("⚙️ Settings")
    mode = st.radio("Mode", ["Two-Player", "Vs Computer (Random)"], index=0)
    if mode != st.session_state.mode:
        st.session_state.mode = mode
        reset_board()
        st.rerun()

    if st.session_state.mode == "Vs Computer (Random)":
        st.write("Who should the computer be?")
        comp = st.radio("Computer plays as", ["O", "X"], index=0, horizontal=True)
        if comp != st.session_state.computer_symbol:
            st.session_state.computer_symbol = comp
            reset_board()
            st.rerun()

    st.markdown("---")
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        if st.button("🔁 Reset Round"):
            reset_board()
            st.rerun()
    with col_sb2:
        if st.button("🧹 Reset Scores"):
            reset_board(hard=True)
            st.rerun()

    st.markdown("---")
    st.subheader("📊 Scoreboard")
    col_s1, col_s2 = st.columns(2)
    col_s1.metric("X", st.session_state.scores["X"])
    col_s2.metric("O", st.session_state.scores["O"])

# -------------------- Turn / Status Bar --------------------
turn_text = f"Turn: **{st.session_state.current}**"
if st.session_state.mode == "Vs Computer (Random)" and st.session_state.current == st.session_state.computer_symbol and not st.session_state.game_over:
    turn_text += " — 🤖 thinking..."
st.markdown(f"### {turn_text}")

# Progress toward end (0..9 moves)
moves_played = 9 - len(available_moves(st.session_state.board))
st.progress(moves_played / 9)

# -------------------- Board Buttons --------------------
def cell_label(v: str) -> str:
    return " " if v == "" else v

# 3x3 grid using columns
for row in range(3):
    c1, c2, c3 = st.columns(3, gap="small")
    for col, idx in zip((c1, c2, c3), range(row * 3, row * 3 + 3)):
        with col:
            disabled = (st.session_state.board[idx] != "") or st.session_state.game_over or \
                       (st.session_state.mode == "Vs Computer (Random)" and st.session_state.current == st.session_state.computer_symbol)
            if st.button(cell_label(st.session_state.board[idx]), key=f"cell_{idx}", use_container_width=True, disabled=disabled):
                place_move(idx)
                st.rerun()

# -------------------- Winning Highlight Board (visual overlay) --------------------
def render_highlight_board():
    """Emoji board highlighting winning cells."""
    win = set(st.session_state.winning_line) if st.session_state.winning_line else set()
    emoji_map = {
        "": "⬜️",
        "X": "❌",
        "O": "⭕"
    }
    # Winning tiles become green squares behind the symbol
    for r in range(3):
        colA, colB, colC = st.columns(3)
        for col, idx in zip((colA, colB, colC), range(r * 3, r * 3 + 3)):
            with col:
                symbol = emoji_map[st.session_state.board[idx]]
                if idx in win:
                    st.markdown(f"<div style='text-align:center;font-size:28px'>🟩 {symbol}</div>", unsafe_allow_html=True)
                else:
                    st.markdown(f"<div style='text-align:center;font-size:28px'>{symbol}</div>", unsafe_allow_html=True)

# -------------------- Game State Messages --------------------
st.markdown("---")
if st.session_state.game_over:
    if st.session_state.winner:
        st.success(f"🏆 **{st.session_state.winner}** wins!")
        render_highlight_board()
    else:
        st.info("🤝 It's a draw!")
else:
    st.caption("Click a cell to play your move.")

# -------------------- Computer Turn (if any) --------------------
# Trigger computer move after rendering (so user sees state change nicely)
if (not st.session_state.game_over and
    st.session_state.mode == "Vs Computer (Random)" and
    st.session_state.current == st.session_state.computer_symbol):
    computer_move_random()
    if st.session_state.game_over:
        st.rerun()
    else:
        st.rerun()

# -------------------- Footer --------------------
st.markdown("---")
st.caption("Tip: Use the sidebar to switch modes, reset the round, or clear scores.")
