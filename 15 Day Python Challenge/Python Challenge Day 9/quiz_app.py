import streamlit as st

st.set_page_config(page_title="❓ Quiz Game", layout="centered")

st.title("❓ Quiz Game App")
st.caption("Test your knowledge with multiple-choice questions!")

# --- Hardcoded Questions ---
questions = [
    {
        "question": "What is the capital of France?",
        "options": ["Berlin", "Madrid", "Paris", "Rome"],
        "answer": "Paris"
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "options": ["Earth", "Mars", "Jupiter", "Saturn"],
        "answer": "Mars"
    },
    {
        "question": "Who wrote 'Hamlet'?",
        "options": ["Charles Dickens", "William Shakespeare", "Leo Tolstoy", "Mark Twain"],
        "answer": "William Shakespeare"
    },
    {
        "question": "Which gas do plants absorb for photosynthesis?",
        "options": ["Oxygen", "Carbon Dioxide", "Nitrogen", "Helium"],
        "answer": "Carbon Dioxide"
    }
]

# --- Session State Setup ---
if "q_index" not in st.session_state:
    st.session_state.q_index = 0
if "score" not in st.session_state:
    st.session_state.score = 0
if "answers" not in st.session_state:
    st.session_state.answers = []

# --- Game Logic ---
if st.session_state.q_index < len(questions):
    q = questions[st.session_state.q_index]
    st.subheader(f"Q{st.session_state.q_index+1}: {q['question']}")
    choice = st.radio("Choose an answer:", q["options"], key=f"q{st.session_state.q_index}")

    if st.button("Next"):
        st.session_state.answers.append(choice)
        if choice == q["answer"]:
            st.session_state.score += 1
        st.session_state.q_index += 1
        st.rerun()   # ✅ updated
else:
    st.success("🎉 Quiz Finished!")
    st.write(f"✅ Your Final Score: **{st.session_state.score}/{len(questions)}**")

    # Show review
    st.subheader("📋 Review")
    for i, q in enumerate(questions):
        user_ans = st.session_state.answers[i]
        correct = q["answer"]
        st.write(f"Q{i+1}: {q['question']}")
        st.write(f"👉 Your Answer: {user_ans}")
        st.write(f"✔️ Correct Answer: {correct}")
        st.markdown("---")

    if st.button("Restart Quiz"):
        st.session_state.q_index = 0
        st.session_state.score = 0
        st.session_state.answers = []
        st.rerun()   # ✅ updated
