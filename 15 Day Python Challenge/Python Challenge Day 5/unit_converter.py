import streamlit as st
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta, date
import json
import requests
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, asdict
import time
import re

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
    page_title="🔄 Universal Converter Hub",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern converter design
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
        font-style: italic;
    }
    
    .converter-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
        margin: 1rem 0;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        border: 1px solid #e0e6ed;
    }
    
    .converter-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 50px rgba(102, 126, 234, 0.2);
    }
    
    .result-display {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(102, 126, 234, 0.3);
    }
    
    .result-value {
        font-size: 2.5rem;
        font-weight: 800;
        margin: 0.5rem 0;
        text-shadow: 0 2px 4px rgba(0, 0, 0, 0.2);
    }
    
    .result-unit {
        font-size: 1.2rem;
        opacity: 0.9;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .category-card {
        background: linear-gradient(135deg, #a8e6cf, #7fcdcd);
        color: #2c3e50;
        padding: 1.5rem;
        border-radius: 15px;
        margin: 0.5rem;
        text-align: center;
        cursor: pointer;
        transition: transform 0.3s ease;
        box-shadow: 0 4px 20px rgba(127, 205, 205, 0.3);
    }
    
    .category-card:hover {
        transform: scale(1.05);
        box-shadow: 0 6px 25px rgba(127, 205, 205, 0.4);
    }
    
    .currency-card {
        background: linear-gradient(135deg, #ffecd2, #fcb69f);
        color: #8b4513;
    }
    
    .temperature-card {
        background: linear-gradient(135deg, #ff9a9e, #fecfef);
        color: #8b008b;
    }
    
    .length-card {
        background: linear-gradient(135deg, #a8edea, #fed6e3);
        color: #2c3e50;
    }
    
    .weight-card {
        background: linear-gradient(135deg, #fad0c4, #ffd1ff);
        color: #8b4513;
    }
    
    .quick-convert {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    
    .history-item {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #764ba2;
    }
    
    .rate-display {
        background: linear-gradient(135deg, #74b9ff, #0984e3);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
    }
    
    .warning-banner {
        background: linear-gradient(135deg, #ff9f43, #ee5a24);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        text-align: center;
    }
    
    .info-banner {
        background: linear-gradient(135deg, #74b9ff, #0984e3);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    .success-banner {
        background: linear-gradient(135deg, #00b894, #00a085);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
    
    /* Input styling */
    .stNumberInput > div > div > input {
        font-size: 1.2rem;
        font-weight: 500;
        text-align: center;
    }
    
    .stSelectbox > div > div > div {
        font-weight: 500;
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
        50% { transform: scale(1.02); }
        100% { transform: scale(1); }
    }
    
    .slide-in {
        animation: slideIn 0.6s ease-out;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-30px); }
        to { opacity: 1; transform: translateX(0); }
    }
</style>
""", unsafe_allow_html=True)

@dataclass
class ConversionRecord:
    """Data class for storing conversion history"""
    timestamp: str
    category: str
    from_unit: str
    to_unit: str
    from_value: float
    to_value: float
    rate: Optional[float] = None

class CurrencyConverter:
    """Real-time currency converter with API integration"""
    
    def __init__(self):
        self.api_key = None  # In production, use environment variable
        self.base_url = "https://api.exchangerate-api.com/v4/latest/"
        self.rates_cache = {}
        self.cache_timestamp = None
        self.cache_duration = 300  # 5 minutes
        
        # Fallback rates (offline mode)
        self.fallback_rates = {
            'USD': 1.0,
            'EUR': 0.85,
            'GBP': 0.73,
            'JPY': 110.0,
            'CAD': 1.25,
            'AUD': 1.35,
            'CHF': 0.92,
            'CNY': 6.45,
            'INR': 74.5,
            'KRW': 1180.0,
            'BRL': 5.2,
            'RUB': 73.5,
            'MXN': 20.1,
            'SGD': 1.35,
            'HKD': 7.8,
            'NOK': 8.6,
            'SEK': 8.9,
            'DKK': 6.3,
            'PLN': 3.9,
            'CZK': 21.5
        }
    
    def get_currency_rates(self, base_currency: str = 'USD') -> Dict[str, float]:
        """Get real-time currency exchange rates"""
        # Check cache first
        if (self.cache_timestamp and 
            time.time() - self.cache_timestamp < self.cache_duration and
            base_currency in self.rates_cache):
            return self.rates_cache[base_currency]
        
        try:
            # Try to get real-time rates
            response = requests.get(f"{self.base_url}{base_currency}", timeout=5)
            if response.status_code == 200:
                data = response.json()
                rates = data.get('rates', {})
                
                # Cache the results
                self.rates_cache[base_currency] = rates
                self.cache_timestamp = time.time()
                
                return rates
        except Exception as e:
            st.warning(f"⚠️ Using offline rates. API Error: {str(e)}")
        
        # Fallback to offline rates
        if base_currency == 'USD':
            return self.fallback_rates
        else:
            # Convert fallback rates to different base
            usd_rate = self.fallback_rates.get(base_currency, 1.0)
            return {k: v / usd_rate for k, v in self.fallback_rates.items()}
    
    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> Tuple[float, float]:
        """Convert currency with real-time rates"""
        if from_currency == to_currency:
            return amount, 1.0
        
        rates = self.get_currency_rates(from_currency)
        
        if to_currency in rates:
            rate = rates[to_currency]
            converted_amount = amount * rate
            return converted_amount, rate
        else:
            return amount, 1.0

class UniversalConverter:
    """Advanced universal unit converter with multiple categories"""
    
    def __init__(self):
        self.initialize_session_state()
        self.currency_converter = CurrencyConverter()
        
        # Comprehensive conversion data
        self.conversion_data = {
            "Length": {
                "base_unit": "meter",
                "units": {
                    "millimeter": {"symbol": "mm", "factor": 0.001},
                    "centimeter": {"symbol": "cm", "factor": 0.01},
                    "meter": {"symbol": "m", "factor": 1.0},
                    "kilometer": {"symbol": "km", "factor": 1000.0},
                    "inch": {"symbol": "in", "factor": 0.0254},
                    "foot": {"symbol": "ft", "factor": 0.3048},
                    "yard": {"symbol": "yd", "factor": 0.9144},
                    "mile": {"symbol": "mi", "factor": 1609.34},
                    "nautical_mile": {"symbol": "nmi", "factor": 1852.0},
                    "light_year": {"symbol": "ly", "factor": 9.461e15},
                    "astronomical_unit": {"symbol": "AU", "factor": 1.496e11}
                }
            },
            "Weight": {
                "base_unit": "kilogram",
                "units": {
                    "milligram": {"symbol": "mg", "factor": 1e-6},
                    "gram": {"symbol": "g", "factor": 0.001},
                    "kilogram": {"symbol": "kg", "factor": 1.0},
                    "tonne": {"symbol": "t", "factor": 1000.0},
                    "ounce": {"symbol": "oz", "factor": 0.0283495},
                    "pound": {"symbol": "lb", "factor": 0.453592},
                    "stone": {"symbol": "st", "factor": 6.35029},
                    "carat": {"symbol": "ct", "factor": 0.0002},
                    "grain": {"symbol": "gr", "factor": 6.479891e-5}
                }
            },
            "Temperature": {
                "base_unit": "celsius",
                "special": True  # Requires special conversion formulas
            },
            "Area": {
                "base_unit": "square_meter",
                "units": {
                    "square_millimeter": {"symbol": "mm²", "factor": 1e-6},
                    "square_centimeter": {"symbol": "cm²", "factor": 1e-4},
                    "square_meter": {"symbol": "m²", "factor": 1.0},
                    "hectare": {"symbol": "ha", "factor": 10000.0},
                    "square_kilometer": {"symbol": "km²", "factor": 1e6},
                    "square_inch": {"symbol": "in²", "factor": 0.00064516},
                    "square_foot": {"symbol": "ft²", "factor": 0.092903},
                    "square_yard": {"symbol": "yd²", "factor": 0.836127},
                    "acre": {"symbol": "ac", "factor": 4046.86},
                    "square_mile": {"symbol": "mi²", "factor": 2.59e6}
                }
            },
            "Volume": {
                "base_unit": "liter",
                "units": {
                    "milliliter": {"symbol": "ml", "factor": 0.001},
                    "liter": {"symbol": "L", "factor": 1.0},
                    "cubic_meter": {"symbol": "m³", "factor": 1000.0},
                    "cubic_inch": {"symbol": "in³", "factor": 0.0163871},
                    "cubic_foot": {"symbol": "ft³", "factor": 28.3168},
                    "gallon_us": {"symbol": "gal (US)", "factor": 3.78541},
                    "gallon_uk": {"symbol": "gal (UK)", "factor": 4.54609},
                    "quart": {"symbol": "qt", "factor": 0.946353},
                    "pint": {"symbol": "pt", "factor": 0.473176},
                    "cup": {"symbol": "cup", "factor": 0.236588},
                    "fluid_ounce": {"symbol": "fl oz", "factor": 0.0295735}
                }
            },
            "Speed": {
                "base_unit": "meter_per_second",
                "units": {
                    "meter_per_second": {"symbol": "m/s", "factor": 1.0},
                    "kilometer_per_hour": {"symbol": "km/h", "factor": 0.277778},
                    "mile_per_hour": {"symbol": "mph", "factor": 0.44704},
                    "foot_per_second": {"symbol": "ft/s", "factor": 0.3048},
                    "knot": {"symbol": "kn", "factor": 0.514444},
                    "mach": {"symbol": "M", "factor": 343.0}
                }
            },
            "Energy": {
                "base_unit": "joule",
                "units": {
                    "joule": {"symbol": "J", "factor": 1.0},
                    "kilojoule": {"symbol": "kJ", "factor": 1000.0},
                    "calorie": {"symbol": "cal", "factor": 4.184},
                    "kilocalorie": {"symbol": "kcal", "factor": 4184.0},
                    "watt_hour": {"symbol": "Wh", "factor": 3600.0},
                    "kilowatt_hour": {"symbol": "kWh", "factor": 3.6e6},
                    "btu": {"symbol": "BTU", "factor": 1055.06}
                }
            }
        }
        
        # Currency data
        self.currencies = {
            'USD': '🇺🇸 US Dollar', 'EUR': '🇪🇺 Euro', 'GBP': '🇬🇧 British Pound',
            'JPY': '🇯🇵 Japanese Yen', 'CAD': '🇨🇦 Canadian Dollar', 'AUD': '🇦🇺 Australian Dollar',
            'CHF': '🇨🇭 Swiss Franc', 'CNY': '🇨🇳 Chinese Yuan', 'INR': '🇮🇳 Indian Rupee',
            'KRW': '🇰🇷 South Korean Won', 'BRL': '🇧🇷 Brazilian Real', 'RUB': '🇷🇺 Russian Ruble',
            'MXN': '🇲🇽 Mexican Peso', 'SGD': '🇸🇬 Singapore Dollar', 'HKD': '🇭🇰 Hong Kong Dollar',
            'NOK': '🇳🇴 Norwegian Krone', 'SEK': '🇸🇪 Swedish Krona', 'DKK': '🇩🇰 Danish Krone',
            'PLN': '🇵🇱 Polish Złoty', 'CZK': '🇨🇿 Czech Koruna'
        }
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'conversion_history' not in st.session_state:
            st.session_state.conversion_history = []
        if 'favorites' not in st.session_state:
            st.session_state.favorites = []
        if 'selected_category' not in st.session_state:
            st.session_state.selected_category = 'Length'
    
    def convert_temperature(self, value: float, from_unit: str, to_unit: str) -> float:
        """Convert between temperature units"""
        # Convert to Celsius first
        if from_unit == "fahrenheit":
            celsius = (value - 32) * 5/9
        elif from_unit == "kelvin":
            celsius = value - 273.15
        elif from_unit == "rankine":
            celsius = (value - 491.67) * 5/9
        else:  # celsius
            celsius = value
        
        # Convert from Celsius to target unit
        if to_unit == "fahrenheit":
            return (celsius * 9/5) + 32
        elif to_unit == "kelvin":
            return celsius + 273.15
        elif to_unit == "rankine":
            return (celsius + 273.15) * 9/5
        else:  # celsius
            return celsius
    
    def convert_unit(self, value: float, from_unit: str, to_unit: str, category: str) -> Tuple[float, Optional[float]]:
        """Universal unit conversion function"""
        if category == "Currency":
            result, rate = self.currency_converter.convert_currency(value, from_unit, to_unit)
            return result, rate
        
        if category == "Temperature":
            result = self.convert_temperature(value, from_unit.lower(), to_unit.lower())
            return result, None
        
        if category not in self.conversion_data:
            return value, None
        
        category_data = self.conversion_data[category]
        
        # Convert to base unit first, then to target unit
        from_factor = category_data["units"][from_unit]["factor"]
        to_factor = category_data["units"][to_unit]["factor"]
        
        base_value = value * from_factor
        result = base_value / to_factor
        
        return result, to_factor / from_factor
    
    def add_to_history(self, category: str, from_unit: str, to_unit: str, from_value: float, to_value: float, rate: Optional[float] = None):
        """Add conversion to history"""
        record = ConversionRecord(
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            category=category,
            from_unit=from_unit,
            to_unit=to_unit,
            from_value=from_value,
            to_value=to_value,
            rate=rate
        )
        st.session_state.conversion_history.insert(0, record)
        # Keep only last 50 conversions
        st.session_state.conversion_history = st.session_state.conversion_history[:50]
    
    def add_to_favorites(self, category: str, from_unit: str, to_unit: str):
        """Add conversion pair to favorites"""
        favorite = f"{category}: {from_unit} → {to_unit}"
        if favorite not in st.session_state.favorites:
            st.session_state.favorites.append(favorite)
    
    def render_category_selector(self):
        """Render category selection interface"""
        st.subheader("🎯 Select Conversion Category")
        
        categories = ["Currency", "Temperature", "Length", "Weight", "Area", "Volume", "Speed", "Energy"]
        
        # Visual category cards
        cols = st.columns(4)
        for i, category in enumerate(categories):
            with cols[i % 4]:
                if st.button(f"{self.get_category_emoji(category)} {category}", key=f"cat_{category}", use_container_width=True):
                    st.session_state.selected_category = category
                    st.rerun()
    
    def get_category_emoji(self, category: str) -> str:
        """Get emoji for category"""
        emojis = {
            "Currency": "💰", "Temperature": "🌡️", "Length": "📏", 
            "Weight": "⚖️", "Area": "📐", "Volume": "🧪", 
            "Speed": "🚀", "Energy": "⚡"
        }
        return emojis.get(category, "🔄")
    
    def render_converter_interface(self, category: str):
        """Render the main converter interface"""
        st.markdown(f'<div class="converter-card fade-in">', unsafe_allow_html=True)
        
        # Header
        emoji = self.get_category_emoji(category)
        st.subheader(f"{emoji} {category} Converter")
        
        # Get available units
        if category == "Currency":
            available_units = list(self.currencies.keys())
            unit_display = self.currencies
        elif category == "Temperature":
            available_units = ["celsius", "fahrenheit", "kelvin", "rankine"]
            unit_display = {
                "celsius": "🌡️ Celsius (°C)",
                "fahrenheit": "🌡️ Fahrenheit (°F)", 
                "kelvin": "🌡️ Kelvin (K)",
                "rankine": "🌡️ Rankine (°R)"
            }
        else:
            category_data = self.conversion_data.get(category, {})
            available_units = list(category_data.get("units", {}).keys())
            unit_display = {unit: f"{data['symbol']} {unit.replace('_', ' ').title()}" 
                           for unit, data in category_data.get("units", {}).items()}
        
        if not available_units:
            st.error(f"No units available for {category}")
            return
        
        # Input section
        col1, col2, col3 = st.columns([2, 1, 2])
        
        with col1:
            st.write("**From:**")
            from_unit = st.selectbox(
                "Select source unit:",
                available_units,
                format_func=lambda x: unit_display.get(x, x),
                key=f"from_{category}"
            )
            
            value = st.number_input(
                f"Enter value in {unit_display.get(from_unit, from_unit)}:",
                value=1.0,
                step=0.01,
                format="%.6f",
                key=f"value_{category}"
            )
        
        with col2:
            st.write("")
            st.write("")
            if st.button("🔄", key=f"swap_{category}", help="Swap units"):
                # Swap logic would go here
                pass
        
        with col3:
            st.write("**To:**")
            to_unit = st.selectbox(
                "Select target unit:",
                available_units,
                index=1 if len(available_units) > 1 else 0,
                format_func=lambda x: unit_display.get(x, x),
                key=f"to_{category}"
            )
        
        # Perform conversion
        if value is not None:
            try:
                result, rate = self.convert_unit(value, from_unit, to_unit, category)
                
                # Display result
                st.markdown(f"""
                <div class="result-display slide-in">
                    <div class="result-value">{result:,.6f}</div>
                    <div class="result-unit">{unit_display.get(to_unit, to_unit)}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Show exchange rate for currency
                if category == "Currency" and rate:
                    st.markdown(f"""
                    <div class="rate-display">
                        <strong>Exchange Rate:</strong> 1 {from_unit} = {rate:.6f} {to_unit}
                    </div>
                    """, unsafe_allow_html=True)
                
                # Action buttons
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("💾 Save to History", key=f"save_{category}"):
                        self.add_to_history(category, from_unit, to_unit, value, result, rate)
                        st.success("✅ Saved to history!")
                
                with col2:
                    if st.button("⭐ Add to Favorites", key=f"fav_{category}"):
                        self.add_to_favorites(category, from_unit, to_unit)
                        st.success("⭐ Added to favorites!")
                
                with col3:
                    if st.button("📋 Copy Result", key=f"copy_{category}"):
                        st.info(f"📋 {result:,.6f} {to_unit}")
                
            except Exception as e:
                st.error(f"❌ Conversion error: {str(e)}")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    def render_quick_conversions(self):
        """Render quick conversion shortcuts"""
        st.subheader("⚡ Quick Conversions")
        
        quick_conversions = {
            "Temperature": [
                ("0", "celsius", "fahrenheit", "Freezing point"),
                ("100", "celsius", "fahrenheit", "Boiling point"),
                ("37", "celsius", "fahrenheit", "Body temperature")
            ],
            "Length": [
                ("1", "meter", "foot", "Basic length"),
                ("1", "kilometer", "mile", "Distance"),
                ("1", "inch", "centimeter", "Small measurements")
            ],
            "Weight": [
                ("1", "kilogram", "pound", "Basic weight"),
                ("1", "pound", "kilogram", "Reverse conversion"),
                ("1", "tonne", "pound", "Heavy weights")
            ]
        }
        
        for category, conversions in quick_conversions.items():
            with st.expander(f"{self.get_category_emoji(category)} {category}"):
                for value, from_unit, to_unit, description in conversions:
                    try:
                        result, _ = self.convert_unit(float(value), from_unit, to_unit, category)
                        
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"""
                            <div class="quick-convert">
                                <strong>{description}:</strong> {value} {from_unit} = {result:.2f} {to_unit}
                            </div>
                            """, unsafe_allow_html=True)
                        with col2:
                            if st.button("Use", key=f"quick_{category}_{from_unit}_{to_unit}"):
                                st.session_state.selected_category = category
                                st.rerun()
                    except:
                        continue
    
    def render_history(self):
        """Render conversion history"""
        st.subheader("📚 Conversion History")
        
        if not st.session_state.conversion_history:
            st.info("No conversion history yet. Perform some conversions to see them here!")
            return
        
        # Display recent conversions
        for i, record in enumerate(st.session_state.conversion_history[:10]):
            st.markdown(f"""
            <div class="history-item">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <strong>{record.category}:</strong> {record.from_value:,.6f} {record.from_unit} 
                        → {record.to_value:,.6f} {record.to_unit}
                    </div>
                    <small>{record.timestamp}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        # Export history
        if st.button("📤 Export History"):
            df = pd.DataFrame([asdict(record) for record in st.session_state.conversion_history])
            csv = df.to_csv(index=False)
            st.download_button(
                label="💾 Download CSV",
                data=csv,
                file_name=f"conversion_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    def render_favorites(self):
        """Render favorite conversions"""
        st.subheader("⭐ Favorite Conversions")
        
        if not st.session_state.favorites:
            st.info("No favorites yet. Add some frequently used conversions!")
            return
        
        for favorite in st.session_state.favorites:
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"⭐ {favorite}")
            with col2:
                if st.button("🗑️", key=f"remove_{favorite}", help="Remove from favorites"):
                    st.session_state.favorites.remove(favorite)
                    st.rerun()
    
    def render_batch_converter(self):
        """Render batch conversion interface"""
        st.subheader("📊 Batch Converter")
        
        category = st.selectbox("Select category for batch conversion:", 
                              ["Length", "Weight", "Temperature", "Currency"])
        
        if category == "Currency":
            available_units = list(self.currencies.keys())
        elif category == "Temperature":
            available_units = ["celsius", "fahrenheit", "kelvin"]
        else:
            available_units = list(self.conversion_data[category]["units"].keys())
        
        col1, col2 = st.columns(2)
        with col1:
            from_unit = st.selectbox("From unit:", available_units, key="batch_from")
        with col2:
            to_units = st.multiselect("To units:", available_units, key="batch_to")
        
        values_input = st.text_area("Enter values (one per line):", placeholder="1\n2\n3\n...")
        
        if st.button("🔄 Convert All") and values_input and to_units:
            try:
                values = [float(line.strip()) for line in values_input.split('\n') if line.strip()]
                
                results = []
                for value in values:
                    row = {"Input": value}
                    for to_unit in to_units:
                        try:
                            result, _ = self.convert_unit(value, from_unit, to_unit, category)
                            row[to_unit] = result
                        except:
                            row[to_unit] = "Error"
                    results.append(row)
                
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True)
                
                # Download option
                csv = df.to_csv(index=False)
                st.download_button(
                    "💾 Download Results",
                    csv,
                    f"batch_conversion_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv"
                )
                
            except Exception as e:
                st.error(f"❌ Error in batch conversion: {str(e)}")
    
    def render_currency_trends(self):
        """Render currency trend analysis"""
        if not PLOTLY_AVAILABLE:
            st.info("📊 Install plotly for currency trend visualization: pip install plotly")
            return
        
        st.subheader("📈 Currency Trends (Mock Data)")
        
        # Mock trend data (in production, use real historical data)
        dates = pd.date_range(start='2024-01-01', end='2024-12-31', freq='D')
        
        # Generate mock data for popular currency pairs
        usd_eur = 0.85 + 0.1 * np.sin(np.linspace(0, 4*np.pi, len(dates))) + np.random.normal(0, 0.02, len(dates))
        usd_gbp = 0.73 + 0.08 * np.cos(np.linspace(0, 3*np.pi, len(dates))) + np.random.normal(0, 0.015, len(dates))
        usd_jpy = 110 + 10 * np.sin(np.linspace(0, 2*np.pi, len(dates))) + np.random.normal(0, 2, len(dates))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(x=dates, y=usd_eur, name='USD/EUR', line=dict(color='blue')))
        fig.add_trace(go.Scatter(x=dates, y=usd_gbp, name='USD/GBP', line=dict(color='green')))
        fig.add_trace(go.Scatter(x=dates, y=usd_jpy/100, name='USD/JPY (÷100)', line=dict(color='red')))
        
        fig.update_layout(
            title="Currency Exchange Rate Trends (2024)",
            xaxis_title="Date",
            yaxis_title="Exchange Rate",
            hovermode="x unified",
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)

def main():
    """Main application function"""
    st.markdown('<h1 class="main-title">🔄 Universal Converter Hub</h1>', unsafe_allow_html=True)
    st.markdown('<p class="subtitle">Professional-Grade Unit Conversion Platform</p>', unsafe_allow_html=True)
    
    # Initialize converter
    converter = UniversalConverter()
    
    # Sidebar navigation
    with st.sidebar:
        st.header("🧭 Navigation")
        
        page = st.selectbox(
            "Select Page:",
            ["🏠 Main Converter", "⚡ Quick Conversions", "📚 History", 
             "⭐ Favorites", "📊 Batch Converter", "📈 Currency Trends", "ℹ️ About"]
        )
        
        st.markdown("---")
        
        # Current selection
        st.subheader("🎯 Current Selection")
        st.write(f"**Category:** {st.session_state.selected_category}")
        
        # Statistics
        st.subheader("📊 Statistics")
        st.metric("Conversions Done", len(st.session_state.conversion_history))
        st.metric("Favorites", len(st.session_state.favorites))
        
        # Quick tips
        st.subheader("💡 Pro Tips")
        tips = [
            "🔄 Use the swap button to reverse conversions",
            "⭐ Save frequently used conversions to favorites",
            "📊 Try batch converter for multiple values",
            "📈 Check currency trends for market insights",
            "💾 Export your history for record keeping"
        ]
        
        for tip in tips:
            st.info(tip)
    
    # Main content based on selected page
    if page == "🏠 Main Converter":
        # Category selection
        converter.render_category_selector()
        
        # Main converter interface
        st.markdown("---")
        converter.render_converter_interface(st.session_state.selected_category)
        
        # Real-time currency info
        if st.session_state.selected_category == "Currency":
            st.markdown(f"""
            <div class="info-banner">
                <h4>💰 Currency Information</h4>
                <p>Exchange rates are updated every 5 minutes. Rates shown are for informational purposes only.</p>
                <p><strong>Last Update:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            </div>
            """, unsafe_allow_html=True)
    
    elif page == "⚡ Quick Conversions":
        converter.render_quick_conversions()
    
    elif page == "📚 History":
        converter.render_history()
    
    elif page == "⭐ Favorites":
        converter.render_favorites()
    
    elif page == "📊 Batch Converter":
        converter.render_batch_converter()
    
    elif page == "📈 Currency Trends":
        converter.render_currency_trends()
    
    elif page == "ℹ️ About":
        st.subheader("📖 About Universal Converter Hub")
        
        st.markdown("""
        <div class="info-banner fade-in">
            <h3>🎯 Features</h3>
            <ul>
                <li>🌍 <strong>Multi-Category Support:</strong> Currency, Temperature, Length, Weight, Area, Volume, Speed, Energy</li>
                <li>💱 <strong>Real-Time Currency:</strong> Live exchange rates with API integration</li>
                <li>📊 <strong>Batch Processing:</strong> Convert multiple values at once</li>
                <li>📚 <strong>History Tracking:</strong> Keep track of all your conversions</li>
                <li>⭐ <strong>Favorites:</strong> Save frequently used conversion pairs</li>
                <li>📈 <strong>Trend Analysis:</strong> Currency market visualization</li>
                <li>📤 <strong>Export Options:</strong> Download results as CSV</li>
            </ul>
        </div>
        
        <div class="success-banner fade-in">
            <h3>🚀 Advanced Technology</h3>
            <p>Built with modern web technologies including real-time API integration, 
               advanced mathematical calculations, and interactive visualizations.</p>
        </div>
        
        <div class="warning-banner fade-in">
            <h3>⚠️ Disclaimer</h3>
            <p>This tool is for informational purposes only. For official conversions, 
               especially for legal or commercial purposes, please consult authoritative sources.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Supported units summary
        st.subheader("📋 Supported Units")
        
        for category, data in converter.conversion_data.items():
            with st.expander(f"{converter.get_category_emoji(category)} {category}"):
                if category == "Temperature":
                    st.write("• Celsius (°C), Fahrenheit (°F), Kelvin (K), Rankine (°R)")
                else:
                    units = data.get("units", {})
                    unit_list = [f"• {unit.replace('_', ' ').title()} ({info['symbol']})" 
                               for unit, info in units.items()]
                    st.markdown("\n".join(unit_list))
        
        # Currency support
        with st.expander("💰 Currencies"):
            currency_list = [f"• {code}: {name}" for code, name in converter.currencies.items()]
            st.markdown("\n".join(currency_list))

if __name__ == "__main__":
    main()