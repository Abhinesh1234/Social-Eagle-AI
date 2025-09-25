import streamlit as st
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date
import json
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, asdict
import base64
from io import BytesIO

# Optional imports with fallbacks
try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("📊 Install plotly for advanced visualizations: pip install plotly")

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    st.warning("🖼️ Install Pillow for image features: pip install pillow")

# Page configuration
st.set_page_config(
    page_title="🏋️ Health & Fitness Dashboard",
    page_icon="🏋️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern health dashboard design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    
    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 3.5rem;
        font-weight: 800;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 1rem;
    }
    
    .subtitle {
        text-align: center;
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
        margin: 10px 0;
        transition: transform 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(102, 126, 234, 0.4);
    }
    
    .health-card {
        padding: 1.5rem;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease;
    }
    
    .health-card:hover {
        transform: translateY(-3px);
    }
    
    .underweight-card {
        background: linear-gradient(135deg, #74b9ff, #0984e3);
        color: white;
    }
    
    .normal-card {
        background: linear-gradient(135deg, #00b894, #00a085);
        color: white;
    }
    
    .overweight-card {
        background: linear-gradient(135deg, #fdcb6e, #e17055);
        color: white;
    }
    
    .obese-card {
        background: linear-gradient(135deg, #e84393, #fd79a8);
        color: white;
    }
    
    .bmi-display {
        font-family: 'Inter', sans-serif;
        font-size: 4rem;
        font-weight: 800;
        text-align: center;
        padding: 2rem;
        border-radius: 20px;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        margin: 20px 0;
        box-shadow: 0 10px 40px rgba(102, 126, 234, 0.3);
    }
    
    .progress-container {
        background: #f8f9fa;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    
    .recommendation-card {
        background: linear-gradient(135deg, #a8e6cf, #7fcdcd);
        color: #2c3e50;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
    }
    
    .warning-card {
        background: linear-gradient(135deg, #ff9f43, #ee5a24);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(238, 90, 36, 0.3);
    }
    
    .info-card {
        background: linear-gradient(135deg, #74b9ff, #0984e3);
        color: white;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(116, 185, 255, 0.3);
    }
    
    .input-section {
        background: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
    }
    
    .stApp > div:first-child {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Custom slider styling */
    .stSlider > div > div > div > div {
        background: linear-gradient(135deg, #667eea, #764ba2);
    }
    
    /* Metric value styling */
    .metric-value {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .metric-label {
        font-size: 1rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Animation classes */
    .fade-in {
        animation: fadeIn 0.8s ease-in;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .pulse {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

@dataclass
class HealthRecord:
    """Data class for storing health measurements"""
    date: str
    weight: float
    height: float
    bmi: float
    category: str
    notes: str = ""
    body_fat: Optional[float] = None
    muscle_mass: Optional[float] = None

@dataclass
class UserProfile:
    """User profile with personal information"""
    name: str
    age: int
    gender: str
    activity_level: str
    goal: str
    target_weight: Optional[float] = None

class BMICalculator:
    """Advanced BMI calculator with multiple calculation methods and health insights"""
    
    def __init__(self):
        self.initialize_session_state()
        
        # BMI categories with detailed ranges and descriptions
        self.bmi_categories = {
            "Severely Underweight": {"range": (0, 16), "color": "#74b9ff", "risk": "High"},
            "Underweight": {"range": (16, 18.5), "color": "#0984e3", "risk": "Moderate"},
            "Normal Weight": {"range": (18.5, 25), "color": "#00b894", "risk": "Low"},
            "Overweight": {"range": (25, 30), "color": "#fdcb6e", "risk": "Moderate"},
            "Obese Class I": {"range": (30, 35), "color": "#e17055", "risk": "High"},
            "Obese Class II": {"range": (35, 40), "color": "#e84393", "risk": "Very High"},
            "Obese Class III": {"range": (40, 50), "color": "#fd79a8", "risk": "Extremely High"}
        }
        
        # Activity level multipliers for calorie calculation
        self.activity_multipliers = {
            "Sedentary": 1.2,
            "Lightly Active": 1.375,
            "Moderately Active": 1.55,
            "Very Active": 1.725,
            "Extremely Active": 1.9
        }
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'health_records' not in st.session_state:
            st.session_state.health_records = []
        if 'user_profile' not in st.session_state:
            st.session_state.user_profile = None
        if 'units' not in st.session_state:
            st.session_state.units = 'metric'  # metric or imperial
    
    def calculate_bmi(self, weight: float, height: float, units: str = 'metric') -> float:
        """Calculate BMI with unit conversion"""
        if units == 'imperial':
            # Convert pounds to kg and inches to meters
            weight_kg = weight * 0.453592
            height_m = height * 0.0254
        else:
            weight_kg = weight
            height_m = height / 100  # cm to meters
        
        return weight_kg / (height_m ** 2)
    
    def get_bmi_category(self, bmi: float) -> Tuple[str, Dict]:
        """Get BMI category and associated data"""
        for category, data in self.bmi_categories.items():
            if data["range"][0] <= bmi < data["range"][1]:
                return category, data
        
        # Handle extreme cases
        if bmi < 16:
            return "Severely Underweight", self.bmi_categories["Severely Underweight"]
        else:
            return "Obese Class III", self.bmi_categories["Obese Class III"]
    
    def calculate_ideal_weight_range(self, height: float, units: str = 'metric') -> Tuple[float, float]:
        """Calculate ideal weight range based on healthy BMI"""
        if units == 'imperial':
            height_m = height * 0.0254
        else:
            height_m = height / 100
        
        min_weight = 18.5 * (height_m ** 2)
        max_weight = 24.9 * (height_m ** 2)
        
        if units == 'imperial':
            min_weight *= 2.20462  # kg to pounds
            max_weight *= 2.20462
        
        return min_weight, max_weight
    
    def estimate_body_fat_percentage(self, bmi: float, age: int, gender: str) -> float:
        """Estimate body fat percentage using BMI, age, and gender"""
        if gender.lower() == 'male':
            body_fat = (1.20 * bmi) + (0.23 * age) - 16.2
        else:  # female
            body_fat = (1.20 * bmi) + (0.23 * age) - 5.4
        
        return max(0, min(100, body_fat))  # Clamp between 0-100%
    
    def calculate_bmr(self, weight: float, height: float, age: int, gender: str, units: str = 'metric') -> float:
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
        if units == 'imperial':
            weight_kg = weight * 0.453592
            height_cm = height * 2.54
        else:
            weight_kg = weight
            height_cm = height
        
        if gender.lower() == 'male':
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) + 5
        else:  # female
            bmr = (10 * weight_kg) + (6.25 * height_cm) - (5 * age) - 161
        
        return bmr
    
    def calculate_daily_calories(self, bmr: float, activity_level: str) -> int:
        """Calculate daily calorie needs based on BMR and activity level"""
        multiplier = self.activity_multipliers.get(activity_level, 1.2)
        return int(bmr * multiplier)
    
    def get_health_recommendations(self, bmi: float, category: str, age: int, gender: str) -> List[str]:
        """Generate personalized health recommendations"""
        recommendations = []
        
        if category == "Underweight":
            recommendations.extend([
                "🍎 Focus on nutrient-dense, calorie-rich foods",
                "💪 Include strength training to build muscle mass",
                "🥛 Add healthy fats like nuts, avocados, and olive oil",
                "👨‍⚕️ Consult a healthcare provider to rule out underlying conditions"
            ])
        elif category == "Normal Weight":
            recommendations.extend([
                "✅ Maintain your current healthy lifestyle",
                "🏃‍♀️ Continue regular physical activity",
                "🥗 Follow a balanced diet with variety",
                "📊 Monitor your weight regularly"
            ])
        elif "Overweight" in category or "Obese" in category:
            recommendations.extend([
                "🥗 Create a moderate caloric deficit (300-500 calories/day)",
                "🏃‍♀️ Aim for 150+ minutes of moderate exercise per week",
                "💧 Drink plenty of water and limit sugary beverages",
                "🍽️ Practice portion control and mindful eating",
                "👨‍⚕️ Consider consulting a healthcare provider or nutritionist"
            ])
        
        # Age-specific recommendations
        if age > 50:
            recommendations.extend([
                "🦴 Ensure adequate calcium and vitamin D intake",
                "💪 Include resistance training to prevent muscle loss",
                "🧘‍♀️ Consider low-impact exercises like swimming or yoga"
            ])
        
        return recommendations
    
    def create_bmi_gauge(self, bmi: float) -> Optional[go.Figure]:
        """Create an interactive BMI gauge chart"""
        if not PLOTLY_AVAILABLE:
            return None
        
        # Create gauge chart
        fig = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = bmi,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "BMI Score", 'font': {'size': 24, 'family': 'Inter'}},
            delta = {'reference': 22.5},  # Middle of normal range
            gauge = {
                'axis': {'range': [None, 45], 'tickwidth': 2, 'tickcolor': "darkblue"},
                'bar': {'color': "navy", 'thickness': 0.3},
                'bgcolor': "white",
                'borderwidth': 3,
                'bordercolor': "gray",
                'steps': [
                    {'range': [0, 16], 'color': "#74b9ff"},
                    {'range': [16, 18.5], 'color': "#0984e3"},
                    {'range': [18.5, 25], 'color': "#00b894"},
                    {'range': [25, 30], 'color': "#fdcb6e"},
                    {'range': [30, 35], 'color': "#e17055"},
                    {'range': [35, 40], 'color': "#e84393"},
                    {'range': [40, 45], 'color': "#fd79a8"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 25  # Overweight threshold
                }
            }
        ))
        
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font={'color': "black", 'family': "Inter"},
            height=400
        )
        
        return fig
    
    def create_progress_chart(self, records: List[HealthRecord]) -> Optional[go.Figure]:
        """Create BMI progress chart over time"""
        if not PLOTLY_AVAILABLE or not records:
            return None
        
        dates = [record.date for record in records]
        bmis = [record.bmi for record in records]
        weights = [record.weight for record in records]
        
        # Create subplot with secondary y-axis
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        # BMI trace
        fig.add_trace(
            go.Scatter(x=dates, y=bmis, name="BMI", line=dict(color="#667eea", width=3)),
            secondary_y=False,
        )
        
        # Weight trace
        fig.add_trace(
            go.Scatter(x=dates, y=weights, name="Weight", line=dict(color="#764ba2", width=2, dash="dash")),
            secondary_y=True,
        )
        
        # Add BMI category zones
        fig.add_hline(y=18.5, line_dash="dot", line_color="blue", annotation_text="Underweight")
        fig.add_hline(y=25, line_dash="dot", line_color="green", annotation_text="Normal")
        fig.add_hline(y=30, line_dash="dot", line_color="orange", annotation_text="Overweight")
        
        fig.update_xaxes(title_text="Date")
        fig.update_yaxes(title_text="BMI", secondary_y=False)
        fig.update_yaxes(title_text="Weight (kg)", secondary_y=True)
        
        fig.update_layout(
            title="BMI & Weight Progress",
            template="plotly_white",
            hovermode="x unified",
            font=dict(family="Inter"),
            height=400
        )
        
        return fig
    
    def create_comparison_chart(self, user_bmi: float, age: int, gender: str) -> Optional[go.Figure]:
        """Create BMI comparison chart with population averages"""
        if not PLOTLY_AVAILABLE:
            return None
        
        # Simulated population data (in real app, this would come from health databases)
        age_groups = ['18-29', '30-39', '40-49', '50-59', '60+']
        male_avg_bmi = [24.2, 26.1, 27.3, 28.1, 27.8]
        female_avg_bmi = [23.8, 25.9, 26.8, 27.5, 27.2]
        
        fig = go.Figure()
        
        # Population averages
        fig.add_trace(go.Bar(
            name='Male Average',
            x=age_groups,
            y=male_avg_bmi,
            marker_color='#74b9ff',
            opacity=0.7
        ))
        
        fig.add_trace(go.Bar(
            name='Female Average',
            x=age_groups,
            y=female_avg_bmi,
            marker_color='#fd79a8',
            opacity=0.7
        ))
        
        # User's BMI line
        fig.add_hline(
            y=user_bmi,
            line_dash="solid",
            line_color="red",
            line_width=3,
            annotation_text=f"Your BMI: {user_bmi:.1f}"
        )
        
        fig.update_layout(
            title=f'Your BMI vs Population Average ({gender})',
            xaxis_title='Age Group',
            yaxis_title='BMI',
            barmode='group',
            template='plotly_white',
            font=dict(family="Inter"),
            height=400
        )
        
        return fig
    
    def export_health_data(self, records: List[HealthRecord], profile: Optional[UserProfile]) -> str:
        """Export health data to CSV format"""
        if not records:
            return ""
        
        df = pd.DataFrame([asdict(record) for record in records])
        csv_string = df.to_csv(index=False)
        
        # Add profile information as header
        if profile:
            header = f"# Health Data Export\n"
            header += f"# Name: {profile.name}\n"
            header += f"# Age: {profile.age}\n"
            header += f"# Gender: {profile.gender}\n"
            header += f"# Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            csv_string = header + csv_string
        
        return csv_string
    
    def render_user_profile_section(self):
        """Render user profile setup section"""
        st.subheader("👤 User Profile")
        
        with st.form("profile_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Name", value=st.session_state.user_profile.name if st.session_state.user_profile else "")
                age = st.number_input("Age", min_value=1, max_value=120, value=st.session_state.user_profile.age if st.session_state.user_profile else 30)
                gender = st.selectbox("Gender", ["Male", "Female"], index=0 if not st.session_state.user_profile else (0 if st.session_state.user_profile.gender == "Male" else 1))
            
            with col2:
                activity_level = st.selectbox("Activity Level", list(self.activity_multipliers.keys()), 
                                            index=2 if not st.session_state.user_profile else list(self.activity_multipliers.keys()).index(st.session_state.user_profile.activity_level))
                goal = st.selectbox("Health Goal", ["Maintain Weight", "Lose Weight", "Gain Weight", "Build Muscle"], 
                                   index=0 if not st.session_state.user_profile else ["Maintain Weight", "Lose Weight", "Gain Weight", "Build Muscle"].index(st.session_state.user_profile.goal))
                target_weight = st.number_input("Target Weight (optional)", min_value=0.0, value=st.session_state.user_profile.target_weight if st.session_state.user_profile and st.session_state.user_profile.target_weight else 0.0)
            
            if st.form_submit_button("💾 Save Profile"):
                st.session_state.user_profile = UserProfile(
                    name=name,
                    age=age,
                    gender=gender,
                    activity_level=activity_level,
                    goal=goal,
                    target_weight=target_weight if target_weight > 0 else None
                )
                st.success("✅ Profile saved!")
                st.rerun()
    
    def render_bmi_input_section(self):
        """Render BMI calculation input section"""
        st.markdown('<div class="input-section">', unsafe_allow_html=True)
        st.subheader("📏 Body Measurements")
        
        # Unit selection
        col1, col2, col3 = st.columns([2, 1, 2])
        with col2:
            units = st.radio("Units", ["Metric", "Imperial"], horizontal=True)
            st.session_state.units = units.lower()
        
        # Input fields based on units
        col1, col2 = st.columns(2)
        
        if st.session_state.units == 'metric':
            with col1:
                height = st.slider("Height (cm)", min_value=100, max_value=250, value=170, step=1)
            with col2:
                weight = st.slider("Weight (kg)", min_value=30.0, max_value=200.0, value=70.0, step=0.1)
        else:  # imperial
            with col1:
                feet = st.slider("Height (feet)", min_value=3, max_value=8, value=5)
                inches = st.slider("Height (inches)", min_value=0, max_value=11, value=7)
                height = feet * 12 + inches
            with col2:
                weight = st.slider("Weight (lbs)", min_value=66, max_value=440, value=154, step=1)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        return height, weight
    
    def render_bmi_results(self, height: float, weight: float):
        """Render BMI calculation results and analysis"""
        # Calculate BMI
        bmi = self.calculate_bmi(weight, height, st.session_state.units)
        category, category_data = self.get_bmi_category(bmi)
        
        # Display BMI prominently
        st.markdown(f"""
        <div class="bmi-display fade-in">
            <div class="metric-value">{bmi:.1f}</div>
            <div class="metric-label">BMI Score</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Category display
        category_class = category.lower().replace(' ', '-').replace('class', 'card')
        if 'underweight' in category_class:
            card_class = 'underweight-card'
        elif 'normal' in category_class:
            card_class = 'normal-card'
        elif 'overweight' in category_class:
            card_class = 'overweight-card'
        else:
            card_class = 'obese-card'
        
        st.markdown(f"""
        <div class="health-card {card_class} fade-in">
            <h3>🎯 {category}</h3>
            <p><strong>Health Risk Level:</strong> {category_data['risk']}</p>
            <p><strong>BMI Range:</strong> {category_data['range'][0]} - {category_data['range'][1]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        return bmi, category, category_data
    
    def render_detailed_analysis(self, height: float, weight: float, bmi: float, category: str):
        """Render detailed health analysis"""
        if not st.session_state.user_profile:
            st.info("👤 Complete your user profile above for personalized analysis!")
            return
        
        profile = st.session_state.user_profile
        
        # Calculate additional metrics
        ideal_min, ideal_max = self.calculate_ideal_weight_range(height, st.session_state.units)
        body_fat = self.estimate_body_fat_percentage(bmi, profile.age, profile.gender)
        bmr = self.calculate_bmr(weight, height, profile.age, profile.gender, st.session_state.units)
        daily_calories = self.calculate_daily_calories(bmr, profile.activity_level)
        
        # Display metrics in cards
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card fade-in">
                <div class="metric-label">Ideal Weight Range</div>
                <div class="metric-value">{ideal_min:.1f} - {ideal_max:.1f}</div>
                <div class="metric-label">{'kg' if st.session_state.units == 'metric' else 'lbs'}</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card fade-in">
                <div class="metric-label">Est. Body Fat</div>
                <div class="metric-value">{body_fat:.1f}%</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card fade-in">
                <div class="metric-label">BMR</div>
                <div class="metric-value">{bmr:.0f}</div>
                <div class="metric-label">calories/day</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card fade-in">
                <div class="metric-label">Daily Calories</div>
                <div class="metric-value">{daily_calories}</div>
                <div class="metric-label">for {profile.activity_level}</div>
            </div>
            """, unsafe_allow_html=True)
        
        return {
            'ideal_range': (ideal_min, ideal_max),
            'body_fat': body_fat,
            'bmr': bmr,
            'daily_calories': daily_calories
        }
    
    def render_recommendations(self, bmi: float, category: str):
        """Render health recommendations"""
        if not st.session_state.user_profile:
            return
        
        profile = st.session_state.user_profile
        recommendations = self.get_health_recommendations(bmi, category, profile.age, profile.gender)
        
        st.markdown(f"""
        <div class="recommendation-card fade-in">
            <h3>💡 Personalized Recommendations</h3>
            {''.join(f'<p>{rec}</p>' for rec in recommendations)}
        </div>
        """, unsafe_allow_html=True)
    
    def render_visualizations(self, bmi: float):
        """Render interactive charts and visualizations"""
        if not PLOTLY_AVAILABLE:
            st.info("📊 Install plotly for interactive visualizations: pip install plotly")
            return
        
        col1, col2 = st.columns(2)
        
        with col1:
            # BMI Gauge
            gauge_fig = self.create_bmi_gauge(bmi)
            if gauge_fig:
                st.plotly_chart(gauge_fig, use_container_width=True)
        
        with col2:
            # Population Comparison
            if st.session_state.user_profile:
                comparison_fig = self.create_comparison_chart(
                    bmi, 
                    st.session_state.user_profile.age, 
                    st.session_state.user_profile.gender
                )
                if comparison_fig:
                    st.plotly_chart(comparison_fig, use_container_width=True)
    
    def render_progress_tracking(self, height: float, weight: float, bmi: float, category: str):
        """Render progress tracking section"""
        st.subheader("📈 Progress Tracking")
        
        # Add new record
        with st.form("add_record"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                record_date = st.date_input("Date", value=date.today())
            with col2:
                notes = st.text_input("Notes (optional)")
            with col3:
                if st.form_submit_button("➕ Add Record"):
                    new_record = HealthRecord(
                        date=record_date.strftime("%Y-%m-%d"),
                        weight=weight,
                        height=height,
                        bmi=bmi,
                        category=category,
                        notes=notes
                    )
                    st.session_state.health_records.append(new_record)
                    st.success("✅ Record added!")
                    st.rerun()
        
        # Display progress chart
        if st.session_state.health_records and PLOTLY_AVAILABLE:
            progress_fig = self.create_progress_chart(st.session_state.health_records)
            if progress_fig:
                st.plotly_chart(progress_fig, use_container_width=True)
        
        # Display records table
        if st.session_state.health_records:
            st.subheader("📋 Health Records")
            
            # Convert to DataFrame for display
            records_data = []
            for record in st.session_state.health_records[-10:]:  # Show last 10 records
                records_data.append({
                    "Date": record.date,
                    "Weight": f"{record.weight:.1f}",
                    "BMI": f"{record.bmi:.1f}",
                    "Category": record.category,
                    "Notes": record.notes or "-"
                })
            
            df = pd.DataFrame(records_data)
            st.dataframe(df, use_container_width=True)
            
            # Export functionality
            col1, col2 = st.columns([3, 1])
            with col2:
                if st.button("📤 Export Data"):
                    csv_data = self.export_health_data(st.session_state.health_records, st.session_state.user_profile)
                    st.download_button(
                        label="💾 Download CSV",
                        data=csv_data,
                        file_name=f"health_data_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )

def main():
    """Main application function"""
    st.markdown('<h1 class="main-title">🏋️ Health & Fitness Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Advanced BMI Calculator with AI-Powered Health Insights</p>', unsafe_allow_html=True)
    
    # Initialize calculator
    calculator = BMICalculator()
    
    # Sidebar for navigation and settings
    with st.sidebar:
        st.header("⚙️ Dashboard Settings")
        
        # Navigation
        page = st.selectbox(
            "📍 Navigate to:",
            ["🏠 Main Dashboard", "👤 User Profile", "📈 Progress Tracking", "📊 Analytics", "ℹ️ About BMI"]
        )
        
        # Quick stats if profile exists
        if st.session_state.user_profile:
            st.subheader("👤 Quick Profile")
            profile = st.session_state.user_profile
            st.write(f"**Name:** {profile.name}")
            st.write(f"**Age:** {profile.age}")
            st.write(f"**Goal:** {profile.goal}")
            
            if st.session_state.health_records:
                latest_record = st.session_state.health_records[-1]
                st.write(f"**Last BMI:** {latest_record.bmi:.1f}")
                st.write(f"**Category:** {latest_record.category}")
        
        # Health tips
        st.subheader("💡 Daily Health Tip")
        health_tips = [
            "💧 Drink at least 8 glasses of water daily",
            "🚶‍♀️ Take a 10-minute walk after meals",
            "😴 Aim for 7-9 hours of quality sleep",
            "🥗 Fill half your plate with vegetables",
            "🧘‍♀️ Practice 5 minutes of meditation daily",
            "📱 Limit screen time before bed",
            "🍎 Choose whole foods over processed ones",
            "💪 Include strength training 2-3 times per week"
        ]
        
        import random
        daily_tip = random.choice(health_tips)
        st.info(daily_tip)
    
    # Main content based on selected page
    if page == "🏠 Main Dashboard":
        # User Profile Section (if not set up)
        if not st.session_state.user_profile:
            st.markdown("""
            <div class="info-card fade-in">
                <h3>🎯 Welcome to Your Health Dashboard!</h3>
                <p>Set up your profile below for personalized health insights and recommendations.</p>
            </div>
            """, unsafe_allow_html=True)
            calculator.render_user_profile_section()
        
        # BMI Calculation Section
        height, weight = calculator.render_bmi_input_section()
        
        # Results and Analysis
        bmi, category, category_data = calculator.render_bmi_results(height, weight)
        
        # Detailed Analysis (requires profile)
        analysis_data = calculator.render_detailed_analysis(height, weight, bmi, category)
        
        # Recommendations
        calculator.render_recommendations(bmi, category)
        
        # Visualizations
        calculator.render_visualizations(bmi)
        
    elif page == "👤 User Profile":
        calculator.render_user_profile_section()
        
        if st.session_state.user_profile:
            st.success("✅ Profile is set up! Return to Main Dashboard for full analysis.")
    
    elif page == "📈 Progress Tracking":
        if not st.session_state.user_profile:
            st.warning("⚠️ Please set up your user profile first!")
        else:
            height, weight = calculator.render_bmi_input_section()
            bmi, category, _ = calculator.render_bmi_results(height, weight)
            calculator.render_progress_tracking(height, weight, bmi, category)
    
    elif page == "📊 Analytics":
        st.subheader("📊 Health Analytics")
        
        if not st.session_state.health_records:
            st.info("📈 Add some health records to see analytics!")
        else:
            # Show summary statistics
            records = st.session_state.health_records
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                avg_bmi = sum(r.bmi for r in records) / len(records)
                st.metric("Average BMI", f"{avg_bmi:.1f}")
            
            with col2:
                weight_change = records[-1].weight - records[0].weight
                st.metric("Weight Change", f"{weight_change:+.1f} kg", delta=f"{weight_change:+.1f}")
            
            with col3:
                days_tracked = (datetime.strptime(records[-1].date, "%Y-%m-%d") - 
                              datetime.strptime(records[0].date, "%Y-%m-%d")).days
                st.metric("Days Tracked", days_tracked)
            
            with col4:
                st.metric("Total Records", len(records))
            
            # Progress visualization
            if PLOTLY_AVAILABLE:
                progress_fig = calculator.create_progress_chart(records)
                if progress_fig:
                    st.plotly_chart(progress_fig, use_container_width=True)
    
    elif page == "ℹ️ About BMI":
        st.subheader("📚 Understanding BMI")
        
        st.markdown("""
        <div class="info-card fade-in">
            <h3>🧮 What is BMI?</h3>
            <p>Body Mass Index (BMI) is a measure of body fat based on height and weight. 
               It's calculated as weight (kg) divided by height squared (m²).</p>
        </div>
        
        <div class="recommendation-card fade-in">
            <h3>📊 BMI Categories</h3>
            <ul>
                <li><strong>Underweight:</strong> BMI less than 18.5</li>
                <li><strong>Normal weight:</strong> BMI 18.5-24.9</li>
                <li><strong>Overweight:</strong> BMI 25-29.9</li>
                <li><strong>Obese:</strong> BMI 30 or greater</li>
            </ul>
        </div>
        
        <div class="warning-card fade-in">
            <h3>⚠️ Important Notes</h3>
            <p>BMI is a screening tool, not a diagnostic tool. It doesn't account for muscle mass, 
               bone density, or fat distribution. Always consult healthcare professionals for 
               comprehensive health assessment.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # BMI calculation examples
        st.subheader("🧮 BMI Calculation Examples")
        
        examples = [
            {"height": 170, "weight": 70, "description": "Average adult"},
            {"height": 180, "weight": 85, "description": "Tall athletic person"},
            {"height": 160, "weight": 55, "description": "Petite person"}
        ]
        
        for example in examples:
            bmi = calculator.calculate_bmi(example["weight"], example["height"])
            category, _ = calculator.get_bmi_category(bmi)
            
            st.write(f"**{example['description']}:** {example['height']}cm, {example['weight']}kg → BMI: {bmi:.1f} ({category})")

if __name__ == "__main__":
    main()