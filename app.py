# This code is add to add the .pth files from the drive 
import os
import gdown
import torch
import streamlit as st
from torchvision import models

# Google Drive file IDs
MODEL_URLS = {
    "Wheat": "https://drive.google.com/file/d/1md2rJv3E3UY_rNXou3a33RcGpWbVS1sY/view?usp=drive_link",
    "Cotton": "https://drive.google.com/file/d/13b0_Yo1t2CaYX6yM6hfoYP2DrTmgRy4z/view?usp=drive_link"
}

MODEL_FILES = {
    "Wheat": "resnet50_wheat_disease.pth",
    "Cotton": "resnet50_cotton_disease.pth"
}

def download_model(crop_type):
    model_file = MODEL_FILES[crop_type]
    model_url = MODEL_URLS[crop_type]

    if not os.path.exists(model_file):
        st.info(f"Downloading {model_file} from Google Drive...")
        gdown.download(model_url, model_file, quiet=False)
    return model_file

@st.cache_resource
def load_model(crop_type):
    model_file = download_model(crop_type)
    model = models.resnet50(pretrained=False)
    num_classes = 3  # adjust according to your dataset
    model.fc = torch.nn.Linear(model.fc.in_features, num_classes)
    model.load_state_dict(torch.load(model_file, map_location=torch.device('cpu')))
    model.eval()
    return model



import streamlit as st
import torch
from torchvision import transforms, models
from PIL import Image
import torch.nn as nn
import base64
import requests
import os
from typing import Optional, Tuple, List

# --- Page Configuration ---
st.set_page_config(
    page_title="Pakistani Crop Doctor",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS to maximize page width
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&display=swap');
    
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 100%;
    }
    
    .stApp {
        max-width: 100%;
    }
    
    /* Urdu Font Styling - More Specific */
    .urdu-text, .urdu-header, .urdu-subtitle {
        font-family: 'Noto Nastaliq Urdu', 'Jameel Noori Nastaleeq', 'Nastaliq', serif !important;
        direction: rtl !important;
    }
    
    /* Specific styling for Urdu headers */
    .urdu-header {
        font-weight: 700 !important;
        font-size: 2.5rem !important;
        line-height: 2.2 !important;
        text-align: center !important;
    }
    
    /* Urdu subtitle styling */
    .urdu-subtitle {
        font-weight: 600 !important;
        font-size: 1.5rem !important;
        line-height: 2.0 !important;
        text-align: center !important;
    }
    
    /* General Urdu text styling */
    .urdu-text {
        font-weight: 500 !important;
        line-height: 1.8 !important;
    }
    
    /* Apply Urdu font to all Urdu content */
    h1, h2, h3, p, div, span {
        font-family: 'Noto Nastaliq Urdu', 'Jameel Noori Nastaleeq', 'Nastaliq', serif;
    }
</style>
""", unsafe_allow_html=True)

# --- Background Image ---
def set_background(image_url: str) -> None:
    """Set background image with error handling"""
    try:
        response = requests.get(image_url, timeout=10)
        response.raise_for_status()
        img = base64.b64encode(response.content).decode()
        
        page_bg_img = f"""
        <style>
        .stApp {{
            background-image: url("data:image/jpg;base64,{img}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
            background-attachment: fixed;
            background-color: rgba(255, 255, 255, 0.7);
            background-blend-mode: soft-light;
        }}
        </style>
        """
        st.markdown(page_bg_img, unsafe_allow_html=True)
    except Exception as e:
        st.warning(f"Could not load background image: {str(e)}")

# Set background
set_background("https://images.unsplash.com/photo-1500382017468-9049fed747ef?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80")

# --- Enhanced Custom CSS ---
custom_css = """
<style>
    /* Main containers */
    .main-container {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        padding: 3rem;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(4px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        margin-bottom: 2rem;
        transition: transform 0.3s ease;
        min-height: 200px;
    }
    
    .main-container:hover {
        transform: translateY(-5px);
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        border-radius: 12px;
        padding: 0.75rem 1.5rem;
        border: none;
        font-weight: bold;
        font-size: 1.1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(76, 175, 80, 0.3);
    }
    
    .stButton>button:hover {
        background: linear-gradient(135deg, #45a049 0%, #4CAF50 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(76, 175, 80, 0.4);
    }
    
    /* Sidebar - comprehensive styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.9) 0%, rgba(46, 125, 50, 0.9) 100%) !important;
        border-radius: 0 15px 15px 0 !important;
        backdrop-filter: blur(3px) !important;
        border: 3px solid #2E7D32 !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
    }
    
    /* Alternative sidebar selectors */
    .css-1d391kg, .css-1d391kg .css-1d391kg, [data-testid="stSidebar"] > div {
        background: linear-gradient(135deg, rgba(76, 175, 80, 0.9) 0%, rgba(46, 125, 50, 0.9) 100%) !important;
        border-radius: 0 15px 15px 0 !important;
        backdrop-filter: blur(3px) !important;
        border: 3px solid #2E7D32 !important;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3) !important;
    }
    
    /* Sidebar text - comprehensive override */
    [data-testid="stSidebar"] *, .css-1d391kg * {
        color: #FFFFFF !important;
        font-weight: 500 !important;
        text-shadow: none !important;
        backdrop-filter: none !important;
        filter: none !important;
        -webkit-backdrop-filter: none !important;
        -webkit-filter: none !important;
    }
    
    /* Sidebar radio buttons */
    [data-testid="stSidebar"] .stRadio > label, .css-1d391kg .stRadio > label {
        color: #FFFFFF !important;
        font-weight: 500 !important;
        text-shadow: none !important;
        backdrop-filter: none !important;
        filter: none !important;
        -webkit-backdrop-filter: none !important;
        -webkit-filter: none !important;
    }
    
    [data-testid="stSidebar"] .stRadio > div, .css-1d391kg .stRadio > div {
        color: #FFFFFF !important;
        font-weight: 500 !important;
        text-shadow: none !important;
        backdrop-filter: none !important;
        filter: none !important;
        -webkit-backdrop-filter: none !important;
        -webkit-filter: none !important;
    }
    
    /* Sidebar markdown */
    [data-testid="stSidebar"] .stMarkdown, .css-1d391kg .stMarkdown {
        color: #FFFFFF !important;
        font-weight: 500 !important;
        text-shadow: none !important;
        backdrop-filter: none !important;
        filter: none !important;
        -webkit-backdrop-filter: none !important;
        -webkit-filter: none !important;
    }
    
    /* Sidebar titles and headers */
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3, [data-testid="stSidebar"] h4,
    .css-1d391kg h1, .css-1d391kg h2, .css-1d391kg h3, .css-1d391kg h4 {
        color: #FFFFFF !important;
        font-weight: bold !important;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.3) !important;
        backdrop-filter: none !important;
        filter: none !important;
        -webkit-backdrop-filter: none !important;
        -webkit-filter: none !important;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #1B5E20;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        font-weight: bold;
    }
    
    /* Paragraphs and text */
    p {
        color: #2E2E2E;
        font-weight: 500;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
    }
    
    /* Urdu text */
    .urdu-text {
        direction: rtl;
        text-align: right;
        font-family: 'Noto Sans Arabic', sans-serif;
        font-size: 1.1rem;
        line-height: 1.6;
        color: #2E2E2E;
        font-weight: 500;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
    }
    
    /* Prediction cards */
    .prediction-card {
        background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(240, 248, 255, 0.95) 100%);
        border-radius: 15px;
        padding: 1.5rem;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        margin-bottom: 1rem;
        border-left: 5px solid #4CAF50;
        transition: all 0.3s ease;
    }
    
    .prediction-card:hover {
        transform: translateX(5px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.2);
    }
    
    /* File uploader */
    .stFileUploader {
        background-color: rgba(255, 255, 255, 0.95);
        border-radius: 10px;
        padding: 1rem;
        border: 2px solid rgba(76, 175, 80, 0.3);
    }
    
    /* Progress bars */
    .stProgress > div > div > div {
        background-color: #4CAF50;
    }
    
    /* Success message */
    .success-message {
        background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
    }
    
    /* Error message */
    .error-message {
        background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        font-weight: bold;
        margin: 1rem 0;
    }
    
    /* Loading animation */
    .loading {
        display: inline-block;
        width: 20px;
        height: 20px;
        border: 3px solid rgba(255,255,255,.3);
        border-radius: 50%;
        border-top-color: #fff;
        animation: spin 1s ease-in-out infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    /* Streamlit text elements */
    .stMarkdown, .stText {
        color: #2E2E2E !important;
        font-weight: 500 !important;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.8) !important;
    }
    
    /* List items */
    li {
        color: #2E2E2E;
        font-weight: 500;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
    }
    
    /* Strong text */
    strong {
        color: #1B5E20;
        font-weight: bold;
        text-shadow: 1px 1px 2px rgba(255,255,255,0.8);
    }
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# --- Language Selection ---
def get_language() -> str:
    """Get current language from session state"""
    if 'language' not in st.session_state:
        st.session_state.language = 'English'
    return st.session_state.language

def set_language(lang: str) -> None:
    """Set language in session state"""
    st.session_state.language = lang

# --- Class Names ---
wheat_classes = [
    'Aphid', 'Black Rust', 'Blast', 'Brown Rust', 'Common Root Rot',
    'Fusarium Head Blight', 'Healthy', 'Leaf Blight', 'Mildew', 'Mite',
    'Septoria', 'Smut', 'Stem fly', 'Tan spot', 'Yellow Rust'
]

wheat_classes_urdu = [
    'افڈ', 'کالی زنگ', 'دھماکہ', 'بھوری زنگ', 'عام جڑ سڑن',
    'فیوزیریئم ہیڈ بلائٹ', 'صحت مند', 'پتے کا بلائٹ', 'سفوفی پھپھوندی', 'مائٹ',
    'سیپٹوریا', 'سنٹ', 'تنا مکھی', 'ٹین سپاٹ', 'پیلی زنگ'
]

cotton_classes = [
    'Aphids', 'Army worm', 'Bacterial blight', 'Cotton Boll Rot', 
    'Green Cotton Boll', 'Healthy', 'Powdery mildew', 'Target spot'
]

cotton_classes_urdu = [
    'افڈز', 'فوجی کیڑا', 'بیکٹیریل بلائٹ', 'کپاس کے گابھے کی سڑن',
    'سبز کپاس کا گابھا', 'صحت مند', 'سفوفی پھپھوندی', 'ہدف داغ'
]

# --- Class Name Mapping (Urdu to English) ---
urdu_to_english_mapping = {
    # Wheat classes
    'افڈ': 'Aphid',
    'کالی زنگ': 'Black Rust',
    'دھماکہ': 'Blast',
    'بھوری زنگ': 'Brown Rust',
    'عام جڑ سڑن': 'Common Root Rot',
    'فیوزیریئم ہیڈ بلائٹ': 'Fusarium Head Blight',
    'صحت مند': 'Healthy',
    'پتے کا بلائٹ': 'Leaf Blight',
    'سفوفی پھپھوندی': 'Mildew',
    'مائٹ': 'Mite',
    'سیپٹوریا': 'Septoria',
    'سنٹ': 'Smut',
    'تنا مکھی': 'Stem fly',
    'ٹین سپاٹ': 'Tan spot',
    'پیلی زنگ': 'Yellow Rust',
    
    # Cotton classes
    'افڈز': 'Aphids',
    'فوجی کیڑا': 'Army worm',
    'بیکٹیریل بلائٹ': 'Bacterial blight',
    'کپاس کے گابھے کی سڑن': 'Cotton Boll Rot',
    'سبز کپاس کا گابھا': 'Green Cotton Boll',
    'سفوفی پھپھوندی': 'Powdery mildew',
    'ہدف داغ': 'Target spot'
}

# --- Comprehensive Treatment Recommendations ---
treatment_recommendations = {
    'Aphid': {
        'en': {
            'description': 'Aphids are small, soft-bodied insects that feed on plant sap.',
            'symptoms': 'Curled leaves, stunted growth, honeydew secretion, sooty mold.',
            'treatment': [
                'Apply neem oil solution (2-3% concentration)',
                'Use insecticidal soap (potassium salts of fatty acids)',
                'Introduce beneficial insects like ladybugs',
                'Apply early morning or evening for best results'
            ],
            'spray_method': 'Mix 2-3 tablespoons neem oil with 1 gallon water. Spray thoroughly on affected areas.',
            'medicine_image': 'https://tse2.mm.bing.net/th/id/OIP.dXMYTIh3fyFUMb1pyXS47gHaMY?r=0&w=500&h=836&rs=1&pid=ImgDetMain&o=7&rm=3',
            'video_link': 'https://www.youtube.com/watch?v=wKMUW6ulOJc',
            'disclaimer': 'IMPORTANT: Always consult with agricultural experts before applying any treatment. Follow manufacturer instructions and safety guidelines.'
        },
        'ur': {
            'description': 'افڈ چھوٹے، نرم جسم کے کیڑے ہیں جو پودوں کے رس پر کھاتے ہیں۔',
            'symptoms': 'مڑے ہوئے پتے، کم نشوونما، شہد کی رطوبت، کالی کائی۔',
            'treatment': [
                'نیم کا تیل کا محلول استعمال کریں (2-3% ارتکاز)',
                'کیڑے مار صابن استعمال کریں',
                'فائدہ مند کیڑے متعارف کریں',
                'صبح یا شام میں استعمال کریں'
            ],
            'spray_method': '2-3 چمچ نیم کا تیل 1 گیلن پانی میں ملا کر متاثرہ جگہوں پر چھڑکیں۔',
            'medicine_image': 'https://tse2.mm.bing.net/th/id/OIP.dXMYTIh3fyFUMb1pyXS47gHaMY?r=0&w=500&h=836&rs=1&pid=ImgDetMain&o=7&rm=3',
            'video_link': 'https://www.youtube.com/watch?v=wKMUW6ulOJc',
            'disclaimer': 'اہم: کسی بھی علاج سے پہلے زرعی ماہرین سے مشورہ کریں۔'
        }
    },
    'Black Rust': {
        'en': {
            'description': 'Black rust is a fungal disease that affects wheat plants.',
            'symptoms': 'Dark brown to black pustules on leaves, stems, and heads.',
            'treatment': [
                'Apply fungicides containing triazoles (Tebuconazole, Propiconazole)',
                'Remove and destroy infected plant debris',
                'Practice crop rotation',
                'Use resistant wheat varieties'
            ],
            'spray_method': 'Apply fungicide at 0.1% concentration. Spray every 7-10 days during infection period.',
            'medicine_image': 'https://tse4.mm.bing.net/th/id/OIP.erGcwtnrmceZoatVOYCV4AHaNM?r=0&rs=1&pid=ImgDetMain&o=7&rm=3',
            'video_link': 'https://www.youtube.com/watch?v=wKMUW6ulOJc',
            'disclaimer': 'CRITICAL: Consult agricultural experts immediately. Incorrect fungicide use can damage crops and soil.'
        },
        'ur': {
            'description': 'کالی زنگ ایک فنگل بیماری ہے جو گندم کے پودوں کو متاثر کرتی ہے۔',
            'symptoms': 'پتوں، تنوں اور بالیوں پر گہرے بھورے سے کالے دانے۔',
            'treatment': [
                'ٹرائازول پر مشتمل فنگسائڈز استعمال کریں',
                'متاثرہ پودوں کے حصے ہٹا دیں',
                'فصل کی تبدیلی کریں',
                'مقاوم اقسام استعمال کریں'
            ],
            'spray_method': '0.1% ارتکاز میں فنگسائڈ استعمال کریں۔ 7-10 دن کے وقفے سے چھڑکیں۔',
            'medicine_image': 'https://tse4.mm.bing.net/th/id/OIP.erGcwtnrmceZoatVOYCV4AHaNM?r=0&rs=1&pid=ImgDetMain&o=7&rm=3',
            'video_link': 'https://www.youtube.com/watch?v=wKMUW6ulOJc',
            'disclaimer': 'اہم: فوری طور پر زرعی ماہرین سے مشورہ کریں۔'
        }
    },
    'Healthy': {
        'en': {
            'description': 'Your crop appears to be healthy with no visible disease symptoms.',
            'symptoms': 'Normal green color, proper growth, no spots or lesions.',
            'treatment': [
                'Continue regular monitoring',
                'Maintain proper irrigation',
                'Apply balanced fertilizers',
                'Practice good field hygiene'
            ],
            'spray_method': 'No treatment needed. Continue preventive measures.',
            'medicine_image': 'https://tse1.mm.bing.net/th/id/OIP.Eo1tHJpJSYyEY_2S2JgygQHaH5?r=0&rs=1&pid=ImgDetMain&o=7&rm=3',
            'video_link': 'https://www.youtube.com/watch?v=kvoNyO6WG-E',
            'disclaimer': 'Continue monitoring and consult experts if symptoms appear.'
        },
        'ur': {
            'description': 'آپ کی فصل صحت مند نظر آتی ہے۔',
            'symptoms': 'عام سبز رنگ، مناسب نشوونما، کوئی داغ نہیں۔',
            'treatment': [
                'مسلسل نگرانی جاری رکھیں',
                'مناسب آبپاشی کریں',
                'متوازن کھاد استعمال کریں',
                'اچھی کھیت کی صفائی کریں'
            ],
            'spray_method': 'کوئی علاج نہیں چاہیے۔ احتیاطی تدابیر جاری رکھیں۔',
            'medicine_image': 'https://tse1.mm.bing.net/th/id/OIP.Eo1tHJpJSYyEY_2S2JgygQHaH5?r=0&rs=1&pid=ImgDetMain&o=7&rm=3',
            'video_link': 'https://www.youtube.com/watch?v=kvoNyO6WG-E',
            'disclaimer': 'مسلسل نگرانی کریں اور علامات ظاہر ہونے پر ماہرین سے مشورہ کریں۔'
        }
    },
    'Blast': {
        'en': {
            'description': 'Blast is a serious fungal disease affecting rice and wheat crops.',
            'symptoms': 'Diamond-shaped lesions on leaves, neck rot, panicle blanking.',
            'treatment': [
                'Apply fungicides containing Tricyclazole or Azoxystrobin',
                'Use resistant varieties',
                'Avoid excessive nitrogen fertilization',
                'Practice field sanitation'
            ],
            'spray_method': 'Apply fungicide at 0.1% concentration. Spray at 7-10 day intervals.',
            'medicine_image': 'https://tse4.mm.bing.net/th/id/OIP.erGcwtnrmceZoatVOYCV4AHaNM?r=0&rs=1&pid=ImgDetMain&o=7&rm=3',
            'video_link': 'https://www.youtube.com/watch?v=2945Lk45Neo',
            'disclaimer': 'CRITICAL: Consult agricultural experts immediately. Blast can cause severe yield losses.'
        },
        'ur': {
            'description': 'دھماکہ ایک سنگین فنگل بیماری ہے جو چاول اور گندم کی فصلوں کو متاثر کرتی ہے۔',
            'symptoms': 'پتوں پر ہیرے کی شکل کے زخم، گردن کی سڑن، خالی بالیاں۔',
            'treatment': [
                'ٹرائیکلازول یا ازوکسسٹروبین پر مشتمل فنگسائڈز استعمال کریں',
                'مقاوم اقسام استعمال کریں',
                'زیادہ نائٹروجن کھاد سے بچیں',
                'کھیت کی صفائی کریں'
            ],
            'spray_method': '0.1% ارتکاز میں فنگسائڈ استعمال کریں۔ 7-10 دن کے وقفے سے چھڑکیں۔',
            'medicine_image': 'https://tse4.mm.bing.net/th/id/OIP.erGcwtnrmceZoatVOYCV4AHaNM?r=0&rs=1&pid=ImgDetMain&o=7&rm=3',
            'video_link': 'https://www.youtube.com/watch?v=2945Lk45Neo',
            'disclaimer': 'اہم: فوری طور پر زرعی ماہرین سے مشورہ کریں۔'
        }
    },
    'Brown Rust': {
        'en': {
            'description': 'Brown rust is a fungal disease that causes orange-brown pustules on wheat leaves.',
            'symptoms': 'Orange-brown pustules on leaves, yellowing, reduced yield.',
            'treatment': [
                'Apply fungicides containing Triazoles or Strobilurins',
                'Use resistant wheat varieties',
                'Practice crop rotation',
                'Remove infected plant debris'
            ],
            'spray_method': 'Apply fungicide at 0.1% concentration. Spray every 10-14 days.',
            'medicine_image': 'https://tse4.mm.bing.net/th/id/OIP.erGcwtnrmceZoatVOYCV4AHaNM?r=0&rs=1&pid=ImgDetMain&o=7&rm=3',
            'video_link': 'https://www.youtube.com/watch?v=MH268oLgBmM',
            'disclaimer': 'IMPORTANT: Consult agricultural experts for proper fungicide selection and application.'
        },
        'ur': {
            'description': 'بھوری زنگ ایک فنگل بیماری ہے جو گندم کے پتوں پر نارنجی-بھورے دانے پیدا کرتی ہے۔',
            'symptoms': 'پتوں پر نارنجی-بھورے دانے، پیلاہٹ، کم پیداوار۔',
            'treatment': [
                'ٹرائازول یا سٹروبیلورن پر مشتمل فنگسائڈز استعمال کریں',
                'مقاوم گندم کی اقسام استعمال کریں',
                'فصل کی تبدیلی کریں',
                'متاثرہ پودوں کے حصے ہٹا دیں'
            ],
            'spray_method': '0.1% ارتکاز میں فنگسائڈ استعمال کریں۔ 10-14 دن کے وقفے سے چھڑکیں۔',
            'medicine_image': 'https://tse4.mm.bing.net/th/id/OIP.erGcwtnrmceZoatVOYCV4AHaNM?r=0&rs=1&pid=ImgDetMain&o=7&rm=3',
            'video_link': 'https://www.youtube.com/watch?v=MH268oLgBmM',
            'disclaimer': 'اہم: مناسب فنگسائڈ کے انتخاب کے لیے زرعی ماہرین سے مشورہ کریں۔'
        }
    },
    'Common Root Rot': {
        'en': {
            'description': 'Common root rot is a soil-borne fungal disease affecting wheat roots.',
            'symptoms': 'Brown lesions on roots, stunted growth, yellowing leaves, poor tillering.',
            'treatment': [
                'Apply fungicide seed treatment',
                'Practice crop rotation with non-host crops',
                'Improve soil drainage',
                'Use resistant varieties'
            ],
            'spray_method': 'Treat seeds with fungicide before planting. Apply soil drench if needed.',
            'medicine_image': 'https://tse4.mm.bing.net/th/id/OIP.erGcwtnrmceZoatVOYCV4AHaNM?r=0&rs=1&pid=ImgDetMain&o=7&rm=3',
            'video_link': 'https://www.youtube.com/watch?v=tOOXjwsLZxA',
            'disclaimer': 'CRITICAL: Root rot requires immediate attention. Consult experts for soil treatment options.'
        },
        'ur': {
            'description': 'عام جڑ سڑن ایک مٹی سے پھیلنے والی فنگل بیماری ہے جو گندم کی جڑوں کو متاثر کرتی ہے۔',
            'symptoms': 'جڑوں پر بھورے زخم، کم نشوونما، پیلاہٹ، کم پھوٹ۔',
            'treatment': [
                'بیج پر فنگسائڈ کا علاج کریں',
                'غیر میزبان فصلوں کے ساتھ فصل کی تبدیلی کریں',
                'مٹی کی نکاسی بہتر کریں',
                'مقاوم اقسام استعمال کریں'
            ],
            'spray_method': 'بیج بونے سے پہلے فنگسائڈ سے علاج کریں۔ ضرورت ہو تو مٹی میں محلول ڈالیں۔',
            'medicine_image': 'https://tse4.mm.bing.net/th/id/OIP.erGcwtnrmceZoatVOYCV4AHaNM?r=0&rs=1&pid=ImgDetMain&o=7&rm=3',
            'video_link': 'https://www.youtube.com/watch?v=tOOXjwsLZxA',
            'disclaimer': 'اہم: جڑ سڑن پر فوری توجہ کی ضرورت ہے۔'
        }
    },
    'Fusarium Head Blight': {
        'en': {
            'description': 'Fusarium head blight is a fungal disease that affects wheat heads and grains.',
            'symptoms': 'Bleached spikelets, pink or orange fungal growth, shriveled grains.',
            'treatment': [
                'Apply fungicides containing Triazoles or Strobilurins',
                'Use resistant wheat varieties',
                'Practice crop rotation',
                'Avoid excessive nitrogen fertilization'
            ],
            'spray_method': 'Apply fungicide at flowering stage. Use 0.1% concentration.',
            'medicine_image': 'https://tse4.mm.bing.net/th/id/OIP.erGcwtnrmceZoatVOYCV4AHaNM?r=0&rs=1&pid=ImgDetMain&o=7&rm=3',
            'video_link': 'https://www.youtube.com/watch?v=97z4XknvHgw',
            'disclaimer': 'CRITICAL: Fusarium can produce mycotoxins. Consult experts immediately.'
        },
        'ur': {
            'description': 'فیوزیریئم ہیڈ بلائٹ ایک فنگل بیماری ہے جو گندم کی بالیوں اور دانوں کو متاثر کرتی ہے۔',
            'symptoms': 'سفید بالیاں، گلابی یا نارنجی فنگل نشوونما، سکڑے دانے۔',
            'treatment': [
                'ٹرائازول یا سٹروبیلورن پر مشتمل فنگسائڈز استعمال کریں',
                'مقاوم گندم کی اقسام استعمال کریں',
                'فصل کی تبدیلی کریں',
                'زیادہ نائٹروجن کھاد سے بچیں'
            ],
            'spray_method': 'پھول آنے کے مرحلے میں فنگسائڈ استعمال کریں۔ 0.1% ارتکاز استعمال کریں۔',
            'medicine_image': 'https://tse4.mm.bing.net/th/id/OIP.erGcwtnrmceZoatVOYCV4AHaNM?r=0&rs=1&pid=ImgDetMain&o=7&rm=3',
            'video_link': 'https://www.youtube.com/watch?v=97z4XknvHgw',
            'disclaimer': 'اہم: فیوزیریئم مائیکوٹوکسین پیدا کر سکتا ہے۔ فوری ماہرین سے مشورہ کریں۔'
        }
    },
    'Leaf Blight': {
        'en': {
            'description': 'Leaf blight is a fungal disease that causes brown lesions on wheat leaves.',
            'symptoms': 'Brown to tan lesions on leaves, yellow halos around lesions.',
            'treatment': [
                'Apply fungicides containing Mancozeb or Chlorothalonil',
                'Remove infected plant debris',
                'Practice crop rotation',
                'Use resistant varieties'
            ],
            'spray_method': 'Apply fungicide at 0.2% concentration. Spray every 7-10 days.',
            'medicine_image': 'https://tse4.mm.bing.net/th/id/OIP.erGcwtnrmceZoatVOYCV4AHaNM?r=0&rs=1&pid=ImgDetMain&o=7&rm=3',
            'video_link': 'https://www.youtube.com/watch?v=EvGahZJS6yo',
            'disclaimer': 'IMPORTANT: Consult agricultural experts for proper fungicide application timing.'
        },
        'ur': {
            'description': 'پتے کا بلائٹ ایک فنگل بیماری ہے جو گندم کے پتوں پر بھورے زخم پیدا کرتی ہے۔',
            'symptoms': 'پتوں پر بھورے سے پیلاہٹ والے زخم، زخموں کے اردگرد پیلا ہالہ۔',
            'treatment': [
                'مینکوزیب یا کلوروتھیلونل پر مشتمل فنگسائڈز استعمال کریں',
                'متاثرہ پودوں کے حصے ہٹا دیں',
                'فصل کی تبدیلی کریں',
                'مقاوم اقسام استعمال کریں'
            ],
            'spray_method': '0.2% ارتکاز میں فنگسائڈ استعمال کریں۔ 7-10 دن کے وقفے سے چھڑکیں۔',
            'medicine_image': 'https://tse4.mm.bing.net/th/id/OIP.erGcwtnrmceZoatVOYCV4AHaNM?r=0&rs=1&pid=ImgDetMain&o=7&rm=3',
            'video_link': 'https://www.youtube.com/watch?v=EvGahZJS6yo',
            'disclaimer': 'اہم: مناسب فنگسائڈ کے استعمال کے وقت کے لیے زرعی ماہرین سے مشورہ کریں۔'
        }
    },
    'Mildew': {
        'en': {
            'description': 'Powdery mildew is a fungal disease that appears as white powdery spots on leaves.',
            'symptoms': 'White powdery spots on leaves, yellowing, stunted growth.',
            'treatment': [
                'Apply fungicides containing Sulfur or Triazoles',
                'Improve air circulation',
                'Avoid overhead irrigation',
                'Use resistant varieties'
            ],
            'spray_method': 'Apply sulfur-based fungicide at 0.5% concentration. Spray every 7 days.',
            'medicine_image': 'https://i5.walmartimages.com/asr/80bb8670-c2bc-4d1d-a3c7-ee40f12c319d.ecb2c7085b341b9ff4acc728f3a58066.jpeg?odnWidth=1000&odnHeight=1000&odnBg=ffffff',
            'video_link': 'https://www.youtube.com/watch?v=Tq7jCwh2CYU',
            'disclaimer': 'IMPORTANT: Apply fungicides early in the morning or evening to avoid leaf burn.'
        },
        'ur': {
            'description': 'سفوفی پھپھوندی ایک فنگل بیماری ہے جو پتوں پر سفید سفوفی داغوں کے طور پر ظاہر ہوتی ہے۔',
            'symptoms': 'پتوں پر سفید سفوفی داغ، پیلاہٹ، کم نشوونما، کم پیداوار۔',
            'treatment': [
                'سلفر یا ٹرائازول پر مشتمل فنگسائڈز استعمال کریں',
                'ہوا کی گردش بہتر کریں',
                'اوپر سے آبپاشی سے بچیں',
                'مقاوم اقسام استعمال کریں'
            ],
            'spray_method': '0.5% ارتکاز میں سلفر پر مبنی فنگسائڈ استعمال کریں۔ 7 دن کے وقفے سے چھڑکیں۔',
            'medicine_image': 'https://i5.walmartimages.com/asr/80bb8670-c2bc-4d1d-a3c7-ee40f12c319d.ecb2c7085b341b9ff4acc728f3a58066.jpeg?odnWidth=1000&odnHeight=1000&odnBg=ffffff',
            'video_link': 'https://www.youtube.com/watch?v=Tq7jCwh2CYU',
            'disclaimer': 'اہم: پتوں کے جلنے سے بچنے کے لیے صبح یا شام میں فنگسائڈ استعمال کریں۔'
        }
    },
    'Mite': {
        'en': {
            'description': 'Mites are tiny arachnids that feed on plant sap and cause damage to wheat.',
            'symptoms': 'Yellow stippling on leaves, webbing, stunted growth, leaf curling.',
            'treatment': [
                'Apply acaricides containing Abamectin or Spiromesifen',
                'Use predatory mites for biological control',
                'Improve field hygiene',
                'Monitor regularly for early detection'
            ],
            'spray_method': 'Apply acaricide at 0.05% concentration. Spray thoroughly on both sides of leaves.',
            'medicine_image': 'https://tse2.mm.bing.net/th/id/OIP.BtiFj6mHPF6eSLvXZdIrewHaHa?r=0&rs=1&pid=ImgDetMain&o=7&rm=3',
            'video_link': 'https://www.youtube.com/watch?v=OfE-JyE8wcY',
            'disclaimer': 'IMPORTANT: Mites can develop resistance quickly. Rotate acaricides and consult experts.'
        },
        'ur': {
            'description': 'مائٹ چھوٹے آرکنڈ ہیں جو پودوں کے رس پر کھاتے ہیں اور گندم کو نقصان پہنچاتے ہیں۔',
            'symptoms': 'پتوں پر پیلا داغ، جالے، کم نشوونما، پتوں کا مڑنا۔',
            'treatment': [
                'ابامیکٹن یا سپائرومیسیفن پر مشتمل ایکارسائڈز استعمال کریں',
                'حیاتیاتی کنٹرول کے لیے شکار مائٹس استعمال کریں',
                'کھیت کی صفائی بہتر کریں',
                'جلدی شناخت کے لیے باقاعدہ نگرانی کریں'
            ],
            'spray_method': '0.05% ارتکاز میں ایکارسائڈ استعمال کریں۔ پتوں کے دونوں طرف اچھی طرح چھڑکیں۔',
            'medicine_image': 'https://tse2.mm.bing.net/th/id/OIP.BtiFj6mHPF6eSLvXZdIrewHaHa?r=0&rs=1&pid=ImgDetMain&o=7&rm=3',
            'video_link': 'https://www.youtube.com/watch?v=OfE-JyE8wcY',
            'disclaimer': 'اہم: مائٹس جلد مزاحمت پیدا کر سکتے ہیں۔ ایکارسائڈز کو تبدیل کریں اور ماہرین سے مشورہ کریں۔'
        }
    },
    'Septoria': {
        'en': {
            'description': 'Septoria leaf blotch is a fungal disease that causes brown lesions on wheat leaves.',
            'symptoms': 'Brown lesions with dark borders, yellow halos, premature leaf death.',
            'treatment': [
                'Apply fungicides containing Triazoles or Strobilurins',
                'Use resistant wheat varieties',
                'Practice crop rotation',
                'Remove infected plant debris'
            ],
            'spray_method': 'Apply fungicide at 0.1% concentration. Spray at flag leaf stage.',
            'medicine_image': 'https://cdn11.bigcommerce.com/s-s3ju3f26xy/images/stencil/2560w/products/1249/2797/Kendon_Triforine_Rose_Fungicide_500mL__59734__24103.1653879580.jpg?c=1',
            'video_link': 'https://www.youtube.com/watch?v=ldwQasPFljM',
            'disclaimer': 'IMPORTANT: Apply fungicides at the correct growth stage for maximum effectiveness.'
        },
        'ur': {
            'description': 'سیپٹوریا لیف بلوچ ایک فنگل بیماری ہے جو گندم کے پتوں پر بھورے زخم پیدا کرتی ہے۔',
            'symptoms': 'گہری سرحدوں والے بھورے زخم، پیلا ہالہ، قبل از وقت پتے کی موت۔',
            'treatment': [
                'ٹرائازول یا سٹروبیلورن پر مشتمل فنگسائڈز استعمال کریں',
                'مقاوم گندم کی اقسام استعمال کریں',
                'فصل کی تبدیلی کریں',
                'متاثرہ پودوں کے حصے ہٹا دیں'
            ],
            'spray_method': '0.1% ارتکاز میں فنگسائڈ استعمال کریں۔ جھنڈے کے پتے کے مرحلے میں چھڑکیں۔',
            'medicine_image': 'https://cdn11.bigcommerce.com/s-s3ju3f26xy/images/stencil/2560w/products/1249/2797/Kendon_Triforine_Rose_Fungicide_500mL__59734__24103.1653879580.jpg?c=1',
            'video_link': 'https://www.youtube.com/watch?v=ldwQasPFljM',
            'disclaimer': 'اہم: زیادہ سے زیادہ تاثیر کے لیے صحیح نشوونما کے مرحلے میں فنگسائڈ استعمال کریں۔'
        }
    },
    'Smut': {
        'en': {
            'description': 'Smut is a fungal disease that affects wheat grains and heads.',
            'symptoms': 'Black powdery spores in place of grains, distorted heads.',
            'treatment': [
                'Treat seeds with fungicide before planting',
                'Use resistant wheat varieties',
                'Practice crop rotation',
                'Remove and destroy infected plants'
            ],
            'spray_method': 'Seed treatment with fungicide at 0.2% concentration before sowing.',
            'medicine_image': 'https://cdn11.bigcommerce.com/s-s3ju3f26xy/images/stencil/2560w/products/1249/2797/Kendon_Triforine_Rose_Fungicide_500mL__59734__24103.1653879580.jpg?c=1',
            'video_link': 'https://www.youtube.com/watch?v=rAU3SSzPbgk',
            'disclaimer': 'CRITICAL: Smut can spread rapidly. Use certified disease-free seeds.'
        },
        'ur': {
            'description': 'سنٹ ایک فنگل بیماری ہے جو گندم کے دانوں اور بالیوں کو متاثر کرتی ہے۔',
            'symptoms': 'دانوں کی جگہ کالے سفوفی سپور، مسخ شدہ بالیاں۔',
            'treatment': [
                'بیج بونے سے پہلے فنگسائڈ سے علاج کریں',
                'مقاوم گندم کی اقسام استعمال کریں',
                'فصل کی تبدیلی کریں',
                'متاثرہ پودوں کو ہٹا کر تباہ کریں'
            ],
            'spray_method': 'بیج بونے سے پہلے 0.2% ارتکاز میں فنگسائڈ سے بیج کا علاج کریں۔',
            'medicine_image': 'https://cdn11.bigcommerce.com/s-s3ju3f26xy/images/stencil/2560w/products/1249/2797/Kendon_Triforine_Rose_Fungicide_500mL__59734__24103.1653879580.jpg?c=1',
            'video_link': 'https://www.youtube.com/watch?v=rAU3SSzPbgk',
            'disclaimer': 'اہم: سنٹ تیزی سے پھیل سکتا ہے۔ تصدیق شدہ بیماری سے پاک بیج استعمال کریں۔'
        }
    },
    'Stem fly': {
        'en': {
            'description': 'Stem fly larvae bore into wheat stems, causing lodging and yield loss.',
            'symptoms': 'Wilting plants, stem breakage, white larvae in stems, lodging.',
            'treatment': [
                'Apply insecticides containing Imidacloprid or Thiamethoxam',
                'Use resistant wheat varieties',
                'Practice early planting',
                'Remove crop residues after harvest'
            ],
            'spray_method': 'Apply systemic insecticide at 0.1% concentration during early growth stages.',
            'medicine_image': 'https://th.bing.com/th/id/R.201746c0ecefc5c23f4983d58c5c3ea2?rik=yJ2%2bPJ%2bKSZZVVg&riu=http%3a%2f%2fwww.hardwareworld.com%2ffiles%2fpi%2fl8%2fC%2f5GDQ.jpg&ehk=WvjtoMFz8cnMHzM38HrhB3YcuEgNzPedmmGIfazQJR0%3d&risl=&pid=ImgRaw&r=0',
            'video_link': 'https://www.youtube.com/watch?v=C3Id_T1Pqbc',
            'disclaimer': 'IMPORTANT: Apply insecticides early before larvae enter stems.'
        },
        'ur': {
            'description': 'تنا مکھی کے لاروے گندم کے تنوں میں سوراخ کرتے ہیں، جس سے پودے گرتے ہیں اور پیداوار کم ہوتی ہے۔',
            'symptoms': 'مرجھائے پودے، تنا ٹوٹنا، تنوں میں سفید لاروے، پودوں کا گرنا۔',
            'treatment': [
                'امیداکلوپرڈ یا تھایامیتھوکسام پر مشتمل کیڑے مار دوائیں استعمال کریں',
                'مقاوم گندم کی اقسام استعمال کریں',
                'جلدی بیج بونے کا طریقہ اپنائیں',
                'کٹائی کے بعد فصل کے باقیات ہٹا دیں'
            ],
            'spray_method': 'ابتدائی نشوونما کے مرحلوں میں 0.1% ارتکاز میں نظامی کیڑے مار دوائی استعمال کریں۔',
            'medicine_image': 'https://th.bing.com/th/id/R.201746c0ecefc5c23f4983d58c5c3ea2?rik=yJ2%2bPJ%2bKSZZVVg&riu=http%3a%2f%2fwww.hardwareworld.com%2ffiles%2fpi%2fl8%2fC%2f5GDQ.jpg&ehk=WvjtoMFz8cnMHzM38HrhB3YcuEgNzPedmmGIfazQJR0%3d&risl=&pid=ImgRaw&r=0',
            'video_link': 'https://www.youtube.com/watch?v=C3Id_T1Pqbc',
            'disclaimer': 'اہم: لاروے تنوں میں داخل ہونے سے پہلے کیڑے مار دوائی استعمال کریں۔'
        }
    },
    'Tan spot': {
        'en': {
            'description': 'Tan spot is a fungal disease that causes tan to brown lesions on wheat leaves.',
            'symptoms': 'Tan to brown diamond-shaped lesions, yellow halos, leaf death.',
            'treatment': [
                'Apply fungicides containing Triazoles or Strobilurins',
                'Use resistant wheat varieties',
                'Practice crop rotation',
                'Remove infected crop residues'
            ],
            'spray_method': 'Apply fungicide at 0.1% concentration. Spray at flag leaf stage.',
            'medicine_image': 'https://tse3.mm.bing.net/th/id/OIP.DbAkoRYkFvvynC1_r0I-pQHaHa?r=0&rs=1&pid=ImgDetMain&o=7&rm=3',
            'video_link': 'https://www.youtube.com/watch?v=rnL7tanW3Po',
            'disclaimer': 'IMPORTANT: Tan spot can reduce yield significantly. Early detection is crucial.'
        },
        'ur': {
            'description': 'ٹین سپاٹ ایک فنگل بیماری ہے جو گندم کے پتوں پر پیلاہٹ سے بھورے زخم پیدا کرتی ہے۔',
            'symptoms': 'پیلاہٹ سے بھورے ہیرے کی شکل کے زخم، پیلا ہالہ، پتے کی موت۔',
            'treatment': [
                'ٹرائازول یا سٹروبیلورن پر مشتمل فنگسائڈز استعمال کریں',
                'مقاوم گندم کی اقسام استعمال کریں',
                'فصل کی تبدیلی کریں',
                'متاثرہ فصل کے باقیات ہٹا دیں'
            ],
            'spray_method': '0.1% ارتکاز میں فنگسائڈ استعمال کریں۔ جھنڈے کے پتے کے مرحلے میں چھڑکیں۔',
            'medicine_image': 'https://tse3.mm.bing.net/th/id/OIP.DbAkoRYkFvvynC1_r0I-pQHaHa?r=0&rs=1&pid=ImgDetMain&o=7&rm=3',
            'video_link': 'https://www.youtube.com/watch?v=rnL7tanW3Po',
            'disclaimer': 'اہم: ٹین سپاٹ پیداوار کو نمایاں طور پر کم کر سکتا ہے۔ جلد شناخت ضروری ہے۔'
        }
    },
    'Yellow Rust': {
        'en': {
            'description': 'Yellow rust is a fungal disease that causes bright yellow pustules on wheat leaves.',
            'symptoms': 'Bright yellow pustules on leaves, yellowing, reduced photosynthesis.',
            'treatment': [
                'Apply fungicides containing Triazoles or Strobilurins',
                'Use resistant wheat varieties',
                'Practice crop rotation',
                'Monitor regularly for early detection'
            ],
            'spray_method': 'Apply fungicide at 0.1% concentration. Spray every 10-14 days during infection.',
            'medicine_image': 'https://tse3.mm.bing.net/th/id/OIP.DbAkoRYkFvvynC1_r0I-pQHaHa?r=0&rs=1&pid=ImgDetMain&o=7&rm=3',
            'video_link': 'https://www.youtube.com/watch?v=HeyXBXBB9Ik',
            'disclaimer': 'CRITICAL: Yellow rust can spread rapidly. Apply fungicides immediately upon detection.'
        },
        'ur': {
            'description': 'پیلی زنگ ایک فنگل بیماری ہے جو گندم کے پتوں پر چمکدار پیلاہٹ والے دانے پیدا کرتی ہے۔',
            'symptoms': 'پتوں پر چمکدار پیلاہٹ والے دانے، پیلاہٹ، کم فوٹوسنتھیسس۔',
            'treatment': [
                'ٹرائازول یا سٹروبیلورن پر مشتمل فنگسائڈز استعمال کریں',
                'مقاوم گندم کی اقسام استعمال کریں',
                'فصل کی تبدیلی کریں',
                'جلدی شناخت کے لیے باقاعدہ نگرانی کریں'
            ],
            'spray_method': '0.1% ارتکاز میں فنگسائڈ استعمال کریں۔ انفیکشن کے دوران 10-14 دن کے وقفے سے چھڑکیں۔',
            'medicine_image': 'https://tse3.mm.bing.net/th/id/OIP.DbAkoRYkFvvynC1_r0I-pQHaHa?r=0&rs=1&pid=ImgDetMain&o=7&rm=3',
            'video_link': 'https://www.youtube.com/watch?v=HeyXBXBB9Ik',
            'disclaimer': 'اہم: پیلی زنگ تیزی سے پھیل سکتا ہے۔ شناخت کے فوراً بعد فنگسائڈ استعمال کریں۔'
        }
    },
    # Cotton Diseases
    'Aphids': {
        'en': {
            'description': 'Aphids are small, soft-bodied insects that feed on cotton plant sap.',
            'symptoms': 'Curled leaves, stunted growth, honeydew secretion, sooty mold.',
            'treatment': [
                'Apply neem oil solution (2-3% concentration)',
                'Use insecticidal soap or pyrethrin-based insecticides',
                'Introduce beneficial insects like ladybugs',
                'Apply early morning or evening for best results'
            ],
            'spray_method': 'Mix 2-3 tablespoons neem oil with 1 gallon water. Spray thoroughly on affected areas.',
            'medicine_image': 'https://i5.walmartimages.com/seo/Harris-Neem-Oil-Spray-for-Plants-Cold-Pressed-Ready-to-Use-128oz_ebb1273c-c03e-4370-b802-6a7d4a881342.969b2a7b21039fc4f515e350ccc84500.jpeg?odnHeight=226&odnWidth=226&odnBg=FFFFFF',
            'video_link': 'https://www.youtube.com/watch?v=jf9mAPAN_aY',
            'disclaimer': 'IMPORTANT: Always consult with agricultural experts before applying any treatment.'
        },
        'ur': {
            'description': 'افڈز چھوٹے، نرم جسم کے کیڑے ہیں جو کپاس کے پودوں کے رس پر کھاتے ہیں۔',
            'symptoms': 'مڑے ہوئے پتے، کم نشوونما، شہد کی رطوبت، کالی کائی۔',
            'treatment': [
                'نیم کا تیل کا محلول استعمال کریں (2-3% ارتکاز)',
                'کیڑے مار صابن یا پائریتھرن پر مبنی کیڑے مار دوائیں استعمال کریں',
                'فائدہ مند کیڑے متعارف کریں',
                'صبح یا شام میں استعمال کریں'
            ],
            'spray_method': '2-3 چمچ نیم کا تیل 1 گیلن پانی میں ملا کر متاثرہ جگہوں پر چھڑکیں۔',
            'medicine_image': 'https://i5.walmartimages.com/seo/Harris-Neem-Oil-Spray-for-Plants-Cold-Pressed-Ready-to-Use-128oz_ebb1273c-c03e-4370-b802-6a7d4a881342.969b2a7b21039fc4f515e350ccc84500.jpeg?odnHeight=226&odnWidth=226&odnBg=FFFFFF',
            'video_link': 'https://www.youtube.com/watch?v=jf9mAPAN_aY',
            'disclaimer': 'اہم: کسی بھی علاج سے پہلے زرعی ماہرین سے مشورہ کریں۔'
        }
    },
    'Army worm': {
        'en': {
            'description': 'Army worms are destructive caterpillars that feed on cotton leaves and can cause severe defoliation.',
            'symptoms': 'Skeletonized leaves, defoliation, dark green to black caterpillars, rapid spread.',
            'treatment': [
                'Apply insecticides containing Spinosad or Bacillus thuringiensis',
                'Use pheromone traps for monitoring',
                'Practice early detection and control',
                'Remove crop residues after harvest'
            ],
            'spray_method': 'Apply insecticide at 0.1% concentration. Spray in early morning or evening.',
            'medicine_image': 'https://5.imimg.com/data5/SELLER/Default/2023/10/353955631/YX/ZX/XZ/88911411/organic-pesticides-500x500.jpg',
            'video_link': 'https://www.youtube.com/watch?v=x8lWE461ZJ4',
            'disclaimer': 'CRITICAL: Army worms can cause complete defoliation. Apply control measures immediately.'
        },
        'ur': {
            'description': 'فوجی کیڑے تباہ کن کیٹرپلر ہیں جو کپاس کے پتوں پر کھاتے ہیں اور شدید پتے گرنے کا سبب بن سکتے ہیں۔',
            'symptoms': 'ہڈیوں والے پتے، پتے گرنا، گہرے سبز سے کالے کیٹرپلر، تیز پھیلاؤ۔',
            'treatment': [
                'سپائنوساد یا باسلس تھرنجینسس پر مشتمل کیڑے مار دوائیں استعمال کریں',
                'نگرانی کے لیے فیرومون ٹریپس استعمال کریں',
                'جلدی شناخت اور کنٹرول کا طریقہ اپنائیں',
                'کٹائی کے بعد فصل کے باقیات ہٹا دیں'
            ],
            'spray_method': '0.1% ارتکاز میں کیڑے مار دوائی استعمال کریں۔ صبح یا شام میں چھڑکیں۔',
            'medicine_image': 'https://5.imimg.com/data5/SELLER/Default/2023/10/353955631/YX/ZX/XZ/88911411/organic-pesticides-500x500.jpg',
            'video_link': 'https://www.youtube.com/watch?v=x8lWE461ZJ4',
            'disclaimer': 'اہم: فوجی کیڑے مکمل پتے گرنے کا سبب بن سکتے ہیں۔ فوری کنٹرول کے اقدامات کریں۔'
        }
    },
    'Bacterial blight': {
        'en': {
            'description': 'Bacterial blight is a serious bacterial disease that affects cotton plants.',
            'symptoms': 'Angular leaf spots, water-soaked lesions, stem cankers, boll rot.',
            'treatment': [
                'Use copper-based bactericides',
                'Plant resistant cotton varieties',
                'Practice crop rotation',
                'Remove and destroy infected plants'
            ],
            'spray_method': 'Apply copper-based bactericide at 0.2% concentration. Spray every 7-10 days.',
            'medicine_image': 'https://tse3.mm.bing.net/th/id/OIP.EF1QTb31MbIS3KPWg2acQwHaHa?r=0&w=500&h=500&rs=1&pid=ImgDetMain&o=7&rm=3',
            'video_link': 'https://www.youtube.com/watch?v=-ry_frRy9II',
            'disclaimer': 'CRITICAL: Bacterial blight can spread rapidly. Use certified disease-free seeds.'
        },
        'ur': {
            'description': 'بیکٹیریل بلائٹ ایک سنگین بیکٹیریل بیماری ہے جو کپاس کے پودوں کو متاثر کرتی ہے۔',
            'symptoms': 'کونیائی پتے کے داغ، پانی سے بھرے زخم، تنا کینکر، گابھے کی سڑن۔',
            'treatment': [
                'تانبے پر مبنی بیکٹیریسائڈز استعمال کریں',
                'مقاوم کپاس کی اقسام لگائیں',
                'فصل کی تبدیلی کریں',
                'متاثرہ پودوں کو ہٹا کر تباہ کریں'
            ],
            'spray_method': '0.2% ارتکاز میں تانبے پر مبنی بیکٹیریسائڈ استعمال کریں۔ 7-10 دن کے وقفے سے چھڑکیں۔',
            'medicine_image': 'https://tse3.mm.bing.net/th/id/OIP.EF1QTb31MbIS3KPWg2acQwHaHa?r=0&w=500&h=500&rs=1&pid=ImgDetMain&o=7&rm=3',
            'video_link': 'https://www.youtube.com/watch?v=-ry_frRy9II',
            'disclaimer': 'اہم: بیکٹیریل بلائٹ تیزی سے پھیل سکتا ہے۔ تصدیق شدہ بیماری سے پاک بیج استعمال کریں۔'
        }
    },
    'Cotton Boll Rot': {
        'en': {
            'description': 'Cotton boll rot is a fungal disease that affects cotton bolls, causing yield loss.',
            'symptoms': 'Brown to black lesions on bolls, moldy growth, premature boll opening.',
            'treatment': [
                'Apply fungicides containing Triazoles or Strobilurins',
                'Improve field drainage',
                'Practice crop rotation',
                'Remove infected bolls'
            ],
            'spray_method': 'Apply fungicide at 0.1% concentration during boll development stage.',
            'medicine_image': 'https://i5.walmartimages.com/asr/44c50dc8-862f-42b4-9885-6357811be65f.6e2d047d5ae6471611c51ac2b0efe840.jpeg?odnWidth=1000&odnHeight=1000&odnBg=ffffff',
            'video_link': 'https://www.youtube.com/watch?v=ow1sTALPW8I',
            'disclaimer': 'IMPORTANT: Boll rot can significantly reduce cotton yield and quality.'
        },
        'ur': {
            'description': 'کپاس کے گابھے کی سڑن ایک فنگل بیماری ہے جو کپاس کے گابھوں کو متاثر کرتی ہے۔',
            'symptoms': 'گابھوں پر بھورے سے کالے زخم، کائی والی نشوونما، قبل از وقت گابھا کھلنا۔',
            'treatment': [
                'ٹرائازول یا سٹروبیلورن پر مشتمل فنگسائڈز استعمال کریں',
                'کھیت کی نکاسی بہتر کریں',
                'فصل کی تبدیلی کریں',
                'متاثرہ گابھے ہٹا دیں'
            ],
            'spray_method': 'گابھے کی نشوونما کے مرحلے میں 0.1% ارتکاز میں فنگسائڈ استعمال کریں۔',
            'medicine_image': 'https://i5.walmartimages.com/asr/44c50dc8-862f-42b4-9885-6357811be65f.6e2d047d5ae6471611c51ac2b0efe840.jpeg?odnWidth=1000&odnHeight=1000&odnBg=ffffff',
            'video_link': 'https://www.youtube.com/watch?v=ow1sTALPW8I',
            'disclaimer': 'اہم: گابھے کی سڑن کپاس کی پیداوار اور معیار کو نمایاں طور پر کم کر سکتی ہے۔'
        }
    },
    'Green Cotton Boll': {
        'en': {
            'description': 'Green cotton boll indicates immature or underdeveloped cotton bolls.',
            'symptoms': 'Green, immature bolls, delayed maturity, poor fiber development.',
            'treatment': [
                'Ensure proper irrigation and nutrition',
                'Monitor temperature and humidity',
                'Use appropriate cotton varieties for your region',
                'Practice proper harvesting timing'
            ],
            'spray_method': 'No chemical treatment needed. Focus on cultural practices.',
            'medicine_image': 'https://cdn2.vectorstock.com/i/1000x1000/83/01/chemical-free-sign-or-stamp-vector-33558301.jpg',
            'video_link': 'https://www.youtube.com/watch?v=ao1I1TM9DUI',
            'disclaimer': 'IMPORTANT: Green bolls are not a disease but a management issue.'
        },
        'ur': {
            'description': 'سبز کپاس کا گابھا نابالغ یا کم نشوونما والے کپاس کے گابھوں کی نشاندہی کرتا ہے۔',
            'symptoms': 'سبز، نابالغ گابھے، تاخیر سے پختگی، خراب ریشہ کی نشوونما۔',
            'treatment': [
                'مناسب آبپاشی اور غذائیت یقینی بنائیں',
                'درجہ حرارت اور نمی کی نگرانی کریں',
                'اپنے علاقے کے لیے مناسب کپاس کی اقسام استعمال کریں',
                'مناسب کٹائی کا وقت اپنائیں'
            ],
            'spray_method': 'کوئی کیمیائی علاج نہیں چاہیے۔ ثقافتی طریقوں پر توجہ دیں۔',
            'medicine_image': 'https://cdn2.vectorstock.com/i/1000x1000/83/01/chemical-free-sign-or-stamp-vector-33558301.jpg',
            'video_link': 'https://www.youtube.com/watch?v=ao1I1TM9DUI',
            'disclaimer': 'اہم: سبز گابھے بیماری نہیں بلکہ انتظام کا مسئلہ ہیں۔'
        }
    },
    'Powdery mildew': {
        'en': {
            'description': 'Powdery mildew is a fungal disease that appears as white powdery spots on cotton leaves.',
            'symptoms': 'White powdery spots on leaves, yellowing, stunted growth, reduced yield.',
            'treatment': [
                'Apply fungicides containing Sulfur or Triazoles',
                'Improve air circulation',
                'Avoid overhead irrigation',
                'Use resistant cotton varieties'
            ],
            'spray_method': 'Apply sulfur-based fungicide at 0.5% concentration. Spray every 7 days.',
            'medicine_image': 'https://ocp.com.au/wp-content/uploads/2023/09/Bag-Render-sulfur-10kg-FA.webp',
            'video_link': 'https://www.youtube.com/watch?v=IfwojJr-ZGQ',
            'disclaimer': 'IMPORTANT: Apply fungicides early in the morning or evening to avoid leaf burn.'
        },
        'ur': {
            'description': 'سفوفی پھپھوندی ایک فنگل بیماری ہے جو کپاس کے پتوں پر سفید سفوفی داغوں کے طور پر ظاہر ہوتی ہے۔',
            'symptoms': 'پتوں پر سفید سفوفی داغ، پیلاہٹ، کم نشوونما، کم پیداوار۔',
            'treatment': [
                'سلفر یا ٹرائازول پر مشتمل فنگسائڈز استعمال کریں',
                'ہوا کی گردش بہتر کریں',
                'اوپر سے آبپاشی سے بچیں',
                'مقاوم کپاس کی اقسام استعمال کریں'
            ],
            'spray_method': '0.5% ارتکاز میں سلفر پر مبنی فنگسائڈ استعمال کریں۔ 7 دن کے وقفے سے چھڑکیں۔',
            'medicine_image': 'https://ocp.com.au/wp-content/uploads/2023/09/Bag-Render-sulfur-10kg-FA.webp',
            'video_link': 'https://www.youtube.com/watch?v=IfwojJr-ZGQ',
            'disclaimer': 'اہم: پتوں کے جلنے سے بچنے کے لیے صبح یا شام میں فنگسائڈ استعمال کریں۔'
        }
    },
    'Target spot': {
        'en': {
            'description': 'Target spot is a fungal disease that causes circular lesions with target-like appearance on cotton leaves.',
            'symptoms': 'Circular brown lesions with concentric rings, yellow halos, leaf defoliation.',
            'treatment': [
                'Apply fungicides containing Triazoles or Strobilurins',
                'Use resistant cotton varieties',
                'Practice crop rotation',
                'Remove infected plant debris'
            ],
            'spray_method': 'Apply fungicide at 0.1% concentration. Spray every 7-10 days.',
            'medicine_image': 'https://standishmilling.com/cdn/shop/files/1428_LifeStyle_01_1024x1024.jpg?v=1715011940',
            'video_link': 'https://www.youtube.com/watch?v=SvI_zXNgyXg',
            'disclaimer': 'IMPORTANT: Target spot can cause significant defoliation and yield loss.'
        },
        'ur': {
            'description': 'ہدف داغ ایک فنگل بیماری ہے جو کپاس کے پتوں پر ہدف کی طرح کے دائرے والے زخم پیدا کرتی ہے۔',
            'symptoms': 'مرکزی حلقوں والے دائرے کے بھورے زخم، پیلا ہالہ، پتے گرنا۔',
            'treatment': [
                'ٹرائازول یا سٹروبیلورن پر مشتمل فنگسائڈز استعمال کریں',
                'مقاوم کپاس کی اقسام استعمال کریں',
                'فصل کی تبدیلی کریں',
                'متاثرہ پودوں کے حصے ہٹا دیں'
            ],
            'spray_method': '0.1% ارتکاز میں فنگسائڈ استعمال کریں۔ 7-10 دن کے وقفے سے چھڑکیں۔',
            'medicine_image': 'https://standishmilling.com/cdn/shop/files/1428_LifeStyle_01_1024x1024.jpg?v=1715011940',
            'video_link': 'https://www.youtube.com/watch?v=SvI_zXNgyXg',
            'disclaimer': 'اہم: ہدف داغ نمایاں پتے گرنے اور پیداوار کے نقصان کا سبب بن سکتا ہے۔'
        }
    }
}

# --- Model Loading ---
@st.cache_resource
def load_wheat_model():
    """Load wheat disease classification model"""
    try:
        model = models.resnet50(weights=None)
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, len(wheat_classes))
        
        if os.path.exists('resnet50_wheat_disease.pth'):
            model.load_state_dict(torch.load('resnet50_wheat_disease.pth', map_location=torch.device('cpu')))
        else:
            st.warning("Wheat model file not found. Using untrained model.")
        
        model.eval()
        return model
    except Exception as e:
        st.error(f"Error loading wheat model: {str(e)}")
        return None

@st.cache_resource
def load_cotton_model():
    """Load cotton disease classification model"""
    try:
        model = models.resnet50(weights=None)
        num_ftrs = model.fc.in_features
        model.fc = nn.Linear(num_ftrs, len(cotton_classes))
        
        if os.path.exists('resnet50_cotton_disease.pth'):
            model.load_state_dict(torch.load('resnet50_cotton_disease.pth', map_location=torch.device('cpu')))
        else:
            st.warning("Cotton model file not found. Using untrained model.")
        
        model.eval()
        return model
    except Exception as e:
        st.error(f"Error loading cotton model: {str(e)}")
        return None

# --- Image Transforms ---
wheat_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

cotton_transform = transforms.Compose([
    transforms.Resize(256),
    transforms.CenterCrop(224),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# --- Prediction Function ---
def predict_image(image, model, transform, classes, crop_type) -> Tuple[Optional[str], Optional[float], Optional[List[Tuple[str, float]]], bool]:
    """Predict disease from image and validate crop type"""
    try:
        img = Image.open(image).convert('RGB')
        img = transform(img).unsqueeze(0)
        
        with torch.no_grad():
            outputs = model(img)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)[0] * 100
            _, preds = torch.max(outputs, 1)
        
        num_predictions = min(3, len(classes))
        top3_prob, top3_catid = torch.topk(probabilities, num_predictions)
        
        predicted_class = classes[preds.item()]
        confidence = probabilities[preds.item()].item()
        
        top3_predictions = []
        for i in range(num_predictions):
            class_idx = top3_catid[i].item()
            prob = top3_prob[i].item()
            top3_predictions.append((classes[class_idx], prob))
        
        # Validate crop type mismatch using a different approach
        is_crop_mismatch = False
        if confidence > 70:  # Only check if confidence is high enough
            # Load both models to compare predictions
            try:
                if crop_type == "wheat":
                    # Load cotton model to check if it gives higher confidence
                    cotton_model = load_cotton_model()
                    if cotton_model:
                        cotton_outputs = cotton_model(img)
                        cotton_probs = torch.nn.functional.softmax(cotton_outputs, dim=1)[0] * 100
                        cotton_confidence = torch.max(cotton_probs).item()
                        
                        # If cotton model gives higher confidence, it's a mismatch
                        if cotton_confidence > confidence + 10:  # 10% threshold
                            is_crop_mismatch = True
                            
                elif crop_type == "cotton":
                    # Load wheat model to check if it gives higher confidence
                    wheat_model = load_wheat_model()
                    if wheat_model:
                        wheat_outputs = wheat_model(img)
                        wheat_probs = torch.nn.functional.softmax(wheat_outputs, dim=1)[0] * 100
                        wheat_confidence = torch.max(wheat_probs).item()
                        
                        # If wheat model gives higher confidence, it's a mismatch
                        if wheat_confidence > confidence + 10:  # 10% threshold
                            is_crop_mismatch = True
            except:
                # Fallback to name-based validation if model loading fails
                if crop_type == "wheat":
                    cotton_diseases = ['Aphids', 'Army worm', 'Bacterial blight', 'Cotton Boll Rot', 
                                     'Green Cotton Boll', 'Powdery mildew', 'Target spot']
                    if predicted_class in cotton_diseases:
                        is_crop_mismatch = True
                elif crop_type == "cotton":
                    wheat_diseases = ['Aphid', 'Black Rust', 'Blast', 'Brown Rust', 'Common Root Rot',
                                    'Fusarium Head Blight', 'Leaf Blight', 'Mildew', 'Mite',
                                    'Septoria', 'Smut', 'Stem fly', 'Tan spot', 'Yellow Rust']
                    if predicted_class in wheat_diseases:
                        is_crop_mismatch = True
        
        return predicted_class, confidence, top3_predictions, is_crop_mismatch
    except Exception as e:
        st.error(f"Error during prediction: {str(e)}")
        return None, None, None, False

# --- Classification Page ---
def classification_page(crop_type: str):
    """Main classification page for wheat or cotton"""
    language = get_language()
    
    # Set up page header
    if crop_type == "wheat":
        crop_emoji = "🌾"
        crop_name_en = "Wheat"
        crop_name_ur = "گندم"
        classes = wheat_classes_urdu if language == "Urdu" else wheat_classes
        model = load_wheat_model()
        transform = wheat_transform
    else:
        crop_emoji = "🧵"
        crop_name_en = "Cotton"
        crop_name_ur = "کپاس"
        classes = cotton_classes_urdu if language == "Urdu" else cotton_classes
        model = load_cotton_model()
        transform = cotton_transform
    
    # Header with proper titles
    if language == "Urdu":
        if crop_type == "wheat":
            main_title = "🌾 گندم کی بیماریوں کی درجہ بندی"
        else:  # cotton
            main_title = "🧵 کپاس  کی بیماریوں کی درجہ بندی"
    else:
        main_title = f"{crop_emoji} {crop_name_en} Disease Classification"
    
    st.markdown(f"""
    <div class='main-container'>
        <h1 class='urdu-header' style='color: #2E7D32;'>
            {main_title}
        </h1>
        <h3 class='urdu-subtitle'>{'مصنوعی ذہانت سے بیماری کی تشخیص' if language == "Urdu" else 'AI-Powered Disease Detection'}</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Back button
    if st.button("← Back to Dashboard", key=f"back_{crop_type}"):
        st.session_state.page = "dashboard"
        st.rerun()
    
    # Check if file was uploaded from sidebar
    uploaded_file = None
    if 'sidebar_uploaded_file' in st.session_state and st.session_state.page == crop_type:
        uploaded_file = st.session_state.sidebar_uploaded_file
        st.success(f"✅ Image uploaded from sidebar - {crop_name_en}")
        # Clear the sidebar uploaded file after using it
        del st.session_state.sidebar_uploaded_file
    
    # File upload (if not uploaded from sidebar)
    if uploaded_file is None:
        if language == "English":
            uploaded_file = st.file_uploader(
                f"Upload a photo of your {crop_name_en.lower()} plant",
                type=['jpg', 'jpeg', 'png'],
                help="Upload a clear image of the affected plant part"
            )
        else:
            uploaded_file = st.file_uploader(
                f"اپنی {crop_name_ur} کی تصویر اپ لوڈ کریں",
                type=['jpg', 'jpeg', 'png'],
                help="متاثرہ پودے کے حصے کی واضح تصویر اپ لوڈ کریں"
            )
    
    if uploaded_file is not None:
        # Display uploaded image
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("📸 Uploaded Image")
            st.image(uploaded_file, use_column_width=True)
        
        with col2:
            st.subheader("🔍 Analysis Results")
            
            if model is None:
                st.error("Model not available. Please check model files.")
                return
            
            # Prediction
            with st.spinner("Analyzing image..."):
                predicted_class, confidence, top3_predictions, is_crop_mismatch = predict_image(
                    uploaded_file, model, transform, classes, crop_type
                )
            
            if predicted_class and confidence is not None:
                # Check for crop mismatch
                if is_crop_mismatch:
                    st.markdown(f"""
                    <div style='background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%); color: white; padding: 1rem; border-radius: 10px; text-align: center; font-weight: bold; margin: 1rem 0;'>
                        ⚠️ <strong>Crop Type Mismatch Detected!</strong><br>
                        You selected {crop_type.title()} but the image appears to be {('Cotton' if crop_type == 'wheat' else 'Wheat')}.<br>
                        Please select the correct crop type for accurate diagnosis.
                    </div>
                    """, unsafe_allow_html=True)
                
                # Display results
                st.markdown(f"""
                <div class='prediction-card'>
                    <h3>🎯 Primary Diagnosis</h3>
                    <h2 style='color: #4CAF50;'>{predicted_class}</h2>
                    <p><strong>Confidence:</strong> {confidence:.1f}%</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Top 3 predictions
                if top3_predictions:
                    st.markdown("### 📊 Top 3 Predictions")
                    for i, (class_name, prob) in enumerate(top3_predictions, 1):
                        st.markdown(f"""
                        <div class='prediction-card'>
                            <p><strong>{i}.</strong> {class_name} - {prob:.1f}%</p>
                        </div>
                        """, unsafe_allow_html=True)
        
        # Treatment recommendations - Full width below both columns
        if predicted_class and confidence is not None:
            # Normalize the predicted class name (remove extra spaces, standardize)
            normalized_class = predicted_class.strip()
            
            # Convert Urdu class name to English if needed
            if normalized_class in urdu_to_english_mapping:
                english_class = urdu_to_english_mapping[normalized_class]
                st.info(f"Detected Urdu class name: '{normalized_class}' → English: '{english_class}'")
                normalized_class = english_class
            
            # Check if predicted class exists in treatment recommendations
            if normalized_class in treatment_recommendations:
                # Get language key (en or ur)
                lang_key = 'ur' if language == 'Urdu' else 'en'
                
                # Check if the language data exists for this disease
                if lang_key in treatment_recommendations[normalized_class]:
                    treatment_data = treatment_recommendations[normalized_class][lang_key]
                else:
                    # Fallback to English if Urdu not available
                    treatment_data = treatment_recommendations[normalized_class]['en']
                    st.warning(f"Urdu treatment information not available for {normalized_class}. Showing English version.")
            else:
                st.error(f"Treatment information not found for disease: '{normalized_class}'")
                st.info("Available diseases: " + ", ".join(list(treatment_recommendations.keys())))
                st.info("Please contact support to add treatment information for this disease.")
                return
            
            # Full page treatment section
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, rgba(255, 255, 255, 0.95) 0%, rgba(240, 248, 255, 0.95) 100%); 
                        border-radius: 20px; padding: 3rem; margin: 2rem 0; 
                        box-shadow: 0 10px 40px rgba(0,0,0,0.2); border: 2px solid #4CAF50;'>
                <h1 style='color: #2E7D32; margin-bottom: 3rem; text-align: center; font-size: 2.5rem;'>
                    💊 {'علاج کی تفصیلی معلومات' if language == 'Urdu' else 'Detailed Treatment Information'}
                </h1>
            </div>
            """, unsafe_allow_html=True)
            
            # Create two columns for better layout
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Description
                st.markdown(f"""
                <div style='background: rgba(255, 255, 255, 0.9); padding: 2rem; border-radius: 15px; 
                            margin: 1rem 0; border-left: 5px solid #4CAF50;'>
                    <h2 style='color: #2E7D32; margin-bottom: 1rem;'>📋 {'تفصیل' if language == 'Urdu' else 'Description'}</h2>
                    <p style='font-size: 1.1rem; line-height: 1.6;'>{treatment_data['description']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Symptoms
                st.markdown(f"""
                <div style='background: rgba(255, 255, 255, 0.9); padding: 2rem; border-radius: 15px; 
                            margin: 1rem 0; border-left: 5px solid #FF9800;'>
                    <h2 style='color: #E65100; margin-bottom: 1rem;'>🔍 {'علامات' if language == 'Urdu' else 'Symptoms'}</h2>
                    <p style='font-size: 1.1rem; line-height: 1.6;'>{treatment_data['symptoms']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Spray Method
                st.markdown(f"""
                <div style='background: rgba(255, 255, 255, 0.9); padding: 2rem; border-radius: 15px; 
                            margin: 1rem 0; border-left: 5px solid #2196F3;'>
                    <h2 style='color: #1565C0; margin-bottom: 1rem;'>🌿 {'چھڑکاؤ کا طریقہ' if language == 'Urdu' else 'Spray Method'}</h2>
                    <p style='font-size: 1.1rem; line-height: 1.6;'>{treatment_data['spray_method']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                # Medicine Image
                st.markdown(f"""
                <div style='background: rgba(255, 255, 255, 0.9); padding: 2rem; border-radius: 15px; 
                            margin: 1rem 0; border-left: 5px solid #FFC107;'>
                    <h2 style='color: #F57F17; margin-bottom: 1rem;'>💊 {'دوا کی تصویر' if language == 'Urdu' else 'Medicine Image'}</h2>
                    <div style='text-align: center;'>
                        <img src="{treatment_data['medicine_image']}" alt="Medicine" 
                             style='max-width: 100%; height: auto; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.2);'>
                        <p style='margin-top: 1rem; font-size: 0.9rem; color: #666;'>
                            {'مثال کے طور پر دکھائی گئی تصویر' if language == 'Urdu' else 'Example medicine image'}
                        </p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Treatment Recommendations
                st.markdown(f"""
                <div style='background: rgba(255, 255, 255, 0.9); padding: 2rem; border-radius: 15px; 
                            margin: 1rem 0; border-left: 5px solid #9C27B0;'>
                    <h2 style='color: #6A1B9A; margin-bottom: 1rem;'>💡 {'علاج کی تجاویز' if language == 'Urdu' else 'Treatment Recommendations'}</h2>
                </div>
                """, unsafe_allow_html=True)
                
                for i, item in enumerate(treatment_data['treatment'], 1):
                    st.markdown(f"""
                    <div style='background: rgba(255, 255, 255, 0.8); padding: 1rem; border-radius: 10px; 
                                margin: 0.5rem 0; border-left: 3px solid #9C27B0;'>
                        <p style='font-size: 1rem; margin: 0;'><strong>{i}.</strong> {item}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                # Video Guide
                st.markdown(f"""
                <div style='background: rgba(255, 255, 255, 0.9); padding: 2rem; border-radius: 15px; 
                            margin: 1rem 0; border-left: 5px solid #FF5722;'>
                    <h2 style='color: #D84315; margin-bottom: 1rem;'>📹 {'ویڈیو گائیڈ' if language == 'Urdu' else 'Video Guide'}</h2>
                    <a href="{treatment_data['video_link']}" target="_blank" 
                       style='color: #4CAF50; text-decoration: none; font-size: 1.1rem; font-weight: bold;'>
                        🎥 {'یوٹیوب پر دیکھیں' if language == 'Urdu' else 'Watch on YouTube'}
                    </a>
                </div>
                """, unsafe_allow_html=True)
                
                # Expert Consultation
                st.markdown(f"""
                <div style='background: rgba(255, 255, 255, 0.9); padding: 2rem; border-radius: 15px; 
                            margin: 1rem 0; border-left: 5px solid #607D8B;'>
                    <h2 style='color: #37474F; margin-bottom: 1rem;'>🏥 {'ماہرین سے رابطہ' if language == 'Urdu' else 'Expert Consultation'}</h2>
                    <p style='font-size: 1.1rem; margin: 0.5rem 0;'><strong>{'زرعی توسیع کے دفتر سے رابطہ کریں' if language == 'Urdu' else 'Contact your local agricultural extension office'}</strong></p>
                    <p style='font-size: 1.1rem; margin: 0.5rem 0;'><strong>{'یا قریبی زرعی ماہر سے مشورہ کریں' if language == 'Urdu' else 'Or consult with a nearby agricultural expert'}</strong></p>
                </div>
                """, unsafe_allow_html=True)
            
            # Important Disclaimer - Full width
            st.markdown(f"""
            <div style='background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%); color: white; 
                        padding: 2rem; border-radius: 20px; margin: 2rem 0; text-align: center;
                        box-shadow: 0 8px 25px rgba(255, 107, 107, 0.3);'>
                <h2 style='margin-bottom: 1rem; font-size: 1.8rem;'>⚠️ {'اہم تنبیہ' if language == 'Urdu' else 'IMPORTANT DISCLAIMER'}</h2>
                <p style='font-size: 1.2rem; margin: 1rem 0; line-height: 1.6;'><strong>{treatment_data['disclaimer']}</strong></p>
                <p style='font-size: 1.2rem; line-height: 1.6;'><strong>{'براہ کرم زرعی ماہرین سے مشورہ کریں' if language == 'Urdu' else 'Please consult agricultural experts before applying any treatment'}</strong></p>
            </div>
            """, unsafe_allow_html=True)
        elif predicted_class and confidence is not None:
            st.markdown(f"### 💊 {'علاج کی معلومات' if language == 'Urdu' else 'Treatment Information'}")
            st.warning("Treatment information not available for this diagnosis." if language == "English" else "اس بیماری کے لیے علاج کی معلومات دستیاب نہیں ہے")
            st.markdown(f"**{'براہ کرم زرعی ماہرین سے مشورہ کریں' if language == 'Urdu' else 'Please consult agricultural experts for proper treatment.'}**")

# --- Dashboard Page ---
def dashboard():
    """Main dashboard page"""
    language = get_language()
    
    # Hero section
    if language == "English":
        st.markdown("""
        <div class='main-container'>
            <h1 style='text-align: center; color: #2E7D32; font-size: 3rem;'>
                🌾 Pakistani Crop Doctor
            </h1>
            <h3 style='text-align: center; color: #4CAF50; font-size: 1.5rem;'>
                AI-Powered Crop Disease Diagnosis
            </h3>
            <p style='text-align: center; font-size: 1.2rem; margin-top: 1rem;'>
                Empowering Pakistani farmers with intelligent disease detection
            </p>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='main-container'>
            <h1 class='urdu-header' style='text-align: center; color: #2E7D32; font-size: 3rem;'>
                🌾 پاکستانی فصل ڈاکٹر
            </h1>
            <h3 class='urdu-subtitle' style='text-align: center; color: #4CAF50; font-size: 1.5rem;'>
                مصنوعی ذہانت سے فصل کی بیماری کی تشخیص
            </h3>
            <p class='urdu-text' style='text-align: center; font-size: 1.2rem; margin-top: 1rem; direction: rtl;'>
                ذہین بیماری کی تشخیص کے ساتھ پاکستانی کسانوں کو بااختیار بنانا
            </p>
        </div>
        """, unsafe_allow_html=True)
    
    # Welcome section
    if language == "English":
        st.markdown("""
        <div class='main-container'>
            <h2>👨‍🌾 Welcome Pakistani Farmers!</h2>
            <p style='font-size: 1.1rem; line-height: 1.6;'>
                This intelligent system helps you identify diseases in your wheat and cotton crops 
                using advanced artificial intelligence technology. Get instant diagnosis and treatment 
                recommendations in both English and Urdu.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("### 🔧 How It Works:")
        st.markdown("""
        1. **Select your crop type** (Wheat or Cotton)
        2. **Upload a clear photo** of affected leaves or plant parts
        3. **Get instant diagnosis** with confidence score
        4. **View treatment recommendations** for better crop health
        """)
    else:
        st.markdown("""
        <div class='main-container'>
            <h2 class='urdu-header' style='color: #2E7D32; font-size: 2.5rem; margin-bottom: 2rem;'>
                👨‍🌾 پاکستانی کسانوں کو خوش آمدید!
            </h2>
            <p class='urdu-text' style='font-size: 1.3rem; line-height: 2.5; text-align: justify; margin-bottom: 2rem; font-weight: 500; direction: rtl; margin-top: 1.5rem;'>
                یہ ذہین نظام جدید مصنوعی ذہانت کی ٹیکنالوجی کے ذریعے گندم اور کپاس کی بیماریوں کی شناخت میں مدد کرتا ہے۔ فوری تشخیص اور علاج کی سفارشات انگریزی اور اردو دونوں زبانوں میں حاصل کریں۔
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class='main-container'>
            <h3 class='urdu-subtitle' style='color: #4CAF50; margin-bottom: 1.5rem;'>🔧 یہ کیسے کام کرتا ہے:</h3>
            <div class='urdu-text' style='font-size: 1.2rem; line-height: 2.2;'>
                <p><strong>1.</strong> اپنی فصل کی قسم منتخب کریں (گندم یا کپاس)</p>
                <p><strong>2.</strong> متاثرہ پتوں کی واضح تصویر اپ لوڈ کریں</p>
                <p><strong>3.</strong> اعتماد کے اسکور کے ساتھ فوری تشخیص حاصل کریں</p>
                <p><strong>4.</strong> بہتر فصل کی صحت کے لیے علاج کی سفارشات دیکھیں</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Crop selection buttons
    if language == "English":
        st.markdown("""
        <div style='text-align: center; margin: 2rem 0;'>
            <h3>🌱 Select Your Crop to Begin</h3>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align: center; margin: 2rem 0;'>
            <h3 class='urdu-subtitle'>🌱 اپنی فصل منتخب کریں</h3>
        </div>
        """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        if language == "English":
            if st.button("🌾 Wheat Disease Classification", key="wheat_btn", use_container_width=True):
                st.session_state.page = "wheat"
                st.rerun()
        else:
            if st.button("🌾 گندم کی بیماریوں کی درجہ بندی", key="wheat_btn", use_container_width=True):
                st.session_state.page = "wheat"
                st.rerun()
    with col2:
        if language == "English":
            if st.button("🧵 Cotton Disease Classification", key="cotton_btn", use_container_width=True):
                st.session_state.page = "cotton"
                st.rerun()
        else:
            if st.button("🧵 کپاس کی بیماریوں کی درجہ بندی", key="cotton_btn", use_container_width=True):
                st.session_state.page = "cotton"
                st.rerun()
    
    # How to Use section
    if language == "English":
        st.markdown("""
        <div class='main-container'>
            <h2>🎯 How to Use</h2>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;'>
                <div style='background: rgba(255, 255, 255, 0.95); padding: 1.5rem; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 4px solid #4CAF50;'>
                    <h4 style='color: #1B5E20; font-weight: bold; margin-bottom: 0.5rem; text-shadow: 1px 1px 2px rgba(255,255,255,0.8);'>1️⃣ Select Crop</h4>
                    <p style='color: #2E2E2E; font-weight: 500; margin: 0; text-shadow: 1px 1px 2px rgba(255,255,255,0.8);'>Choose between Wheat or Cotton from the main dashboard</p>
                </div>
                <div style='background: rgba(255, 255, 255, 0.95); padding: 1.5rem; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 4px solid #4CAF50;'>
                    <h4 style='color: #1B5E20; font-weight: bold; margin-bottom: 0.5rem; text-shadow: 1px 1px 2px rgba(255,255,255,0.8);'>2️⃣ Upload Photo</h4>
                    <p style='color: #2E2E2E; font-weight: 500; margin: 0; text-shadow: 1px 1px 2px rgba(255,255,255,0.8);'>Take a clear photo of the affected plant part</p>
                </div>
                <div style='background: rgba(255, 255, 255, 0.95); padding: 1.5rem; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 4px solid #4CAF50;'>
                    <h4 style='color: #1B5E20; font-weight: bold; margin-bottom: 0.5rem; text-shadow: 1px 1px 2px rgba(255,255,255,0.8);'>3️⃣ Get Diagnosis</h4>
                    <p style='color: #2E2E2E; font-weight: 500; margin: 0; text-shadow: 1px 1px 2px rgba(255,255,255,0.8);'>Receive instant AI-powered disease diagnosis</p>
                </div>
                <div style='background: rgba(255, 255, 255, 0.95); padding: 1.5rem; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 4px solid #4CAF50;'>
                    <h4 style='color: #1B5E20; font-weight: bold; margin-bottom: 0.5rem; text-shadow: 1px 1px 2px rgba(255,255,255,0.8);'>4️⃣ Treatment Guide</h4>
                    <p style='color: #2E2E2E; font-weight: 500; margin: 0; text-shadow: 1px 1px 2px rgba(255,255,255,0.8);'>View detailed treatment recommendations</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class='main-container'>
            <h2 class='urdu-subtitle' style='color: #4CAF50; margin-bottom: 1.5rem;'>🎯 استعمال کرنے کا طریقہ</h2>
            <div style='display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;'>
                <div style='background: rgba(255, 255, 255, 0.95); padding: 1.5rem; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 4px solid #4CAF50;'>
                    <h4 class='urdu-text' style='color: #1B5E20; font-weight: bold; margin-bottom: 0.5rem; direction: rtl;'>1️⃣ فصل منتخب کریں</h4>
                    <p class='urdu-text' style='color: #2E2E2E; font-weight: 500; margin: 0; direction: rtl; line-height: 1.8;'>مین ڈیش بورڈ سے گندم یا کپاس منتخب کریں</p>
                </div>
                <div style='background: rgba(255, 255, 255, 0.95); padding: 1.5rem; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 4px solid #4CAF50;'>
                    <h4 class='urdu-text' style='color: #1B5E20; font-weight: bold; margin-bottom: 0.5rem; direction: rtl;'>2️⃣ تصویر اپ لوڈ کریں</h4>
                    <p class='urdu-text' style='color: #2E2E2E; font-weight: 500; margin: 0; direction: rtl; line-height: 1.8;'>متاثرہ پودے کے حصے کی واضح تصویر لیں</p>
                </div>
                <div style='background: rgba(255, 255, 255, 0.95); padding: 1.5rem; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 4px solid #4CAF50;'>
                    <h4 class='urdu-text' style='color: #1B5E20; font-weight: bold; margin-bottom: 0.5rem; direction: rtl;'>3️⃣ تشخیص حاصل کریں</h4>
                    <p class='urdu-text' style='color: #2E2E2E; font-weight: 500; margin: 0; direction: rtl; line-height: 1.8;'>فوری AI سے طاقتور بیماری کی تشخیص حاصل کریں</p>
                </div>
                <div style='background: rgba(255, 255, 255, 0.95); padding: 1.5rem; border-radius: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 4px solid #4CAF50;'>
                    <h4 class='urdu-text' style='color: #1B5E20; font-weight: bold; margin-bottom: 0.5rem; direction: rtl;'>4️⃣ علاج کی رہنمائی</h4>
                    <p class='urdu-text' style='color: #2E2E2E; font-weight: 500; margin: 0; direction: rtl; line-height: 1.8;'>تفصیلی علاج کی سفارشات دیکھیں</p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# --- Sidebar Configuration ---
with st.sidebar:
    # Crop icons header
    st.markdown("## 🌾 🧵")
    
    st.title("🌱 Pakistani Crop Doctor")
    st.markdown("---")
    
    # Language selector
    current_language = get_language()
    lang = st.radio(
        "🌍 Select Language / زبان منتخب کریں",
        ["English", "Urdu"],
        index=0 if current_language == "English" else 1,
        key="language_selector"
    )
    
    # Update language if changed
    if lang != current_language:
        set_language(lang)
        st.rerun()
    
    st.markdown("---")
    
    # Crop information
    st.markdown("### 🌾 Wheat Diseases")
    st.markdown("**15 Disease Types:**")
    st.markdown("- Aphid, Black Rust, Blast")
    st.markdown("- Brown Rust, Root Rot")
    st.markdown("- Fusarium, Leaf Blight")
    st.markdown("- Mildew, Mite, Septoria")
    st.markdown("- Smut, Stem fly, Tan spot")
    st.markdown("- Yellow Rust, Healthy")
    
    st.markdown("---")
    
    st.markdown("### 🧵 Cotton Diseases")
    st.markdown("**8 Disease Types:**")
    st.markdown("- Aphids, Army worm")
    st.markdown("- Bacterial blight")
    st.markdown("- Boll Rot, Green Boll")
    st.markdown("- Powdery mildew")
    st.markdown("- Target spot, Healthy")
    
    st.markdown("---")
    st.markdown("""
    **🌾 Farmer Benefits:**
    - 💰 Save money on crop losses
    - ⏰ Early disease detection
    - 📱 Easy mobile access
    - 🎯 Accurate AI diagnosis
    - 💊 Expert treatment advice
    - 🌍 Available in Urdu/English
    """)

# --- Main App ---
def main():
    """Main application function"""
    if 'page' not in st.session_state:
        st.session_state.page = "dashboard"
    
    if st.session_state.page == "dashboard":
        dashboard()
    elif st.session_state.page == "wheat":
        classification_page("wheat")
    elif st.session_state.page == "cotton":
        classification_page("cotton")

if __name__ == "__main__":
    main()
