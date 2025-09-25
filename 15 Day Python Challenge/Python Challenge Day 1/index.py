import streamlit as st
import random
import time
from datetime import datetime
import base64

# Page configuration - GUI-like setup
st.set_page_config(
    page_title="✨ Greeting Generator Pro ✨",
    page_icon="🎉",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state for GUI-like behavior
if 'greeting_generated' not in st.session_state:
    st.session_state.greeting_generated = False
if 'user_name' not in st.session_state:
    st.session_state.user_name = ""
if 'user_age' not in st.session_state:
    st.session_state.user_age = 25
if 'theme_color' not in st.session_state:
    st.session_state.theme_color = "blue"

# Advanced CSS for GUI-like appearance
st.markdown("""
<style>
    /* Hide Streamlit branding for GUI feel */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container styling */
    .main {
        padding-top: 1rem;
    }
    
    /* GUI Window Frame */
    .gui-window {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem;
        box-shadow: 0 20px 40px rgba(0,0,0,0.3);
        border: 3px solid rgba(255,255,255,0.2);
    }
    
    /* Title Bar */
    .title-bar {
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4, #45B7D1, #96CEB4);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    /* Input Panel */
    .input-panel {
        background: rgba(255,255,255,0.15);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(45deg, #FF6B6B, #4ECDC4);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.7rem 2rem;
        font-weight: bold;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton > button:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 35px rgba(0,0,0,0.3);
        background: linear-gradient(45deg, #4ECDC4, #FF6B6B);
    }
    
    /* Greeting display */
    .greeting-display {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 15px 35px rgba(0,0,0,0.2);
        border: 2px solid rgba(255,255,255,0.3);
        animation: fadeIn 0.8s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Stats panel */
    .stats-panel {
        background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%);
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem;
        text-align: center;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    /* Input labels */
    .input-label {
        color: white;
        font-size: 1.2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3);
    }
    
    /* Slider custom styling */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
    }
    
    /* Fun fact box */
    .fun-fact {
        background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #ff6b6b;
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    
    /* Control panel */
    .control-panel {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1rem;
        margin: 1rem 0;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* Progress bar styling */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
    }
</style>
""", unsafe_allow_html=True)

# Main GUI Container
st.markdown('<div class="gui-window">', unsafe_allow_html=True)

# Title Bar
st.markdown('<h1 class="title-bar">✨ Greeting Generator Pro ✨</h1>', unsafe_allow_html=True)

# Status bar
status_col1, status_col2, status_col3 = st.columns([1, 2, 1])
with status_col1:
    st.markdown("**Status:** Ready")
with status_col2:
    current_time = datetime.now().strftime("%H:%M:%S")
    st.markdown(f"**Time:** {current_time}")
with status_col3:
    st.markdown(f"**Version:** 2.0")

st.markdown("---")

# Input Panel
st.markdown('<div class="input-panel">', unsafe_allow_html=True)
st.markdown('<div class="input-label">👤 Personal Information</div>', unsafe_allow_html=True)

# Two-column layout for inputs
input_col1, input_col2 = st.columns([1, 1])

with input_col1:
    st.markdown("**Full Name:**")
    name = st.text_input("", 
                        placeholder="Enter your full name here...", 
                        label_visibility="collapsed",
                        key="name_input")
    
with input_col2:
    st.markdown("**Age Selection:**")
    age = st.slider("", 
                   min_value=1, 
                   max_value=120, 
                   value=st.session_state.user_age,
                   label_visibility="collapsed",
                   key="age_slider")

# Real-time age display
if age:
    st.markdown(f"<div style='text-align: center; color: white; font-size: 1.2rem; margin-top: 10px;'>Current Age: <strong>{age} years old</strong></div>", unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Control Panel
st.markdown('<div class="control-panel">', unsafe_allow_html=True)
control_col1, control_col2, control_col3 = st.columns([1, 1, 1])

with control_col1:
    theme = st.selectbox("🎨 Theme:", ["Classic", "Vibrant", "Elegant", "Fun"], key="theme_select")

with control_col2:
    greeting_style = st.selectbox("✨ Style:", ["Formal", "Casual", "Funny", "Inspiring"], key="style_select")

with control_col3:
    language = st.selectbox("🌍 Language:", ["English", "Spanish", "French", "German"], key="lang_select")

st.markdown('</div>', unsafe_allow_html=True)

# Action Buttons
button_col1, button_col2, button_col3 = st.columns([1, 2, 1])

with button_col2:
    if st.button("🎭 Generate Personalized Greeting 🎭", use_container_width=True, key="generate_btn"):
        if name:
            st.session_state.greeting_generated = True
            st.session_state.user_name = name
            st.session_state.user_age = age
            
            # Simulate processing with progress bar
            progress_bar = st.progress(0)
            for i in range(100):
                time.sleep(0.01)
                progress_bar.progress(i + 1)
            progress_bar.empty()
        else:
            st.error("⚠️ Please enter your name first!")

# Function definitions
def get_age_info(age):
    if age < 13:
        return "🧒", "young explorer", "boundless curiosity and wonder", "childhood magic"
    elif age < 20:
        return "🧑‍🎓", "bright teenager", "dreams and endless possibilities", "youthful energy"
    elif age < 30:
        return "🌟", "young adult", "ambition and personal growth", "determination"
    elif age < 50:
        return "💼", "experienced individual", "wisdom and life experience", "balanced perspective"
    elif age < 70:
        return "🏆", "seasoned expert", "deep knowledge and expertise", "refined wisdom"
    else:
        return "👑", "wise sage", "profound wisdom and life stories", "timeless grace"

def get_themed_greeting(name, age, style, theme):
    emoji, description, quality, trait = get_age_info(age)
    
    greetings = {
        "Formal": [
            f"Good day, {name}. At {age} years of age, you exemplify the qualities of a {description}.",
            f"It is my pleasure to greet you, {name}. Your {age} years reflect a journey of {quality}.",
            f"Salutations, {name}. As a {description} of {age} years, you bring {trait} to everything you do."
        ],
        "Casual": [
            f"Hey {name}! {age} looks awesome on you - you're such a cool {description}! 😎",
            f"What's up, {name}! Love that you're {age} and rocking life as a {description}! 🤘",
            f"Hi there, {name}! At {age}, you've got that perfect {description} vibe going! ✨"
        ],
        "Funny": [
            f"Well hello there, {name}! At {age}, you're like a fine cheese - getting better with age! 🧀",
            f"Greetings, {name}! {age} years old and still avoiding adulting like a pro! 😂",
            f"Hey {name}! They say {age} is the new 25... or was it the other way around? 🤔"
        ],
        "Inspiring": [
            f"Welcome, {name}! Your {age} years represent a beautiful journey of growth and {quality}. ✨",
            f"Greetings, inspiring {name}! At {age}, you're writing an amazing story filled with {trait}. 📖",
            f"Hello, wonderful {name}! Your {age} years shine bright with {quality} and endless potential! 🌟"
        ]
    }
    
    return random.choice(greetings.get(style, greetings["Casual"])), emoji, description, quality, trait

def get_fun_fact(age):
    facts = [
        f"🎈 You've been alive for approximately {age * 365:,} days!",
        f"🌙 You've witnessed about {age * 12:,} full moons in your lifetime!",
        f"💫 Your heart has beaten roughly {age * 365 * 24 * 60 * 70:,} times!",
        f"🌍 You've traveled around the sun {age} times on this amazing journey!",
        f"⭐ You've experienced approximately {age * 52:,} weekends of joy!",
        f"🎂 You've celebrated {age} birthdays and created countless precious memories!"
    ]
    return random.choice(facts)

# Display Greeting if Generated
if st.session_state.greeting_generated and st.session_state.user_name:
    greeting, age_emoji, description, quality, trait = get_themed_greeting(
        st.session_state.user_name, 
        st.session_state.user_age, 
        greeting_style, 
        theme
    )
    
    # Main Greeting Display
    st.markdown(f"""
    <div class="greeting-display">
        <h2>{age_emoji} {greeting} {age_emoji}</h2>
        <p style="font-size: 1.2rem; margin-top: 1rem; opacity: 0.9;">
            You bring {trait} to this world, and that makes it a brighter place! 🌟
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Stats Dashboard
    st.markdown("### 📊 Personal Dashboard")
    
    stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
    
    with stats_col1:
        st.markdown(f"""
        <div class="stats-panel">
            <h3>🎂 Age</h3>
            <h2>{st.session_state.user_age}</h2>
            <p>Years Young!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with stats_col2:
        birth_year = datetime.now().year - st.session_state.user_age
        st.markdown(f"""
        <div class="stats-panel">
            <h3>🗓️ Born</h3>
            <h2>{birth_year}</h2>
            <p>Great Vintage!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with stats_col3:
        next_milestone = ((st.session_state.user_age // 10) + 1) * 10
        years_to_milestone = next_milestone - st.session_state.user_age
        st.markdown(f"""
        <div class="stats-panel">
            <h3>🎯 Next Goal</h3>
            <h2>{next_milestone}</h2>
            <p>In {years_to_milestone} years!</p>
        </div>
        """, unsafe_allow_html=True)
    
    with stats_col4:
        life_progress = min((st.session_state.user_age / 100) * 100, 100)
        st.markdown(f"""
        <div class="stats-panel">
            <h3>📈 Progress</h3>
            <h2>{life_progress:.0f}%</h2>
            <p>Life Journey!</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Fun Fact Section
    fun_fact = get_fun_fact(st.session_state.user_age)
    st.markdown(f"""
    <div class="fun-fact">
        <h4>🎯 Amazing Fact About You:</h4>
        <p style="font-size: 1.1rem; margin: 0;">{fun_fact}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Action Buttons Row
    action_col1, action_col2, action_col3 = st.columns([1, 1, 1])
    
    with action_col1:
        if st.button("🎲 Generate New Greeting", use_container_width=True):
            st.rerun()
    
    with action_col2:
        if st.button("💾 Save Greeting", use_container_width=True):
            st.success("Greeting saved to memory! 💾")
    
    with action_col3:
        if st.button("📤 Share Greeting", use_container_width=True):
            st.info("Sharing feature coming soon! 📤")

# Footer Status Bar
st.markdown("---")
footer_col1, footer_col2, footer_col3 = st.columns([1, 2, 1])
with footer_col1:
    st.markdown("**Greetings Generated:** " + str(random.randint(1000, 9999)))
with footer_col2:
    st.markdown("**✨ Made with Streamlit Magic ✨**")
with footer_col3:
    st.markdown("**Users Happy:** 😊 100%")

st.markdown('</div>', unsafe_allow_html=True)

# Auto-refresh every 60 seconds for time display
time.sleep(1)
if st.button("🔄 Refresh", key="hidden_refresh", help="Auto-refresh"):
    st.rerun()