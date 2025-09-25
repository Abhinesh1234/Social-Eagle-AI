import streamlit as st
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date, time
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import calendar

# Optional imports with fallbacks
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("📊 Install plotly for advanced visualizations: pip install plotly")

# Page configuration
st.set_page_config(
    page_title="💧 Hydration & Wellness Dashboard",
    page_icon="💧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for water-themed design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #74b9ff 0%, #0984e3 50%, #00b894 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #0984e3;
        margin-bottom: 2rem;
        font-style: italic;
    }
    
    .water-card {
        background: linear-gradient(135deg, #74b9ff, #0984e3);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
        box-shadow: 0 10px 40px rgba(116, 185, 255, 0.3);
        transition: transform 0.3s ease;
    }
    
    .water-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(116, 185, 255, 0.4);
    }
    
    .progress-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 2px solid #e3f2fd;
        transition: transform 0.3s ease;
    }
    
    .progress-card:hover {
        transform: translateY(-3px);
        border-color: #74b9ff;
    }
    
    .hydration-display {
        background: linear-gradient(135deg, #e3f2fd, #bbdefb);
        color: #0d47a1;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin: 1rem 0;
        border: 3px solid #74b9ff;
        position: relative;
        overflow: hidden;
    }
    
    .hydration-display::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
        animation: wave 3s infinite;
    }
    
    @keyframes wave {
        0% { left: -100%; }
        100% { left: 100%; }
    }
    
    .intake-value {
        font-size: 3rem;
        font-weight: 800;
        margin: 0.5rem 0;
        text-shadow: 0 2px 4px rgba(13, 71, 161, 0.2);
    }
    
    .goal-text {
        font-size: 1.2rem;
        opacity: 0.8;
        margin-top: 0.5rem;
    }
    
    .quick-add-btn {
        background: linear-gradient(135deg, #00b894, #00a085);
        color: white;
        border: none;
        padding: 1rem 1.5rem;
        border-radius: 15px;
        margin: 0.5rem;
        cursor: pointer;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(0, 184, 148, 0.3);
    }
    
    .quick-add-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 184, 148, 0.4);
    }
    
    .container-btn {
        background: linear-gradient(135deg, #fdcb6e, #e17055);
        color: white;
        border: none;
        padding: 1rem;
        border-radius: 12px;
        margin: 0.3rem;
        cursor: pointer;
        transition: transform 0.2s ease;
        font-weight: 500;
        min-width: 80px;
    }
    
    .container-btn:hover {
        transform: scale(1.05);
    }
    
    .achievement-badge {
        background: linear-gradient(135deg, #ffd700, #ffb347);
        color: #8b4513;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-weight: 600;
        margin: 0.3rem;
        display: inline-block;
        box-shadow: 0 2px 10px rgba(255, 215, 0, 0.3);
        animation: glow 2s infinite alternate;
    }
    
    @keyframes glow {
        from { box-shadow: 0 2px 10px rgba(255, 215, 0, 0.3); }
        to { box-shadow: 0 4px 20px rgba(255, 215, 0, 0.6); }
    }
    
    .streak-counter {
        background: linear-gradient(135deg, #e84393, #fd79a8);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 6px 25px rgba(232, 67, 147, 0.3);
    }
    
    .tip-card {
        background: linear-gradient(135deg, #a8e6cf, #7fcdcd);
        color: #2c3e50;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        border-left: 5px solid #00b894;
    }
    
    .warning-card {
        background: linear-gradient(135deg, #ff9f43, #ee5a24);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(238, 90, 36, 0.3);
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .stat-item {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        border-top: 4px solid #74b9ff;
    }
    
    .stat-value {
        font-size: 2rem;
        font-weight: 700;
        color: #0984e3;
    }
    
    .stat-label {
        color: #666;
        margin-top: 0.5rem;
        font-weight: 500;
    }
    
    /* Animated water wave effect */
    .water-wave {
        background: linear-gradient(135deg, #74b9ff, #0984e3);
        position: relative;
        overflow: hidden;
    }
    
    .water-wave::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1000 100'%3E%3Cpath d='M0,50 Q250,0 500,50 T1000,50 L1000,100 L0,100 Z' fill='rgba(255,255,255,0.1)'/%3E%3C/svg%3E");
        background-size: 1000px 100px;
        animation: wave-animation 8s linear infinite;
    }
    
    @keyframes wave-animation {
        0% { background-position-x: 0; }
        100% { background-position-x: 1000px; }
    }
    
    /* Progress bar animations */
    .animated-progress {
        transition: width 1s ease-in-out;
    }
    
    /* Fade in animation */
    .fade-in {
        animation: fadeIn 0.8s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    /* Container type icons */
    .container-icon {
        font-size: 1.5rem;
        margin-right: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

@dataclass
class WaterIntake:
    """Data class for water intake records"""
    timestamp: str
    amount_ml: float
    container_type: str
    notes: str = ""

@dataclass
class UserProfile:
    """User profile for personalized hydration goals"""
    name: str
    weight_kg: float
    age: int
    gender: str
    activity_level: str
    climate: str
    daily_goal_ml: float
    wake_time: str = "07:00"
    sleep_time: str = "22:00"

@dataclass
class Achievement:
    """Achievement/badge system"""
    id: str
    name: str
    description: str
    icon: str
    unlocked_date: Optional[str] = None

class HydrationTracker:
    """Advanced hydration tracking system with AI insights"""
    
    def __init__(self):
        self.initialize_session_state()
        
        # Container presets with emojis and typical volumes
        self.containers = {
            "Glass": {"icon": "🥛", "volume": 250, "color": "#74b9ff"},
            "Water Bottle": {"icon": "🍶", "volume": 500, "color": "#0984e3"},
            "Large Bottle": {"icon": "💧", "volume": 1000, "color": "#00b894"},
            "Cup": {"icon": "☕", "volume": 200, "color": "#fdcb6e"},
            "Sports Bottle": {"icon": "🚰", "volume": 750, "color": "#e17055"},
            "Custom": {"icon": "⚗️", "volume": 0, "color": "#a8e6cf"}
        }
        
        # Activity level multipliers for hydration needs
        self.activity_multipliers = {
            "Sedentary": 1.0,
            "Lightly Active": 1.2,
            "Moderately Active": 1.5,
            "Very Active": 1.8,
            "Extremely Active": 2.0
        }
        
        # Climate adjustments
        self.climate_adjustments = {
            "Temperate": 1.0,
            "Hot/Humid": 1.3,
            "Cold/Dry": 1.1,
            "High Altitude": 1.4
        }
        
        # Achievement definitions
        self.achievements = [
            Achievement("first_drop", "First Drop 💧", "Log your first water intake", "💧"),
            Achievement("daily_goal", "Goal Crusher 🎯", "Reach your daily goal", "🎯"),
            Achievement("week_streak", "Week Warrior 📅", "7 days in a row", "📅"),
            Achievement("month_streak", "Monthly Master 🗓️", "30 days in a row", "🗓️"),
            Achievement("hydration_hero", "Hydration Hero 🦸‍♂️", "100 days total", "🦸‍♂️"),
            Achievement("early_bird", "Early Bird 🌅", "Log water before 8 AM", "🌅"),
            Achievement("night_owl", "Night Owl 🦉", "Log water after 10 PM", "🦉"),
            Achievement("big_sipper", "Big Sipper 🥤", "Log 1L in single entry", "🥤")
        ]
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'water_intake_records' not in st.session_state:
            st.session_state.water_intake_records = []
        if 'user_profile' not in st.session_state:
            st.session_state.user_profile = None
        if 'achievements_unlocked' not in st.session_state:
            st.session_state.achievements_unlocked = []
        if 'reminder_settings' not in st.session_state:
            st.session_state.reminder_settings = {
                'enabled': False,
                'interval_hours': 2,
                'start_time': '08:00',
                'end_time': '20:00'
            }
    
    def calculate_recommended_intake(self, weight_kg: float, age: int, gender: str, 
                                   activity_level: str, climate: str) -> float:
        """Calculate personalized daily water intake recommendation"""
        # Base calculation: 35ml per kg of body weight
        base_intake = weight_kg * 35
        
        # Age adjustments
        if age > 65:
            base_intake *= 0.9  # Slightly less for elderly
        elif age < 18:
            base_intake *= 1.1  # More for growing bodies
        
        # Gender adjustments (males generally need more)
        if gender.lower() == 'male':
            base_intake *= 1.1
        
        # Activity level adjustments
        activity_multiplier = self.activity_multipliers.get(activity_level, 1.0)
        base_intake *= activity_multiplier
        
        # Climate adjustments
        climate_multiplier = self.climate_adjustments.get(climate, 1.0)
        base_intake *= climate_multiplier
        
        return round(base_intake)
    
    def get_today_intake(self) -> float:
        """Get total water intake for today"""
        today = date.today().strftime("%Y-%m-%d")
        today_records = [r for r in st.session_state.water_intake_records 
                        if r.timestamp.startswith(today)]
        return sum(record.amount_ml for record in today_records)
    
    def get_progress_percentage(self) -> float:
        """Get today's progress percentage"""
        if not st.session_state.user_profile:
            return 0.0
        
        today_intake = self.get_today_intake()
        goal = st.session_state.user_profile.daily_goal_ml
        return min((today_intake / goal) * 100, 100) if goal > 0 else 0
    
    def add_water_intake(self, amount_ml: float, container_type: str, notes: str = ""):
        """Add water intake record"""
        record = WaterIntake(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            amount_ml=amount_ml,
            container_type=container_type,
            notes=notes
        )
        st.session_state.water_intake_records.append(record)
        
        # Check for achievements
        self.check_achievements()
        
        # Sort records by timestamp (newest first)
        st.session_state.water_intake_records.sort(
            key=lambda x: x.timestamp, reverse=True
        )
    
    def check_achievements(self):
        """Check and unlock achievements"""
        total_records = len(st.session_state.water_intake_records)
        today_intake = self.get_today_intake()
        
        achievements_to_unlock = []
        
        # First Drop
        if total_records >= 1 and "first_drop" not in st.session_state.achievements_unlocked:
            achievements_to_unlock.append("first_drop")
        
        # Daily Goal
        if (st.session_state.user_profile and 
            today_intake >= st.session_state.user_profile.daily_goal_ml and
            "daily_goal" not in st.session_state.achievements_unlocked):
            achievements_to_unlock.append("daily_goal")
        
        # Big Sipper
        if (st.session_state.water_intake_records and 
            st.session_state.water_intake_records[0].amount_ml >= 1000 and
            "big_sipper" not in st.session_state.achievements_unlocked):
            achievements_to_unlock.append("big_sipper")
        
        # Early Bird / Night Owl
        if st.session_state.water_intake_records:
            latest_time = datetime.strptime(st.session_state.water_intake_records[0].timestamp, "%Y-%m-%d %H:%M:%S")
            hour = latest_time.hour
            
            if hour < 8 and "early_bird" not in st.session_state.achievements_unlocked:
                achievements_to_unlock.append("early_bird")
            elif hour >= 22 and "night_owl" not in st.session_state.achievements_unlocked:
                achievements_to_unlock.append("night_owl")
        
        # Add newly unlocked achievements
        for achievement_id in achievements_to_unlock:
            if achievement_id not in st.session_state.achievements_unlocked:
                st.session_state.achievements_unlocked.append(achievement_id)
                st.balloons()  # Celebrate!
    
    def get_streak_count(self) -> int:
        """Calculate current streak of days meeting goal"""
        if not st.session_state.user_profile:
            return 0
        
        goal = st.session_state.user_profile.daily_goal_ml
        streak = 0
        current_date = date.today()
        
        for i in range(365):  # Check up to a year back
            check_date = current_date - timedelta(days=i)
            date_str = check_date.strftime("%Y-%m-%d")
            
            day_records = [r for r in st.session_state.water_intake_records 
                          if r.timestamp.startswith(date_str)]
            day_total = sum(record.amount_ml for record in day_records)
            
            if day_total >= goal:
                streak += 1
            else:
                break
        
        return streak
    
    def render_profile_setup(self):
        """Render user profile setup"""
        st.subheader("👤 Personal Hydration Profile")
        
        with st.form("hydration_profile"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Name", 
                                   value=st.session_state.user_profile.name if st.session_state.user_profile else "")
                weight_kg = st.number_input("Weight (kg)", 
                                          min_value=30.0, max_value=200.0, 
                                          value=st.session_state.user_profile.weight_kg if st.session_state.user_profile else 70.0,
                                          step=0.1)
                age = st.number_input("Age", 
                                    min_value=1, max_value=120,
                                    value=st.session_state.user_profile.age if st.session_state.user_profile else 30)
                gender = st.selectbox("Gender", ["Male", "Female"],
                                    index=0 if not st.session_state.user_profile else 
                                    (0 if st.session_state.user_profile.gender == "Male" else 1))
            
            with col2:
                activity_level = st.selectbox("Activity Level", list(self.activity_multipliers.keys()),
                                            index=2 if not st.session_state.user_profile else
                                            list(self.activity_multipliers.keys()).index(st.session_state.user_profile.activity_level))
                climate = st.selectbox("Climate", list(self.climate_adjustments.keys()),
                                     index=0 if not st.session_state.user_profile else
                                     list(self.climate_adjustments.keys()).index(st.session_state.user_profile.climate))
                
                # Calculate recommended intake
                recommended = self.calculate_recommended_intake(weight_kg, age, gender, activity_level, climate)
                st.info(f"💡 Recommended daily intake: **{recommended:,.0f} ml** ({recommended/1000:.1f}L)")
                
                custom_goal = st.number_input("Daily Goal (ml)", 
                                            min_value=500, max_value=8000,
                                            value=int(recommended),
                                            step=250)
            
            if st.form_submit_button("💾 Save Profile", use_container_width=True):
                st.session_state.user_profile = UserProfile(
                    name=name,
                    weight_kg=weight_kg,
                    age=age,
                    gender=gender,
                    activity_level=activity_level,
                    climate=climate,
                    daily_goal_ml=custom_goal
                )
                st.success("✅ Profile saved! Your personalized hydration journey begins now! 🚀")
                st.rerun()
    
    def render_quick_add_section(self):
        """Render quick water intake buttons"""
        st.subheader("💧 Quick Add Water")
        
        # Container buttons
        cols = st.columns(len(self.containers))
        for i, (container_name, container_data) in enumerate(self.containers.items()):
            with cols[i]:
                if st.button(
                    f"{container_data['icon']}\n{container_name}\n{container_data['volume']}ml", 
                    key=f"quick_{container_name}",
                    help=f"Add {container_data['volume']}ml"
                ):
                    if container_name == "Custom":
                        # Handle custom amount
                        st.session_state.show_custom_input = True
                    else:
                        self.add_water_intake(container_data['volume'], container_name)
                        st.success(f"✅ Added {container_data['volume']}ml from {container_name}!")
                        st.rerun()
        
        # Custom input section
        if getattr(st.session_state, 'show_custom_input', False):
            with st.form("custom_water"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    custom_amount = st.number_input("Amount (ml)", min_value=1, max_value=2000, value=250)
                with col2:
                    custom_container = st.selectbox("Container", list(self.containers.keys())[:-1])  # Exclude "Custom"
                with col3:
                    notes = st.text_input("Notes (optional)")
                
                if st.form_submit_button("➕ Add Water"):
                    self.add_water_intake(custom_amount, custom_container, notes)
                    st.session_state.show_custom_input = False
                    st.success(f"✅ Added {custom_amount}ml!")
                    st.rerun()
    
    def render_daily_progress(self):
        """Render daily progress display"""
        if not st.session_state.user_profile:
            st.info("👤 Set up your profile first for personalized tracking!")
            return
        
        today_intake = self.get_today_intake()
        goal = st.session_state.user_profile.daily_goal_ml
        progress = self.get_progress_percentage()
        
        # Main hydration display
        st.markdown(f"""
        <div class="hydration-display water-wave fade-in">
            <div class="intake-value">{today_intake:,.0f} ml</div>
            <div class="goal-text">of {goal:,.0f} ml goal ({progress:.1f}%)</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress bar with animation
        progress_color = "#00b894" if progress >= 100 else "#74b9ff" if progress >= 75 else "#fdcb6e" if progress >= 50 else "#e17055"
        
        st.markdown(f"""
        <div style="background: #e3f2fd; border-radius: 20px; padding: 10px; margin: 1rem 0;">
            <div style="background: {progress_color}; width: {progress}%; height: 20px; border-radius: 15px; 
                        transition: width 1s ease-in-out; position: relative;">
                <div style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%); 
                            color: white; font-weight: bold; font-size: 0.8rem;">
                    {progress:.1f}%
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Status message
        if progress >= 100:
            st.markdown("""
            <div class="water-card">
                <h3>🎉 Congratulations! Goal Achieved!</h3>
                <p>You've reached your daily hydration goal. Keep up the excellent work!</p>
            </div>
            """, unsafe_allow_html=True)
        elif progress >= 75:
            st.markdown("""
            <div class="tip-card">
                <h4>💪 Almost There!</h4>
                <p>You're doing great! Just a bit more to reach your goal.</p>
            </div>
            """, unsafe_allow_html=True)
        elif progress < 25:
            remaining = goal - today_intake
            st.markdown(f"""
            <div class="warning-card">
                <h4>🚨 Let's Catch Up!</h4>
                <p>You need {remaining:,.0f} ml more to reach your daily goal. Start hydrating! 💧</p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_statistics_dashboard(self):
        """Render comprehensive statistics"""
        st.subheader("📊 Hydration Analytics")
        
        if not st.session_state.water_intake_records:
            st.info("📈 Start logging water intake to see your statistics!")
            return
        
        # Calculate statistics
        total_records = len(st.session_state.water_intake_records)
        total_volume = sum(r.amount_ml for r in st.session_state.water_intake_records)
        avg_per_entry = total_volume / total_records if total_records > 0 else 0
        
        # Today's stats
        today_intake = self.get_today_intake()
        today_entries = len([r for r in st.session_state.water_intake_records 
                            if r.timestamp.startswith(date.today().strftime("%Y-%m-%d"))])
        
        # Streak
        current_streak = self.get_streak_count()
        
        # Statistics grid
        stats_data = [
            {"label": "Today's Intake", "value": f"{today_intake:,.0f} ml", "icon": "💧"},
            {"label": "Today's Entries", "value": str(today_entries), "icon": "📝"},
            {"label": "Current Streak", "value": f"{current_streak} days", "icon": "🔥"},
            {"label": "Total Volume", "value": f"{total_volume/1000:.1f}L", "icon": "🌊"},
            {"label": "Total Entries", "value": str(total_records), "icon": "📊"},
            {"label": "Avg per Entry", "value": f"{avg_per_entry:.0f} ml", "icon": "📏"}
        ]
        
        cols = st.columns(3)
        for i, stat in enumerate(stats_data):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="stat-item fade-in">
                    <div style="font-size: 1.5rem; margin-bottom: 0.5rem;">{stat['icon']}</div>
                    <div class="stat-value">{stat['value']}</div>
                    <div class="stat-label">{stat['label']}</div>
                </div>
                """, unsafe_allow_html=True)
        
        # Streak display
        if current_streak > 0:
            st.markdown(f"""
            <div class="streak-counter fade-in">
                <h3>🔥 {current_streak} Day Streak! 🔥</h3>
                <p>Keep the momentum going! Consistency is key to healthy hydration habits.</p>
            </div>
            """, unsafe_allow_html=True)
    
    def render_hydration_chart(self):
        """Render interactive hydration charts"""
        if not PLOTLY_AVAILABLE or not st.session_state.water_intake_records:
            if not PLOTLY_AVAILABLE:
                st.info("📊 Install plotly for interactive charts: pip install plotly")
            else:
                st.info("📈 Log some water intake to see your hydration patterns!")
            return
        
        st.subheader("📈 Hydration Trends")
        
        # Prepare data for the last 30 days
        end_date = date.today()
        start_date = end_date - timedelta(days=29)
        
        daily_data = []
        for i in range(30):
            current_date = start_date + timedelta(days=i)
            date_str = current_date.strftime("%Y-%m-%d")
            
            day_records = [r for r in st.session_state.water_intake_records 
                          if r.timestamp.startswith(date_str)]
            day_total = sum(record.amount_ml for record in day_records)
            
            daily_data.append({
                'date': current_date,
                'intake_ml': day_total,
                'intake_l': day_total / 1000,
                'goal_met': day_total >= (st.session_state.user_profile.daily_goal_ml if st.session_state.user_profile else 2000)
            })
        
        df = pd.DataFrame(daily_data)
        
        # Create the main chart
        fig = make_subplots(
            rows=2, cols=1,
            row_heights=[0.7, 0.3],
            subplot_titles=('Daily Water Intake (Last 30 Days)', 'Goal Achievement'),
            vertical_spacing=0.1
        )
        
        # Daily intake line chart
        colors = ['#00b894' if goal_met else '#74b9ff' for goal_met in df['goal_met']]
        
        fig.add_trace(
            go.Scatter(
                x=df['date'],
                y=df['intake_l'],
                mode='lines+markers',
                name='Daily Intake',
                line=dict(color='#74b9ff', width=3),
                marker=dict(size=8, color=colors),
                hovertemplate='<b>%{x}</b><br>Intake: %{y:.2f}L<extra></extra>'
            ),
            row=1, col=1
        )
        
        # Add goal line
        if st.session_state.user_profile:
            goal_l = st.session_state.user_profile.daily_goal_ml / 1000
            fig.add_hline(
                y=goal_l,
                line_dash="dash",
                line_color="#e17055",
                annotation_text=f"Goal: {goal_l:.1f}L",
                row=1
            )
        
        # Goal achievement bar chart
        fig.add_trace(
            go.Bar(
                x=df['date'],
                y=df['goal_met'].astype(int),
                name='Goal Met',
                marker_color=['#00b894' if met else '#e17055' for met in df['goal_met']],
                hovertemplate='<b>%{x}</b><br>Goal Met: %{text}<extra></extra>',
                text=['Yes' if met else 'No' for met in df['goal_met']]
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            height=600,
            showlegend=False,
            title_text="Your Hydration Journey",
            template="plotly_white",
            font=dict(family="Inter")
        )
        
        fig.update_xaxes(title_text="Date", row=2, col=1)
        fig.update_yaxes(title_text="Intake (Liters)", row=1, col=1)
        fig.update_yaxes(title_text="Goal Status", row=2, col=1, tickmode='array', tickvals=[0, 1], ticktext=['Not Met', 'Met'])
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Weekly pattern analysis
        if len(df) >= 7:
            self.render_weekly_pattern_analysis(df)
    
    def render_weekly_pattern_analysis(self, df):
        """Render weekly hydration pattern analysis"""
        st.subheader("📅 Weekly Pattern Analysis")
        
        # Add day of week to dataframe
        df['day_of_week'] = df['date'].dt.day_name()
        df['weekday'] = df['date'].dt.dayofweek
        
        # Calculate average by day of week
        weekly_avg = df.groupby(['day_of_week', 'weekday'])['intake_l'].mean().reset_index()
        weekly_avg = weekly_avg.sort_values('weekday')
        
        # Create weekly pattern chart
        fig = go.Figure()
        
        colors = ['#e17055' if intake < 2.0 else '#fdcb6e' if intake < 2.5 else '#00b894' 
                 for intake in weekly_avg['intake_l']]
        
        fig.add_trace(
            go.Bar(
                x=weekly_avg['day_of_week'],
                y=weekly_avg['intake_l'],
                marker_color=colors,
                text=[f'{val:.1f}L' for val in weekly_avg['intake_l']],
                textposition='auto',
                name='Average Intake'
            )
        )
        
        fig.update_layout(
            title="Average Intake by Day of Week",
            xaxis_title="Day of Week",
            yaxis_title="Average Intake (Liters)",
            template="plotly_white",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Insights
        best_day = weekly_avg.loc[weekly_avg['intake_l'].idxmax(), 'day_of_week']
        worst_day = weekly_avg.loc[weekly_avg['intake_l'].idxmin(), 'day_of_week']
        
        st.markdown(f"""
        <div class="tip-card">
            <h4>📊 Weekly Insights</h4>
            <p><strong>🏆 Best Day:</strong> {best_day} ({weekly_avg.loc[weekly_avg['day_of_week']==best_day, 'intake_l'].iloc[0]:.1f}L average)</p>
            <p><strong>📉 Focus Day:</strong> {worst_day} ({weekly_avg.loc[weekly_avg['day_of_week']==worst_day, 'intake_l'].iloc[0]:.1f}L average)</p>
            <p><strong>💡 Tip:</strong> Consider setting reminders on {worst_day}s to boost your hydration!</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_achievements_section(self):
        """Render achievements and badges"""
        st.subheader("🏆 Achievements & Badges")
        
        # Display unlocked achievements
        if st.session_state.achievements_unlocked:
            st.markdown("### 🌟 Unlocked Achievements")
            achievement_cols = st.columns(min(len(st.session_state.achievements_unlocked), 4))
            
            for i, achievement_id in enumerate(st.session_state.achievements_unlocked):
                achievement = next((a for a in self.achievements if a.id == achievement_id), None)
                if achievement:
                    with achievement_cols[i % 4]:
                        st.markdown(f"""
                        <div class="achievement-badge">
                            {achievement.icon} {achievement.name}
                        </div>
                        """, unsafe_allow_html=True)
                        st.caption(achievement.description)
        
        # Display locked achievements
        locked_achievements = [a for a in self.achievements 
                             if a.id not in st.session_state.achievements_unlocked]
        
        if locked_achievements:
            st.markdown("### 🔒 Locked Achievements")
            for achievement in locked_achievements:
                col1, col2 = st.columns([1, 4])
                with col1:
                    st.markdown(f"🔒 {achievement.icon}")
                with col2:
                    st.write(f"**{achievement.name}**")
                    st.caption(achievement.description)
    
    def render_intake_history(self):
        """Render recent intake history"""
        st.subheader("📝 Recent Intake History")
        
        if not st.session_state.water_intake_records:
            st.info("💧 No intake records yet. Start logging your water intake!")
            return
        
        # Show last 10 records
        recent_records = st.session_state.water_intake_records[:10]
        
        for record in recent_records:
            timestamp_dt = datetime.strptime(record.timestamp, "%Y-%m-%d %H:%M:%S")
            time_ago = datetime.now() - timestamp_dt
            
            if time_ago.days > 0:
                time_str = f"{time_ago.days}d ago"
            elif time_ago.seconds > 3600:
                time_str = f"{time_ago.seconds//3600}h ago"
            elif time_ago.seconds > 60:
                time_str = f"{time_ago.seconds//60}m ago"
            else:
                time_str = "Just now"
            
            container_info = self.containers.get(record.container_type, {"icon": "💧"})
            
            col1, col2, col3, col4 = st.columns([1, 2, 2, 2])
            with col1:
                st.markdown(f"<div style='font-size: 1.5rem;'>{container_info['icon']}</div>", 
                          unsafe_allow_html=True)
            with col2:
                st.write(f"**{record.amount_ml:,.0f} ml**")
            with col3:
                st.write(record.container_type)
            with col4:
                st.write(f"*{time_str}*")
            
            if record.notes:
                st.caption(f"📝 {record.notes}")
            
            st.divider()
    
    def render_hydration_tips(self):
        """Render hydration tips and health information"""
        st.subheader("💡 Hydration Tips & Health Benefits")
        
        tips_and_benefits = [
            {
                "title": "🌅 Start Your Day Right",
                "content": "Drink a glass of water immediately after waking up to kickstart your metabolism and rehydrate after hours of sleep.",
                "type": "tip"
            },
            {
                "title": "🧠 Brain Power Boost",
                "content": "Even mild dehydration (2% fluid loss) can impair concentration, memory, and mood. Stay sharp by staying hydrated!",
                "type": "benefit"
            },
            {
                "title": "💪 Exercise Hydration",
                "content": "Drink 500-600ml of water 2-3 hours before exercise, and 200-300ml every 15-20 minutes during activity.",
                "type": "tip"
            },
            {
                "title": "✨ Glowing Skin",
                "content": "Proper hydration helps maintain skin elasticity and can reduce signs of aging. Your skin will thank you!",
                "type": "benefit"
            },
            {
                "title": "🍎 Natural Appetite Control",
                "content": "Sometimes thirst masquerades as hunger. Try drinking water first before reaching for snacks.",
                "type": "tip"
            },
            {
                "title": "🏃‍♂️ Enhanced Performance",
                "content": "Optimal hydration can improve physical performance by up to 25% and reduce fatigue.",
                "type": "benefit"
            }
        ]
        
        for i, item in enumerate(tips_and_benefits):
            if item["type"] == "tip":
                st.markdown(f"""
                <div class="tip-card fade-in">
                    <h4>{item['title']}</h4>
                    <p>{item['content']}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="water-card fade-in">
                    <h4>{item['title']}</h4>
                    <p>{item['content']}</p>
                </div>
                """, unsafe_allow_html=True)

def main():
    """Main application function"""
    st.markdown('<h1 class="main-title">💧 Hydration & Wellness Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Your Personal Water Intake Tracker & Health Companion</p>', unsafe_allow_html=True)
    
    # Initialize tracker
    tracker = HydrationTracker()
    
    # Sidebar navigation
    with st.sidebar:
        st.header("🧭 Navigation")
        
        page = st.selectbox(
            "Select Page:",
            ["🏠 Dashboard", "👤 Profile Setup", "📊 Analytics", "🏆 Achievements", 
             "📝 History", "💡 Health Tips", "⚙️ Settings"]
        )
        
        st.markdown("---")
        
        # Quick stats
        if st.session_state.user_profile:
            st.subheader("📈 Quick Stats")
            today_intake = tracker.get_today_intake()
            progress = tracker.get_progress_percentage()
            streak = tracker.get_streak_count()
            
            st.metric("Today's Intake", f"{today_intake:,.0f} ml")
            st.metric("Progress", f"{progress:.1f}%")
            st.metric("Streak", f"{streak} days")
            
            # Mini progress bar
            st.progress(progress/100)
        
        st.markdown("---")
        
        # Quick add buttons
        st.subheader("⚡ Quick Add")
        quick_amounts = [250, 500, 750]
        for amount in quick_amounts:
            if st.button(f"💧 {amount}ml", key=f"sidebar_quick_{amount}", use_container_width=True):
                tracker.add_water_intake(amount, "Glass")
                st.success(f"Added {amount}ml!")
                st.rerun()
        
        st.markdown("---")
        
        # Motivational quote
        quotes = [
            "💧 Water is life's matter and matrix, mother and medium.",
            "🌊 The cure for anything is salt water: sweat, tears or the sea.",
            "💎 Pure water is the world's first and foremost medicine.",
            "🏃‍♂️ A river cuts through rock, not because of power but persistence.",
            "✨ Water is the driving force of all nature."
        ]
        
        import random
        daily_quote = random.choice(quotes)
        st.info(daily_quote)
    
    # Main content based on selected page
    if page == "🏠 Dashboard":
        if not st.session_state.user_profile:
            st.markdown("""
            <div class="water-card fade-in">
                <h3>🎯 Welcome to Your Hydration Journey!</h3>
                <p>Set up your personal profile to get started with customized hydration tracking, 
                   personalized goals, and detailed analytics.</p>
            </div>
            """, unsafe_allow_html=True)
            tracker.render_profile_setup()
        else:
            # Daily progress
            tracker.render_daily_progress()
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Quick add section
                tracker.render_quick_add_section()
                
                # Statistics
                tracker.render_statistics_dashboard()
            
            with col2:
                # Recent history
                tracker.render_intake_history()
    
    elif page == "👤 Profile Setup":
        tracker.render_profile_setup()
        
        if st.session_state.user_profile:
            st.success("✅ Profile configured! Return to Dashboard to start tracking.")
    
    elif page == "📊 Analytics":
        if not st.session_state.user_profile:
            st.warning("⚠️ Please set up your profile first!")
        else:
            tracker.render_hydration_chart()
    
    elif page == "🏆 Achievements":
        tracker.render_achievements_section()
    
    elif page == "📝 History":
        tracker.render_intake_history()
        
        # Export functionality
        if st.session_state.water_intake_records:
            st.markdown("---")
            st.subheader("📤 Export Data")
            
            df = pd.DataFrame([asdict(record) for record in st.session_state.water_intake_records])
            csv = df.to_csv(index=False)
            
            st.download_button(
                "💾 Download History as CSV",
                csv,
                f"hydration_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv"
            )
    
    elif page == "💡 Health Tips":
        tracker.render_hydration_tips()
    
    elif page == "⚙️ Settings":
        st.subheader("⚙️ App Settings")
        
        # Reminder settings
        st.markdown("### 🔔 Reminder Settings")
        
        reminder_enabled = st.checkbox("Enable Reminders", 
                                     value=st.session_state.reminder_settings['enabled'])
        
        if reminder_enabled:
            col1, col2 = st.columns(2)
            with col1:
                interval = st.slider("Reminder Interval (hours)", 1, 8, 
                                   st.session_state.reminder_settings['interval_hours'])
            with col2:
                start_time = st.time_input("Start Time", 
                                         time.fromisoformat(st.session_state.reminder_settings['start_time']))
                end_time = st.time_input("End Time", 
                                       time.fromisoformat(st.session_state.reminder_settings['end_time']))
            
            if st.button("💾 Save Reminder Settings"):
                st.session_state.reminder_settings.update({
                    'enabled': reminder_enabled,
                    'interval_hours': interval,
                    'start_time': start_time.strftime("%H:%M"),
                    'end_time': end_time.strftime("%H:%M")
                })
                st.success("✅ Reminder settings saved!")
        
        st.markdown("---")
        
        # Data management
        st.markdown("### 🗃️ Data Management")
        
        if st.button("🗑️ Clear All Data", type="secondary"):
            if st.button("⚠️ Confirm Clear All Data"):
                st.session_state.water_intake_records = []
                st.session_state.achievements_unlocked = []
                st.success("✅ All data cleared!")
                st.rerun()
        
        st.warning("⚠️ This will permanently delete all your hydration records and achievements.")

if __name__ == "__main__":
    main()