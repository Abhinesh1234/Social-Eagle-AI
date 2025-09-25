import streamlit as st
import math
import numpy as np
from datetime import datetime, timedelta
import json
import re
from typing import List, Dict, Any, Union
from dataclasses import dataclass, asdict
import pandas as pd
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import base64
from io import BytesIO

# Optional imports with fallbacks
PYTESSERACT_IMPORT_SUCCESS = False

try:
    import plotly.graph_objects as go
    import plotly.express as px
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    st.warning("📊 Plotly not installed. Some visualization features will be limited.")

try:
    import sympy as sp
    from sympy.parsing.sympy_parser import parse_expr
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False
    st.warning("🧮 SymPy not installed. Using basic math evaluation.")

try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    CV2_AVAILABLE = False
    st.warning("🖼️ OpenCV not installed. Image processing will be limited.")

try:
    import pytesseract
    # Test if tesseract is actually available with better error handling
    PYTESSERACT_IMPORT_SUCCESS = True
    try:
        # Try to get version first
        version = pytesseract.get_tesseract_version()
        PYTESSERACT_AVAILABLE = True
        st.success(f"✅ Tesseract {version} detected successfully!")
    except pytesseract.TesseractNotFoundError as e:
        PYTESSERACT_AVAILABLE = False
        st.error(f"🔧 Tesseract OCR engine not found: {str(e)}")
    except Exception as e:
        PYTESSERACT_AVAILABLE = False
        st.warning(f"👁️ Tesseract issue: {str(e)}")
except ImportError as e:
    PYTESSERACT_IMPORT_SUCCESS = False
    PYTESSERACT_AVAILABLE = False
    st.error(f"📦 PyTesseract import failed: {str(e)}")
    st.info("Try: pip install --upgrade pytesseract")

try:
    from streamlit_drawable_canvas import st_canvas
    CANVAS_AVAILABLE = True
except ImportError:
    CANVAS_AVAILABLE = False
    st.error("🎨 streamlit-drawable-canvas not installed. Please run: pip install streamlit-drawable-canvas")

# Page configuration
st.set_page_config(
    page_title="🧮 Advanced Calculator Pro",
    page_icon="🧮",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern design
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    .main-title {
        font-family: 'Inter', sans-serif;
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 2rem;
    }
    
    .calculator-display {
        font-family: 'Courier New', monospace;
        font-size: 2.5rem;
        font-weight: bold;
        text-align: right;
        padding: 20px;
        background: linear-gradient(135deg, #1e3c72, #2a5298);
        color: white;
        border-radius: 15px;
        margin-bottom: 20px;
        min-height: 80px;
        display: flex;
        align-items: center;
        justify-content: flex-end;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .calc-button {
        width: 100%;
        height: 60px;
        font-size: 1.5rem;
        font-weight: 600;
        border-radius: 12px;
        border: none;
        margin: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
        font-family: 'Inter', sans-serif;
    }
    
    .calc-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.15);
    }
    
    .operator-btn {
        background: linear-gradient(135deg, #ff6b6b, #ee5a52);
        color: white;
    }
    
    .number-btn {
        background: linear-gradient(135deg, #4ecdc4, #44a08d);
        color: white;
    }
    
    .function-btn {
        background: linear-gradient(135deg, #a8e6cf, #7fcdcd);
        color: #2c3e50;
    }
    
    .history-item {
        background: rgba(255, 255, 255, 0.1);
        padding: 10px;
        border-radius: 8px;
        margin: 5px 0;
        font-family: 'Courier New', monospace;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 20px;
        border-radius: 12px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .canvas-container {
        border: 3px solid #667eea;
        border-radius: 15px;
        padding: 10px;
        background: linear-gradient(135deg, #f5f7fa, #c3cfe2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .recognition-result {
        background: linear-gradient(135deg, #a8e6cf, #7fcdcd);
        color: #2c3e50;
        padding: 15px;
        border-radius: 10px;
        margin: 10px 0;
        font-family: 'Courier New', monospace;
        font-size: 1.2rem;
        font-weight: bold;
    }
    
    .canvas-controls {
        background: rgba(255, 255, 255, 0.1);
        padding: 10px;
        border-radius: 8px;
        margin: 10px 0;
    }
    
    .ai-badge {
        background: linear-gradient(135deg, #ff9a9e, #fecfef);
        color: #2c3e50;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        display: inline-block;
        margin: 5px;
    }
    
    .stApp > div:first-child {
        background: linear-gradient(135deg, #0c0c0c, #1a1a2e, #16213e);
    }
    
    .stSlider > div > div > div {
        background: linear-gradient(135deg, #667eea, #764ba2);
    }
</style>
""", unsafe_allow_html=True)

@dataclass
class CalculationHistory:
    """Data class for storing calculation history"""
    timestamp: str
    expression: str
    result: str
    mode: str
    input_method: str = "manual"  # manual, handwritten

class HandwritingRecognizer:
    """AI-powered handwriting recognition for mathematical expressions"""
    
    def __init__(self):
        self.symbol_mapping = {
            # Common OCR misrecognitions
            'x': '*', 'X': '*', '×': '*', 'χ': '*',
            '÷': '/', '−': '-', '–': '-', '—': '-',
            '²': '**2', '³': '**3', 
            '√': 'sqrt', '∛': 'cbrt',
            'π': 'pi', 'Π': 'pi',
            'α': 'alpha', 'β': 'beta', 'γ': 'gamma',
            '∑': 'sum', '∏': 'prod',
            '∫': 'integrate', '∂': 'diff',
            '≈': '~', '≠': '!=', '≤': '<=', '≥': '>=',
            '°': '*pi/180',  # degree to radian
            '!': 'factorial',
        }
        
        # Try to configure tesseract path automatically
        self.configure_tesseract_path()
    
    def configure_tesseract_path(self):
        """Automatically configure tesseract path for different operating systems"""
        import platform
        import os
        import shutil
        
        system = platform.system().lower()
        
        # First, try to find tesseract in PATH
        tesseract_path = shutil.which("tesseract")
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path
            return True
        
        # Common tesseract installation paths
        possible_paths = []
        
        if system == "windows":
            possible_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Users\%s\AppData\Local\Tesseract-OCR\tesseract.exe" % os.getenv('USERNAME', ''),
                r"C:\tesseract\tesseract.exe",
                r"C:\Tools\tesseract\tesseract.exe"
            ]
        elif system == "darwin":  # macOS
            possible_paths = [
                "/usr/local/bin/tesseract",
                "/opt/homebrew/bin/tesseract",
                "/usr/bin/tesseract",
                "/opt/local/bin/tesseract"  # MacPorts
            ]
        else:  # Linux and others
            possible_paths = [
                "/usr/bin/tesseract",
                "/usr/local/bin/tesseract",
                "/bin/tesseract",
                "/snap/bin/tesseract"  # Snap packages
            ]
        
        # Try each path
        for path in possible_paths:
            if os.path.exists(path) and os.path.isfile(path):
                pytesseract.pytesseract.tesseract_cmd = path
                return True
        
        return False
    
    def manual_tesseract_config(self, custom_path):
        """Manually set tesseract path"""
        import os
        
        if custom_path and os.path.exists(custom_path):
            pytesseract.pytesseract.tesseract_cmd = custom_path
            return True
        return False
    
    def debug_tesseract_installation(self):
        """Debug tesseract installation and provide detailed info"""
        import platform
        import os
        import shutil
        
        debug_info = {
            "system": platform.system(),
            "python_version": platform.python_version(),
            "current_tesseract_cmd": getattr(pytesseract.pytesseract, 'tesseract_cmd', 'Not set'),
            "tesseract_in_path": bool(shutil.which("tesseract")),
            "path_locations": []
        }
        
        # Check common locations
        system = platform.system().lower()
        possible_paths = []
        
        if system == "windows":
            possible_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"
            ]
        elif system == "darwin":
            possible_paths = [
                "/usr/local/bin/tesseract",
                "/opt/homebrew/bin/tesseract",
                "/usr/bin/tesseract"
            ]
        else:
            possible_paths = [
                "/usr/bin/tesseract",
                "/usr/local/bin/tesseract"
            ]
        
        for path in possible_paths:
            if os.path.exists(path):
                debug_info["path_locations"].append(f"✅ Found: {path}")
            else:
                debug_info["path_locations"].append(f"❌ Not found: {path}")
        
        return debug_info
    
    def preprocess_image(self, image: Image.Image) -> Image.Image:
        """Advanced image preprocessing for better OCR accuracy"""
        try:
            # Convert to numpy array
            img_array = np.array(image)
            
            # Convert to grayscale if needed
            if len(img_array.shape) == 3:
                if CV2_AVAILABLE:
                    img_array = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                else:
                    # Fallback grayscale conversion
                    img_array = np.dot(img_array[...,:3], [0.2989, 0.5870, 0.1140])
            
            if CV2_AVAILABLE:
                # Apply advanced preprocessing with OpenCV
                img_array = cv2.bilateralFilter(img_array.astype(np.uint8), 9, 75, 75)
                img_array = cv2.adaptiveThreshold(
                    img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                    cv2.THRESH_BINARY, 11, 2
                )
                kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
                img_array = cv2.morphologyEx(img_array, cv2.MORPH_CLOSE, kernel)
            else:
                # Fallback processing without OpenCV
                img_array = img_array.astype(np.uint8)
                # Simple thresholding
                threshold = np.mean(img_array)
                img_array = np.where(img_array > threshold, 255, 0).astype(np.uint8)
            
            # Invert if background is dark
            if np.mean(img_array) < 127:
                img_array = 255 - img_array
            
            # Convert back to PIL Image
            processed_image = Image.fromarray(img_array)
            
            # Resize for better OCR
            width, height = processed_image.size
            scale_factor = max(1, 300 / min(width, height))
            new_size = (int(width * scale_factor), int(height * scale_factor))
            processed_image = processed_image.resize(new_size, Image.LANCZOS)
            
            return processed_image
            
        except Exception as e:
            st.warning(f"Preprocessing error: {e}")
            return image
    
    def recognize_text(self, image: Image.Image) -> str:
        """Recognize text from image using OCR"""
        if not PYTESSERACT_AVAILABLE:
            return "OCR_NOT_AVAILABLE"
        
        try:
            # Preprocess the image
            processed_image = self.preprocess_image(image)
            
            # Configure Tesseract for mathematical expressions
            custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789+-*/=().,sincoatglnexpqrtpi'
            
            # OCR attempt
            recognized_text = pytesseract.image_to_string(processed_image, config=custom_config).strip()
            
            return recognized_text
            
        except Exception as e:
            st.warning(f"OCR Error: {e}")
            return ""
    
    def is_valid_expression(self, text_input: str) -> bool:
        """Check if the recognized text looks like a valid mathematical expression"""
        if not text_input or len(text_input.strip()) < 1:
            return False
        
        # Remove whitespace for checking
        text_clean = text_input.replace(" ", "")
        
        # Should contain at least one digit or mathematical symbol
        has_digit = any(c.isdigit() for c in text_clean)
        has_math = any(c in "+-*/=().,sincoatlnexpqrtpi" for c in text_clean)
        
        # Should not be too long (likely OCR error)
        reasonable_length = len(text_clean) < 100
        
        return (has_digit or has_math) and reasonable_length
    
    def post_process_text(self, text_input: str) -> str:
        """Clean and standardize the recognized text"""
        if not text_input:
            return ""
        
        # Remove extra whitespace
        text_processed = re.sub(r'\s+', '', text_input)
        
        # Replace common OCR errors
        for wrong, correct in self.symbol_mapping.items():
            text_processed = text_processed.replace(wrong, correct)
        
        # Fix common patterns
        text_processed = re.sub(r'(\d)([a-zA-Z])', r'\1*\2', text_processed)  # 2x -> 2*x
        text_processed = re.sub(r'([a-zA-Z])(\d)', r'\1*\2', text_processed)  # x2 -> x*2
        text_processed = re.sub(r'(\))(\d)', r'\1*\2', text_processed)        # )2 -> )*2
        text_processed = re.sub(r'(\d)(\()', r'\1*\2', text_processed)        # 2( -> 2*(
        
        # Remove equals sign if at the end
        text_processed = re.sub(r'=+$', '', text_processed)
        
        # Replace multiple operators
        text_processed = re.sub(r'\++', '+', text_processed)
        text_processed = re.sub(r'-+', '-', text_processed)
        text_processed = re.sub(r'\*+', '*', text_processed)
        text_processed = re.sub(r'/+', '/', text_processed)
        
        return text_processed
    
    def recognize_expression(self, canvas_data) -> tuple[str, float]:
        """Main method to recognize handwritten mathematical expression"""
        if not PYTESSERACT_AVAILABLE:
            return "Please install pytesseract: pip install pytesseract", 0.0
        
        if canvas_data is None or canvas_data.image_data is None:
            return "", 0.0
        
        try:
            # Convert canvas data to PIL Image
            image = Image.fromarray(canvas_data.image_data.astype('uint8'))
            
            # Check if image has content (not blank)
            img_array = np.array(image.convert('L'))
            if np.all(img_array == img_array[0, 0]):  # All pixels same color (blank)
                return "", 0.0
            
            # Recognize text
            raw_text = self.recognize_text(image)
            
            if not raw_text or raw_text == "OCR_NOT_AVAILABLE":
                return raw_text, 0.0
            
            # Post-process the text
            processed_text = self.post_process_text(raw_text)
            
            # Calculate confidence
            confidence = self.calculate_confidence(raw_text, processed_text, image)
            
            return processed_text, confidence
            
        except Exception as e:
            st.error(f"Recognition error: {e}")
            return "", 0.0
    
    def calculate_confidence(self, raw_text: str, processed_text: str, image: Image.Image) -> float:
        """Calculate confidence score for the recognition"""
        confidence = 0.5  # Base confidence
        
        # Factor 1: Text length (reasonable expressions get higher confidence)
        if 3 <= len(processed_text) <= 20:
            confidence += 0.2
        elif len(processed_text) > 20:
            confidence -= 0.1
        
        # Factor 2: Valid mathematical characters
        valid_chars = set('0123456789+-*/().,sincoatlnexpqrt')
        text_chars = set(processed_text.lower())
        if text_chars:
            valid_ratio = len(text_chars.intersection(valid_chars)) / len(text_chars)
            confidence += 0.3 * valid_ratio
        
        # Factor 3: Image quality indicators
        img_array = np.array(image.convert('L'))
        
        # Contrast check
        contrast = np.std(img_array)
        if contrast > 50:  # Good contrast
            confidence += 0.1
        
        # Size check
        width, height = image.size
        if width > 200 and height > 50:
            confidence += 0.1
        
        return min(confidence, 1.0)  # Cap at 1.0

class AdvancedCalculator:
    """Advanced calculator with multiple modes and features"""
    
    def __init__(self):
        self.initialize_session_state()
        # Check both global and session state for tesseract availability
        tesseract_available = PYTESSERACT_AVAILABLE or st.session_state.get('tesseract_working', False)
        if PYTESSERACT_IMPORT_SUCCESS and tesseract_available:
            self.handwriting_recognizer = HandwritingRecognizer()
        else:
            self.handwriting_recognizer = None
    
    def initialize_session_state(self):
        """Initialize session state variables"""
        if 'display' not in st.session_state:
            st.session_state.display = '0'
        if 'history' not in st.session_state:
            st.session_state.history = []
        if 'memory' not in st.session_state:
            st.session_state.memory = 0
        if 'last_result' not in st.session_state:
            st.session_state.last_result = 0
        if 'mode' not in st.session_state:
            st.session_state.mode = 'Basic'
        if 'theme' not in st.session_state:
            st.session_state.theme = 'Dark'
        if 'canvas_key' not in st.session_state:
            st.session_state.canvas_key = 0
        if 'last_recognized' not in st.session_state:
            st.session_state.last_recognized = ""
        if 'recognition_confidence' not in st.session_state:
            st.session_state.recognition_confidence = 0.0
        if 'tesseract_working' not in st.session_state:
            st.session_state.tesseract_working = False
    
    def add_to_history(self, expression: str, result: str, input_method: str = "manual"):
        """Add calculation to history"""
        history_item = CalculationHistory(
            timestamp=datetime.now().strftime("%H:%M:%S"),
            expression=expression,
            result=result,
            mode=st.session_state.mode,
            input_method=input_method
        )
        st.session_state.history.insert(0, history_item)
        # Keep only last 50 calculations
        st.session_state.history = st.session_state.history[:50]
    
    def safe_eval(self, expression: str) -> Union[float, str]:
        """Safely evaluate mathematical expressions"""
        try:
            # Replace common mathematical functions
            expr_clean = expression.replace('^', '**')
            expr_clean = expr_clean.replace('π', str(math.pi))
            expr_clean = expr_clean.replace('pi', str(math.pi))
            expr_clean = expr_clean.replace('e', str(math.e))
            
            if SYMPY_AVAILABLE:
                # Use sympy for safe evaluation
                result = float(parse_expr(expr_clean, transformations='all'))
            else:
                # Fallback: basic evaluation with math functions
                # Add math functions to the namespace
                safe_dict = {
                    "__builtins__": {},
                    "sin": math.sin, "cos": math.cos, "tan": math.tan,
                    "log": math.log10, "ln": math.log, "sqrt": math.sqrt,
                    "pi": math.pi, "e": math.e, "exp": math.exp,
                    "abs": abs, "pow": pow, "round": round
                }
                result = eval(expr_clean, safe_dict)
            
            return float(result)
        except Exception as e:
            return f"Error: {str(e)}"
    
    def format_number(self, num: Union[float, int]) -> str:
        """Format number for display"""
        if isinstance(num, (int, float)):
            if abs(num) >= 1e10 or (abs(num) < 1e-4 and num != 0):
                return f"{num:.4e}"
            elif num == int(num):
                return str(int(num))
            else:
                return f"{num:.8g}"
        return str(num)
    
    def render_display(self):
        """Render the calculator display"""
        st.markdown(f"""
        <div class="calculator-display">
            {st.session_state.display}
        </div>
        """, unsafe_allow_html=True)
    
    def basic_calculator(self):
        """Basic calculator interface"""
        # Number pad and operations
        col1, col2, col3, col4 = st.columns(4)
        
        # Row 1
        with col1:
            if st.button("C", key="clear", help="Clear"):
                st.session_state.display = '0'
                st.rerun()
        with col2:
            if st.button("⌫", key="backspace", help="Backspace"):
                if len(st.session_state.display) > 1:
                    st.session_state.display = st.session_state.display[:-1]
                else:
                    st.session_state.display = '0'
                st.rerun()
        with col3:
            if st.button("±", key="plusminus", help="Plus/Minus"):
                try:
                    current = float(st.session_state.display)
                    st.session_state.display = self.format_number(-current)
                    st.rerun()
                except:
                    pass
        with col4:
            if st.button("÷", key="divide", help="Divide"):
                self.append_to_display('/')
        
        # Row 2
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("7", key="seven"):
                self.append_to_display('7')
        with col2:
            if st.button("8", key="eight"):
                self.append_to_display('8')
        with col3:
            if st.button("9", key="nine"):
                self.append_to_display('9')
        with col4:
            if st.button("×", key="multiply", help="Multiply"):
                self.append_to_display('*')
        
        # Row 3
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("4", key="four"):
                self.append_to_display('4')
        with col2:
            if st.button("5", key="five"):
                self.append_to_display('5')
        with col3:
            if st.button("6", key="six"):
                self.append_to_display('6')
        with col4:
            if st.button("−", key="subtract", help="Subtract"):
                self.append_to_display('-')
        
        # Row 4
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("1", key="one"):
                self.append_to_display('1')
        with col2:
            if st.button("2", key="two"):
                self.append_to_display('2')
        with col3:
            if st.button("3", key="three"):
                self.append_to_display('3')
        with col4:
            if st.button("+", key="add", help="Add"):
                self.append_to_display('+')
        
        # Row 5
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("0", key="zero"):
                self.append_to_display('0')
        with col2:
            if st.button(".", key="decimal", help="Decimal"):
                self.append_to_display('.')
        with col3:
            if st.button("=", key="equals", help="Calculate"):
                self.calculate()
        with col4:
            if st.button("π", key="pi", help="Pi"):
                self.append_to_display('pi')
    
    def scientific_calculator(self):
        """Scientific calculator interface"""
        # Scientific functions
        col1, col2, col3, col4, col5 = st.columns(5)
        
        # Row 1 - Advanced functions
        with col1:
            if st.button("sin", key="sin"):
                self.append_to_display('sin(')
        with col2:
            if st.button("cos", key="cos"):
                self.append_to_display('cos(')
        with col3:
            if st.button("tan", key="tan"):
                self.append_to_display('tan(')
        with col4:
            if st.button("log", key="log"):
                self.append_to_display('log(')
        with col5:
            if st.button("ln", key="ln"):
                self.append_to_display('ln(')
        
        # Row 2
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            if st.button("√", key="sqrt"):
                self.append_to_display('sqrt(')
        with col2:
            if st.button("x²", key="square"):
                self.append_to_display('**2')
        with col3:
            if st.button("x^y", key="power"):
                self.append_to_display('**')
        with col4:
            if st.button("(", key="open_paren"):
                self.append_to_display('(')
        with col5:
            if st.button(")", key="close_paren"):
                self.append_to_display(')')
        
        # Include basic calculator
        self.basic_calculator()
    
    def programmer_calculator(self):
        """Programmer calculator for different number bases"""
        st.subheader("🔢 Base Conversion")
        
        # Input number
        col1, col2 = st.columns(2)
        with col1:
            input_base = st.selectbox("Input Base", ["Decimal", "Binary", "Octal", "Hexadecimal"])
        with col2:
            number_input = st.text_input("Enter number", st.session_state.display)
        
        if number_input:
            try:
                # Convert to decimal first
                if input_base == "Decimal":
                    decimal_val = int(number_input)
                elif input_base == "Binary":
                    decimal_val = int(number_input, 2)
                elif input_base == "Octal":
                    decimal_val = int(number_input, 8)
                else:  # Hexadecimal
                    decimal_val = int(number_input, 16)
                
                # Display conversions
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Decimal", str(decimal_val))
                with col2:
                    st.metric("Binary", bin(decimal_val)[2:])
                with col3:
                    st.metric("Octal", oct(decimal_val)[2:])
                with col4:
                    st.metric("Hex", hex(decimal_val)[2:].upper())
                
                # Bitwise operations
                st.subheader("🔧 Bitwise Operations")
                col1, col2, col3 = st.columns(3)
                with col1:
                    other_num = st.number_input("Second number (decimal)", value=0)
                with col2:
                    operation = st.selectbox("Operation", ["AND", "OR", "XOR", "NOT", "Left Shift", "Right Shift"])
                
                if operation and other_num is not None:
                    with col3:
                        if operation == "AND":
                            result = decimal_val & int(other_num)
                        elif operation == "OR":
                            result = decimal_val | int(other_num)
                        elif operation == "XOR":
                            result = decimal_val ^ int(other_num)
                        elif operation == "NOT":
                            result = ~decimal_val
                        elif operation == "Left Shift":
                            result = decimal_val << int(other_num)
                        else:  # Right Shift
                            result = decimal_val >> int(other_num)
                        
                        st.metric("Result", f"{result} ({bin(result)[2:]})")
            
            except ValueError:
                st.error("Invalid number format for selected base")
    
    def unit_converter(self):
        """Unit conversion calculator"""
        st.subheader("📏 Unit Converter")
        
        conversion_types = {
            "Length": {
                "meters": 1,
                "kilometers": 1000,
                "centimeters": 0.01,
                "millimeters": 0.001,
                "inches": 0.0254,
                "feet": 0.3048,
                "yards": 0.9144,
                "miles": 1609.34
            },
            "Weight": {
                "grams": 1,
                "kilograms": 1000,
                "pounds": 453.592,
                "ounces": 28.3495,
                "tons": 1000000
            },
            "Temperature": {
                "celsius": "base",
                "fahrenheit": "special",
                "kelvin": "special"
            }
        }
        
        col1, col2, col3 = st.columns(3)
        with col1:
            conv_type = st.selectbox("Conversion Type", list(conversion_types.keys()))
        with col2:
            from_unit = st.selectbox("From", list(conversion_types[conv_type].keys()))
        with col3:
            to_unit = st.selectbox("To", list(conversion_types[conv_type].keys()))
        
        value = st.number_input("Enter value", value=1.0)
        
        if conv_type == "Temperature":
            # Special handling for temperature
            if from_unit == "celsius":
                if to_unit == "fahrenheit":
                    result = (value * 9/5) + 32
                elif to_unit == "kelvin":
                    result = value + 273.15
                else:
                    result = value
            elif from_unit == "fahrenheit":
                if to_unit == "celsius":
                    result = (value - 32) * 5/9
                elif to_unit == "kelvin":
                    result = (value - 32) * 5/9 + 273.15
                else:
                    result = value
            else:  # kelvin
                if to_unit == "celsius":
                    result = value - 273.15
                elif to_unit == "fahrenheit":
                    result = (value - 273.15) * 9/5 + 32
                else:
                    result = value
        else:
            # Standard unit conversion
            from_factor = conversion_types[conv_type][from_unit]
            to_factor = conversion_types[conv_type][to_unit]
            result = value * from_factor / to_factor
        
        st.success(f"{value} {from_unit} = {result:.6g} {to_unit}")
    
    def render_handwriting_canvas(self):
        """Render the handwriting recognition canvas"""
        if not CANVAS_AVAILABLE:
            st.error("🎨 Canvas not available. Please install: pip install streamlit-drawable-canvas")
            return
        
        # Check both global variable and session state for tesseract availability
        tesseract_available = PYTESSERACT_AVAILABLE or st.session_state.get('tesseract_working', False)
        
        if not tesseract_available:
            st.error("👁️ Tesseract OCR not available!")
            
            # Show detailed troubleshooting
            with st.expander("🔧 TROUBLESHOOTING GUIDE", expanded=True):
                st.markdown("### 🎯 **Step-by-Step Fix:**")
                
                # Step 1: Check Python package
                st.markdown("**STEP 1: Verify Python Package**")
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.code("pip show pytesseract")
                with col2:
                    if st.button("🔍 Check"):
                        try:
                            import pytesseract
                            st.success("✅ Installed")
                        except:
                            st.error("❌ Missing")
                
                # Step 2: Install/Reinstall Tesseract
                st.markdown("**STEP 2: Install Tesseract OCR Engine**")
                
                import platform
                system = platform.system()
                
                if system == "Windows":
                    st.markdown("""
                    **Windows Options:**
                    ```bash
                    # Option A: Download installer (RECOMMENDED)
                    # 1. Go to: https://github.com/UB-Mannheim/tesseract/wiki
                    # 2. Download Windows installer
                    # 3. Install to: C:\\Program Files\\Tesseract-OCR\\
                    # 4. Restart this app
                    
                    # Option B: Chocolatey
                    choco install tesseract
                    
                    # Option C: Winget
                    winget install --id UB-Mannheim.TesseractOCR
                    ```
                    """)
                elif system == "Darwin":  # macOS
                    st.markdown("""
                    **macOS Commands:**
                    ```bash
                    # Option A: Homebrew (RECOMMENDED)
                    brew install tesseract
                    
                    # Option B: MacPorts
                    sudo port install tesseract
                    
                    # Then restart this app
                    ```
                    """)
                else:  # Linux
                    st.markdown("""
                    **Linux Commands:**
                    ```bash
                    # Ubuntu/Debian
                    sudo apt update
                    sudo apt install tesseract-ocr
                    
                    # CentOS/RHEL/Fedora
                    sudo dnf install tesseract
                    
                    # Arch Linux
                    sudo pacman -S tesseract
                    
                    # Then restart this app
                    ```
                    """)
                
                # Step 3: Verify Installation
                st.markdown("**STEP 3: Test Installation**")
                st.code("tesseract --version")
                st.markdown("👆 Run this in your terminal. You should see version info.")
                
                # Step 4: Manual Path Configuration
                st.markdown("**STEP 4: Manual Path (if still not working)**")
                manual_path = st.text_input(
                    "Enter full path to tesseract executable:",
                    placeholder={
                        "Windows": "C:\\Program Files\\Tesseract-OCR\\tesseract.exe",
                        "Darwin": "/usr/local/bin/tesseract", 
                        "Linux": "/usr/bin/tesseract"
                    }.get(system, "/usr/bin/tesseract")
                )
                
                if st.button("🚀 Apply Manual Path") and manual_path:
                    import os
                    if os.path.exists(manual_path):
                        if PYTESSERACT_IMPORT_SUCCESS:
                            pytesseract.pytesseract.tesseract_cmd = manual_path
                            try:
                                version = pytesseract.get_tesseract_version()
                                st.success(f"🎉 SUCCESS! Tesseract {version} configured!")
                                # Store success in session state instead of modifying global
                                st.session_state.tesseract_working = True
                                st.rerun()
                            except Exception as e:
                                st.error(f"❌ Still not working: {str(e)}")
                        else:
                            st.error("❌ PyTesseract package issue")
                    else:
                        st.error("❌ Path doesn't exist!")
                
                # Quick diagnostic
                st.markdown("**STEP 5: Quick Diagnostic**")
                if st.button("🩺 Run Diagnostic"):
                    st.write("**Diagnostic Results:**")
                    
                    # Check pytesseract import
                    try:
                        import pytesseract as pt
                        st.success("✅ pytesseract imports successfully")
                        
                        # Check current tesseract command
                        current_cmd = getattr(pt.pytesseract, 'tesseract_cmd', 'tesseract')
                        st.info(f"📍 Current tesseract command: {current_cmd}")
                        
                        # Try to run tesseract
                        try:
                            version = pt.get_tesseract_version()
                            st.success(f"✅ Tesseract {version} is accessible!")
                            # Store success in session state
                            st.session_state.tesseract_working = True
                            st.balloons()
                            st.rerun()
                        except pt.TesseractNotFoundError:
                            st.error("❌ Tesseract binary not found in system PATH")
                        except Exception as e:
                            st.error(f"❌ Tesseract error: {str(e)}")
                            
                    except ImportError as e:
                        st.error(f"❌ pytesseract import failed: {str(e)}")
                        st.code("pip install --upgrade pytesseract")
                    
                    # Check system PATH
                    import os
                    path_env = os.environ.get('PATH', '')
                    if 'tesseract' in path_env.lower():
                        st.success("✅ Tesseract found in PATH")
                    else:
                        st.warning("⚠️ Tesseract not found in PATH")
            
            st.info("📝 You can still use other calculator modes while fixing this!")
            return
        
        # If we get here, OCR is available!
        st.subheader("✍️ Handwrite Your Equation")
        st.markdown('<div class="ai-badge">🤖 AI-Powered Recognition</div>', unsafe_allow_html=True)
        
        # Canvas controls
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            stroke_width = st.slider("Pen Width", 2, 10, 4)
        with col2:
            stroke_color = st.color_picker("Pen Color", "#000000")
        with col3:
            bg_color = st.color_picker("Background", "#FFFFFF")
        with col4:
            canvas_height = st.slider("Canvas Height", 200, 400, 250)
        
        # Create the canvas
        canvas_result = st_canvas(
            fill_color="rgba(255, 165, 0, 0.3)",
            stroke_width=stroke_width,
            stroke_color=stroke_color,
            background_color=bg_color,
            background_image=None,
            update_streamlit=True,
            width=600,
            height=canvas_height,
            drawing_mode="freedraw",
            point_display_radius=0,
            key=f"canvas_{st.session_state.canvas_key}",
            display_toolbar=True,
        )
        
        # Canvas controls
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("🔍 Recognize", type="primary"):
                if canvas_result.image_data is not None:
                    with st.spinner("🤖 Analyzing handwriting..."):
                        try:
                            recognized_text, confidence = self.handwriting_recognizer.recognize_expression(canvas_result)
                            
                            if recognized_text and not recognized_text.startswith("Please install") and not recognized_text.startswith("OCR Error"):
                                st.session_state.last_recognized = recognized_text
                                st.session_state.recognition_confidence = confidence
                                
                                # Display recognition result
                                st.markdown(f"""
                                <div class="recognition-result">
                                    📝 Recognized: <strong>{recognized_text}</strong>
                                    <br>🎯 Confidence: {confidence:.1%}
                                </div>
                                """, unsafe_allow_html=True)
                                
                                # Auto-calculate if confidence is high
                                if confidence > 0.7:
                                    st.session_state.display = recognized_text
                                    self.calculate_expression(recognized_text, "handwritten")
                                    st.success("✅ Automatically calculated!")
                                else:
                                    st.warning("⚠️ Low confidence. Please verify the expression.")
                                    st.session_state.display = recognized_text
                            else:
                                st.error("❌ Could not recognize the expression.")
                                if recognized_text.startswith("OCR Error") or recognized_text.startswith("Please install"):
                                    st.error(recognized_text)
                        except Exception as e:
                            st.error(f"Recognition failed: {str(e)}")
                            if "tesseract" in str(e).lower():
                                st.info("💡 This looks like a Tesseract installation issue. Check the troubleshooting guide!")
                else:
                    st.warning("⚠️ Please draw something on the canvas first!")
        
        with col2:
            if st.button("🧹 Clear Canvas"):
                st.session_state.canvas_key += 1
                st.rerun()
        
        with col3:
            if st.button("📋 Use Recognized"):
                if st.session_state.last_recognized:
                    st.session_state.display = st.session_state.last_recognized
                    st.rerun()
                else:
                    st.warning("No recognized expression to use!")
        
        with col4:
            if st.button("🧮 Calculate"):
                if st.session_state.last_recognized:
                    self.calculate_expression(st.session_state.last_recognized, "handwritten")
                else:
                    st.warning("No expression to calculate!")
        
        # Show recent recognition if available
        if st.session_state.last_recognized:
            with st.expander("📊 Recognition Details", expanded=False):
                st.write(f"**Last Recognized:** {st.session_state.last_recognized}")
                st.write(f"**Confidence:** {st.session_state.recognition_confidence:.1%}")
                
                # Simple confidence bar (fallback if plotly not available)
                confidence_percent = int(st.session_state.recognition_confidence * 100)
                st.progress(st.session_state.recognition_confidence, text=f"Confidence: {confidence_percent}%")
        
        # Tips for better recognition
        with st.expander("💡 Tips for Better Recognition", expanded=False):
            st.markdown("""
            **For best results:**
            - ✍️ Write clearly and large
            - 🔢 Use standard mathematical symbols
            - 📏 Keep numbers and operators well-spaced  
            - 🎯 Write horizontally (left to right)
            - 🖊️ Use consistent pen width
            - 🎨 Use high contrast colors (black on white works best)
            - 📐 Avoid complex fractions (use / instead)
            - ✅ Write simple expressions first to test
            
            **Supported symbols:**
            - Numbers: 0-9
            - Operations: + - * / = ( )
            - Functions: sin cos tan log ln sqrt
            - Constants: pi e
            
            **Common issues:**
            - Make sure Tesseract OCR is properly installed
            - Write clearly - OCR struggles with messy handwriting
            - Use good contrast between pen and background
            """)
        
        # Test OCR functionality
        with st.expander("🧪 Test OCR", expanded=False):
            if st.button("Test Tesseract Installation"):
                try:
                    version = pytesseract.get_tesseract_version()
                    st.success(f"✅ Tesseract {version} is working!")
                except Exception as e:
                    st.error(f"❌ Tesseract test failed: {str(e)}")
                    st.info("Please follow the troubleshooting guide above.")
    
    def append_to_display(self, value: str):
        """Append value to display"""
        if st.session_state.display == '0' and value.isdigit():
            st.session_state.display = value
        else:
            st.session_state.display += value
        st.rerun()
    
    def calculate_expression(self, expression: str, input_method: str = "manual"):
        """Calculate expression with specified input method"""
        try:
            result = self.safe_eval(expression)
            
            if isinstance(result, str):  # Error case
                st.error(result)
                return
            
            formatted_result = self.format_number(result)
            self.add_to_history(expression, formatted_result, input_method)
            st.session_state.display = formatted_result
            st.session_state.last_result = result
            
            # Show calculation result
            st.success(f"✅ {expression} = {formatted_result}")
            
            if input_method == "handwritten":
                st.balloons()  # Celebrate handwriting recognition success!
            
            st.rerun()
            
        except Exception as e:
            st.error(f"Calculation error: {str(e)}")
    
    def calculate(self):
        """Perform calculation (wrapper for backward compatibility)"""
        expression = st.session_state.display
        self.calculate_expression(expression, "manual")
    
    def render_history(self):
        """Render calculation history"""
        if st.session_state.history:
            st.subheader("📊 History")
            for i, calc in enumerate(st.session_state.history[:10]):  # Show last 10
                # Input method icon
                input_icon = "✍️" if calc.input_method == "handwritten" else "⌨️"
                mode_icon = {"Basic": "🔢", "Scientific": "🧪", "Programmer": "💻", "Unit Converter": "📏"}.get(calc.mode, "🧮")
                
                with st.expander(f"{input_icon} {calc.timestamp} - {mode_icon} {calc.mode}", expanded=False):
                    st.code(f"{calc.expression} = {calc.result}")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button(f"Use Result", key=f"use_result_{i}"):
                            st.session_state.display = calc.result
                            st.rerun()
                    with col2:
                        if st.button(f"Use Expression", key=f"use_expr_{i}"):
                            st.session_state.display = calc.expression
                            st.rerun()
                    
                    # Show input method badge
                    method_color = "#ff9a9e" if calc.input_method == "handwritten" else "#a8e6cf"
                    st.markdown(f"""
                    <div style="background: {method_color}; color: #2c3e50; padding: 5px 10px; border-radius: 15px; 
                                display: inline-block; font-size: 0.8rem; margin-top: 5px;">
                        {input_icon} {calc.input_method.title()} Input
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info("No calculations yet")
    
    def render_memory_functions(self):
        """Render memory functions"""
        st.subheader("💾 Memory")
        st.write(f"Memory: {self.format_number(st.session_state.memory)}")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            if st.button("MC", help="Memory Clear"):
                st.session_state.memory = 0
                st.success("Memory cleared")
        with col2:
            if st.button("MR", help="Memory Recall"):
                st.session_state.display = self.format_number(st.session_state.memory)
                st.rerun()
        with col3:
            if st.button("M+", help="Memory Add"):
                try:
                    st.session_state.memory += float(st.session_state.display)
                    st.success("Added to memory")
                except:
                    st.error("Invalid number")
        with col4:
            if st.button("M-", help="Memory Subtract"):
                try:
                    st.session_state.memory -= float(st.session_state.display)
                    st.success("Subtracted from memory")
                except:
                    st.error("Invalid number")
    
    def render_graph(self):
        """Render function graphing"""
        st.subheader("📈 Function Grapher")
        
        function_input = st.text_input("Enter function (use x as variable)", "x**2")
        col1, col2 = st.columns(2)
        with col1:
            x_min = st.number_input("X min", value=-10.0)
            x_max = st.number_input("X max", value=10.0)
        
        if function_input:
            try:
                x = np.linspace(x_min, x_max, 1000)
                # Replace common math functions for numpy
                func_str = function_input.replace('^', '**')
                func_str = func_str.replace('sin', 'np.sin')
                func_str = func_str.replace('cos', 'np.cos')
                func_str = func_str.replace('tan', 'np.tan')
                func_str = func_str.replace('log', 'np.log10')
                func_str = func_str.replace('ln', 'np.log')
                func_str = func_str.replace('sqrt', 'np.sqrt')
                func_str = func_str.replace('exp', 'np.exp')
                
                y = eval(func_str)
                
                if PLOTLY_AVAILABLE:
                    fig = go.Figure(data=go.Scatter(x=x, y=y, mode='lines', name=function_input))
                    fig.update_layout(
                        title=f"Graph of y = {function_input}",
                        xaxis_title="x",
                        yaxis_title="y",
                        template="plotly_dark"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    # Fallback: Simple line chart using streamlit
                    import pandas as pd
                    df = pd.DataFrame({'x': x, 'y': y})
                    st.line_chart(df.set_index('x'))
                
            except Exception as e:
                st.error(f"Error plotting function: {str(e)}")
    
    def export_history(self):
        """Export calculation history"""
        if st.session_state.history:
            df = pd.DataFrame([asdict(calc) for calc in st.session_state.history])
            
            col1, col2 = st.columns(2)
            with col1:
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📄 Download as CSV",
                    data=csv,
                    file_name=f"calculator_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            with col2:
                json_data = df.to_json(orient="records", indent=2)
                st.download_button(
                    label="📋 Download as JSON",
                    data=json_data,
                    file_name=f"calculator_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )

def main():
    """Main application function"""
    st.markdown('<h1 class="main-title">🧮 Advanced Calculator Pro</h1>', unsafe_allow_html=True)
    
    # Show package status
    missing_packages = []
    if not PLOTLY_AVAILABLE:
        missing_packages.append("plotly")
    if not SYMPY_AVAILABLE:
        missing_packages.append("sympy") 
    if not CV2_AVAILABLE:
        missing_packages.append("opencv-python")
    if not PYTESSERACT_AVAILABLE:
        missing_packages.append("pytesseract")
    if not CANVAS_AVAILABLE:
        missing_packages.append("streamlit-drawable-canvas")
    
    if missing_packages:
        with st.expander("📦 Optional Packages", expanded=False):
            st.info(f"Install these for full functionality: {', '.join(missing_packages)}")
            st.code(f"pip install {' '.join(missing_packages)}")
    
    # Initialize calculator
    calc = AdvancedCalculator()
    
    # Store in session state for debugging access
    st.session_state.calc = calc
    
    # Sidebar for settings and modes
    with st.sidebar:
        st.header("⚙️ Settings")
        
        # Mode selection
        available_modes = ["Basic", "Scientific", "Programmer", "Unit Converter"]
        tesseract_available = PYTESSERACT_AVAILABLE or st.session_state.get('tesseract_working', False)
        if CANVAS_AVAILABLE and (PYTESSERACT_IMPORT_SUCCESS and tesseract_available):
            available_modes.append("Handwriting")
        
        current_mode_index = 0
        if st.session_state.mode in available_modes:
            current_mode_index = available_modes.index(st.session_state.mode)
        
        st.session_state.mode = st.selectbox(
            "Calculator Mode",
            available_modes,
            index=current_mode_index
        )
        
        # Theme selection
        st.session_state.theme = st.selectbox("Theme", ["Dark", "Light"])
        
        # Quick input
        st.subheader("⚡ Quick Input")
        quick_expr = st.text_input("Enter expression directly")
        if st.button("Calculate Expression") and quick_expr:
            st.session_state.display = quick_expr
            calc.calculate()
        
        # Memory functions
        calc.render_memory_functions()
        
        # Statistics about usage
        st.subheader("📊 Statistics")
        total_calcs = len(st.session_state.history)
        if total_calcs > 0:
            st.metric("Total Calculations", total_calcs)
            
            # Count by input method
            handwritten_count = sum(1 for calc_item in st.session_state.history if calc_item.input_method == "handwritten")
            manual_count = total_calcs - handwritten_count
            
            if handwritten_count > 0:
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("✍️ Handwritten", handwritten_count)
                with col2:
                    st.metric("⌨️ Manual", manual_count)
            
            # Mode statistics
            mode_counts = {}
            for calc_item in st.session_state.history:
                mode_counts[calc_item.mode] = mode_counts.get(calc_item.mode, 0) + 1
            most_used_mode = max(mode_counts, key=mode_counts.get)
            st.metric("Most Used Mode", most_used_mode)
            
            # Average confidence for handwritten calculations
            if st.session_state.recognition_confidence > 0:
                st.metric("Last Recognition", f"{st.session_state.recognition_confidence:.1%}")
        
        # AI Recognition Status
        tesseract_available = PYTESSERACT_AVAILABLE or st.session_state.get('tesseract_working', False)
        if PYTESSERACT_IMPORT_SUCCESS and CANVAS_AVAILABLE and tesseract_available:
            st.subheader("🤖 AI Status")
            if st.session_state.last_recognized:
                st.success("✅ Recognition Active")
                st.write(f"**Last:** {st.session_state.last_recognized}")
            else:
                st.info("🎯 Ready for handwriting")
        else:
            st.subheader("🤖 AI Status")
            st.warning("📦 Install packages for AI features")
    
    # Main calculator interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Display
        calc.render_display()
        
        # Mode-specific interface
        if st.session_state.mode == "Basic":
            calc.basic_calculator()
        elif st.session_state.mode == "Scientific":
            calc.scientific_calculator()
        elif st.session_state.mode == "Programmer":
            calc.programmer_calculator()
        elif st.session_state.mode == "Unit Converter":
            calc.unit_converter()
        elif st.session_state.mode == "Handwriting":
            # Special layout for handwriting mode
            st.info("🎨 Draw your mathematical expression below and let AI solve it!")
            calc.render_handwriting_canvas()
            
            # Show quick reference
            with st.expander("🔗 Quick Actions", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    if st.button("📝 Try: 2+3", key="demo_1"):
                        st.session_state.display = "2+3"
                        calc.calculate_expression("2+3", "manual")
                with col2:
                    if st.button("📝 Try: sqrt(16)", key="demo_2"):
                        st.session_state.display = "sqrt(16)"
                        calc.calculate_expression("sqrt(16)", "manual")
                with col3:
                    if st.button("📝 Try: pi*2", key="demo_3"):
                        st.session_state.display = "pi*2"
                        calc.calculate_expression("pi*2", "manual")
        
        # Function graphing (for scientific mode)
        if st.session_state.mode == "Scientific":
            with st.expander("📈 Function Grapher", expanded=False):
                calc.render_graph()
    
    with col2:
        # History
        calc.render_history()
        
        # Export options
        if st.session_state.history:
            st.subheader("📤 Export")
            calc.export_history()
        
        # Help section
        with st.expander("❓ Help", expanded=False):
            st.markdown("""
            **Keyboard Shortcuts:**
            - Numbers: 0-9
            - Operations: +, -, *, /
            - Enter: Calculate
            - Esc: Clear
            
            **Scientific Functions:**
            - sin, cos, tan: Trigonometric functions
            - log: Base-10 logarithm
            - ln: Natural logarithm
            - sqrt: Square root
            - pi: π constant
            - e: Euler's number
            
            **🤖 AI Handwriting Recognition:**
            - Draw equations on the canvas
            - AI automatically recognizes mathematical symbols
            - Supports numbers, operators, and functions
            - High accuracy with clear handwriting
            - Auto-calculates when confidence > 70%
            
            **Tips:**
            - Use parentheses for complex expressions
            - Memory functions store values across calculations
            - History shows your last 50 calculations
            - Export your calculation history as CSV/JSON
            - Install optional packages for full features!
            """)
    
    # Add installation note for required packages
    with st.sidebar:
        with st.expander("📦 Installation Guide", expanded=False):
            st.markdown("""
            **STEP 1: Python Packages**
            ```bash
            # Essential packages
            pip install streamlit pandas numpy pillow
            
            # For handwriting recognition
            pip install streamlit-drawable-canvas pytesseract opencv-python
            
            # For advanced features  
            pip install sympy plotly
            ```
            
            **STEP 2: Tesseract OCR Engine**
            
            **Windows:**
            1. Download installer from:
               https://github.com/UB-Mannheim/tesseract/wiki
            2. Install to default location
            3. Restart Streamlit
            
            OR use Chocolatey:
            ```bash
            choco install tesseract
            ```
            
            **macOS:**
            ```bash
            # Using Homebrew (recommended)
            brew install tesseract
            
            # Using MacPorts
            sudo port install tesseract
            ```
            
            **Linux (Ubuntu/Debian):**
            ```bash
            sudo apt update
            sudo apt install tesseract-ocr
            sudo apt install libtesseract-dev  # for development
            ```
            
            **Linux (CentOS/RHEL/Fedora):**
            ```bash
            sudo yum install tesseract
            # OR for newer versions:
            sudo dnf install tesseract
            ```
            
            **Docker:**
            ```dockerfile
            RUN apt-get update && apt-get install -y tesseract-ocr
            ```
            
            **Verification:**
            After installation, test in terminal:
            ```bash
            tesseract --version
            ```
            
            **Troubleshooting:**
            - Make sure Tesseract is in your PATH
            - Restart your terminal and Streamlit after installation
            - On Windows, installer usually adds to PATH automatically
            - On macOS/Linux, Homebrew/apt usually handles PATH
            """)
        
        # Show current OCR status with detailed debugging
        st.subheader("🔧 OCR Status")
        
        if PYTESSERACT_IMPORT_SUCCESS:
            st.success("✅ PyTesseract package imported")
            
            if PYTESSERACT_AVAILABLE:
                try:
                    version = pytesseract.get_tesseract_version()
                    st.success(f"✅ Tesseract {version} working!")
                except Exception as e:
                    st.error(f"❌ Tesseract error: {str(e)}")
            else:
                st.error("❌ Tesseract binary not found")
                
                # Manual path configuration
                st.subheader("🛠️ Manual Configuration")
                custom_path = st.text_input(
                    "Tesseract path:", 
                    placeholder="e.g., C:\\Program Files\\Tesseract-OCR\\tesseract.exe"
                )
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔍 Find Tesseract"):
                        import shutil
                        found_path = shutil.which("tesseract")
                        if found_path:
                            st.success(f"Found: {found_path}")
                            if st.button("Use This Path"):
                                pytesseract.pytesseract.tesseract_cmd = found_path
                                st.rerun()
                        else:
                            st.error("Not found in PATH")
                
                with col2:
                    if st.button("✅ Apply Path") and custom_path:
                        import os
                        if os.path.exists(custom_path):
                            pytesseract.pytesseract.tesseract_cmd = custom_path
                            st.success("Path updated! Test below.")
                            st.rerun()
                        else:
                            st.error("Path doesn't exist!")
        else:
            st.error("❌ PyTesseract not installed")
            if st.button("📦 Reinstall PyTesseract"):
                st.code("pip install --upgrade --force-reinstall pytesseract")
        
        # Debug information
        with st.expander("🐛 Debug Info", expanded=False):
            if PYTESSERACT_IMPORT_SUCCESS and hasattr(st.session_state, 'calc') and hasattr(st.session_state.calc, 'handwriting_recognizer'):
                try:
                    debug_info = st.session_state.calc.handwriting_recognizer.debug_tesseract_installation()
                    st.json(debug_info)
                except:
                    pass
            
            # Show environment info
            import platform
            import os
            st.write("**System Info:**")
            st.write(f"- OS: {platform.system()} {platform.release()}")
            st.write(f"- Python: {platform.python_version()}")
            st.write(f"- PATH contains tesseract: {'tesseract' in os.environ.get('PATH', '')}")
            
            # Try to show current tesseract command
            if PYTESSERACT_IMPORT_SUCCESS:
                current_cmd = getattr(pytesseract.pytesseract, 'tesseract_cmd', 'Default (tesseract)')
                st.write(f"- Current tesseract cmd: {current_cmd}")
        
        # Quick tesseract test button
        if st.button("🧪 Test OCR Now"):
            if PYTESSERACT_IMPORT_SUCCESS:
                try:
                    # Try to get version
                    version = pytesseract.get_tesseract_version()
                    st.success(f"🎉 SUCCESS! Tesseract {version} is working!")
                    
                    # Note: Can't modify global here, but we can update session state
                    st.session_state.tesseract_working = True
                    st.rerun()
                    
                except pytesseract.TesseractNotFoundError as e:
                    st.error(f"❌ Tesseract not found: {str(e)}")
                    st.info("💡 Try the manual configuration above!")
                except Exception as e:
                    st.error(f"❌ Test failed: {str(e)}")
                    st.info("💡 Check the debug info above for more details.")
            else:
                st.error("❌ PyTesseract not available. Try reinstalling.")

if __name__ == "__main__":
    main()