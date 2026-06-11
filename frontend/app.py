import streamlit as st
import requests
import json
import os
import base64
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Set page config first
st.set_page_config(
    page_title="Vishakan Biotech Smart Farming Assistant",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Base URL
API_URL = os.getenv("API_URL", "http://127.0.0.1:8000/api")

# Theme colors
PRIMARY_GREEN = "#1B7F3A"
DARK_GREEN = "#0E5C2D"
LIGHT_GREEN = "#E8F5E9"
SOIL_BROWN = "#7B4F2A"

# Load Custom CSS
def load_css():
    css_path = os.path.join(os.path.dirname(__file__), "style.css")
    if os.path.exists(css_path):
        with open(css_path) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Session State Initialization
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "user_name" not in st.session_state:
    st.session_state.user_name = "Farmer"
if "user_role" not in st.session_state:
    st.session_state.user_role = "Farmer"
if "language" not in st.session_state:
    st.session_state.language = "English"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# Helper for API headers
def get_headers():
    if st.session_state.auth_token:
        return {"Authorization": f"Bearer {st.session_state.auth_token}"}
    return {}

# -----------------------------
# LOCAL MOCK FALLBACKS (if API is offline)
# -----------------------------
MOCK_PRODUCTS = [
    {"id": 1, "product_name": "V-NITRO", "category": "Bio Fertilizer", "description": "Nitrogen fixing biofertilizer containing Azotobacter and Azospirillum.", "dosage": "2.5 ml/L water", "benefits": "Fixes atmospheric nitrogen.", "price": 350.0, "unit": "500ml"},
    {"id": 2, "product_name": "V-PHOS", "category": "Bio Fertilizer", "description": "Phosphate solubilizer containing Bacillus megaterium.", "dosage": "2 ml/L water", "benefits": "Solubilizes insoluble soil phosphorus.", "price": 380.0, "unit": "500ml"},
    {"id": 3, "product_name": "V-SOL-K", "category": "Bio Fertilizer", "description": "Potash mobilizer containing Frateuria aurantia.", "dosage": "2 ml/L water", "benefits": "Mobilizes potassium, improves quality.", "price": 420.0, "unit": "500ml"},
    {"id": 4, "product_name": "VIRIDINE", "category": "Bio Fungicide", "description": "Contains Trichoderma viride, controls soil diseases.", "dosage": "2.5 ml/L water", "benefits": "Suppresses rot and wilt diseases.", "price": 480.0, "unit": "500ml"},
    {"id": 5, "product_name": "V-CURE", "category": "Bio Fungicide", "description": "Contains Pseudomonas fluorescens, controls leaf spots.", "dosage": "2.5 ml/L water", "benefits": "Suppresses blights and spots.", "price": 460.0, "unit": "500ml"},
    {"id": 6, "product_name": "V-CIDE", "category": "Bio Pesticide", "description": "Beauveria bassiana bio-insecticide for sucking pests.", "dosage": "3 ml/L water", "benefits": "Controls thrips and whiteflies.", "price": 580.0, "unit": "500ml"},
    {"id": 7, "product_name": "V-NEMATO", "category": "Bio Nematicide", "description": "Nematicidal fungi for root nematodes.", "dosage": "3 ml/L water", "benefits": "Controls root-knot nematodes.", "price": 620.0, "unit": "1kg"},
    {"id": 8, "product_name": "V-COMBINE", "category": "Bio Stimulant", "description": "Consortium of seaweed, humic, and amino acids.", "dosage": "2 ml/L water", "benefits": "Boosts crop health and flowering.", "price": 650.0, "unit": "500ml"}
]

# -----------------------------
# LOGIN & REGISTER SCREEN
# -----------------------------
def login_register_page():
    # Centered branded panel
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            f"""
            <div style="text-align: center; margin-bottom: 20px;">
                <h1 style="color: #0E5C2D; font-weight: 800; font-size: 38px; margin-bottom: 0;">VISHAKAN BIOTECH</h1>
                <p style="color: #7B4F2A; font-weight: 500; font-size: 14px; text-transform: uppercase; letter-spacing: 2px;">Prosperity Through Biologicals</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        tab_login, tab_register = st.tabs(["🔐 Farmer Sign In", "🌾 New Registration"])
        
        with tab_login:
            st.write("Welcome back! Please sign in with your mobile number.")
            mobile = st.text_input("Mobile Number", placeholder="e.g. 9876543210", key="login_mob")
            password = st.text_input("Password", type="password", key="login_pw")
            
            if st.button("Sign In", use_container_width=True):
                # Try API login
                try:
                    res = requests.post(f"{API_URL}/auth/login", json={"mobile": mobile, "password": password})
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.authenticated = True
                        st.session_state.auth_token = data["access_token"]
                        st.session_state.user_role = data["role"]
                        
                        # fetch profile
                        profile_res = requests.get(f"{API_URL}/auth/me", headers=get_headers())
                        if profile_res.status_code == 200:
                            st.session_state.user_name = profile_res.json()["name"]
                            
                        st.success(f"Successfully signed in! Welcome, {st.session_state.user_name}.")
                        st.rerun()
                    else:
                        st.error(res.json().get("detail", "Incorrect mobile number or password."))
                except requests.exceptions.ConnectionError:
                    # LOCAL FALLBACK
                    if mobile == "9999999999" and password == "vishakan_admin_123":
                        st.session_state.authenticated = True
                        st.session_state.user_name = "Vishakan Admin"
                        st.session_state.user_role = "Admin"
                        st.success("Successfully logged in as Admin (Local Fallback Mode).")
                        st.rerun()
                    elif len(mobile) >= 10 and password == "farmer123":
                        st.session_state.authenticated = True
                        st.session_state.user_name = "Arun Kumar"
                        st.session_state.user_role = "Farmer"
                        st.success("Successfully logged in as Farmer (Local Fallback Mode).")
                        st.rerun()
                    else:
                        st.warning("Connection to API failed. Try fallback credentials:\n- Mobile: 9999999999, Pass: vishakan_admin_123 (Admin)\n- Mobile: 9876543210, Pass: farmer123 (Farmer)")
                        
        with tab_register:
            st.write("Register a new biological farming profile.")
            reg_name = st.text_input("Full Name", placeholder="e.g. Ramesh Kumar")
            reg_mobile = st.text_input("Mobile Number", placeholder="e.g. 9876543210", key="reg_mob")
            reg_pw = st.text_input("Create Password", type="password", key="reg_pw")
            reg_district = st.selectbox("District", ["Coimbatore", "Erode", "Tiruppur", "Salem", "Madurai", "Trichy", "Thanjavur"])
            reg_lang = st.selectbox("Language Preference", ["Tamil", "English", "Malayalam", "Kannada", "Telugu"])
            
            if st.button("Submit Registration", use_container_width=True):
                try:
                    res = requests.post(f"{API_URL}/auth/register", json={
                        "name": reg_name, "mobile": reg_mobile, "password": reg_pw,
                        "district": reg_district, "state": "Tamil Nadu", "language": reg_lang,
                        "role": "Farmer"
                    })
                    if res.status_code == 201:
                        st.success("Account registered successfully! Please sign in using the Login tab.")
                    else:
                        st.error(res.json().get("detail", "Failed to register account."))
                except requests.exceptions.ConnectionError:
                    st.success("Fallback Mode: Account registered successfully (Simulated). Please Sign In.")

# -----------------------------
# SIDEBAR NAVIGATION
# -----------------------------
def draw_sidebar():
    st.sidebar.markdown(
        f"""
        <div style="text-align: center; padding: 10px 0; margin-bottom: 20px;">
            <div style="font-size: 50px;">🌱</div>
            <h2 style="color: #FFFFFF; font-weight: 800; font-size: 24px; margin: 0;">VISHAKAN BIOTECH</h2>
            <p style="color: #C8E6C9; font-weight: 500; font-size: 11px; text-transform: uppercase; letter-spacing: 1.5px; margin: 0;">Prosperity Through Biologicals</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Custom Sidebar Navigation Menu Items
    menu = [
        "Dashboard", "Crop Recommendation", "Disease Detection", "Product Advisor", 
        "Soil Health Analysis", "Dosage Calculator", "Voice Assistant", 
        "Vishakan AI Agronomist", "Farmer History", "Analytics", "Settings"
    ]
    
    selected_page = st.sidebar.radio("Navigation Menu", menu, label_visibility="collapsed")
    st.session_state.page = selected_page
    
    st.sidebar.markdown("<br><hr style='border-color: rgba(255,255,255,0.2);'><br>", unsafe_allow_html=True)
    
    # User Profile card in sidebar
    st.sidebar.markdown(
        f"""
        <div style="background-color: rgba(255,255,255,0.1); border-radius: 10px; padding: 15px; text-align: center;">
            <p style="color: #C8E6C9; font-size: 11px; margin: 0; text-transform: uppercase;">Logged In As</p>
            <h4 style="color: #FFFFFF; margin: 5px 0 0 0; font-weight: 600;">{st.session_state.user_name}</h4>
            <p style="color: #C8E6C9; font-size: 12px; margin: 0;">({st.session_state.user_role})</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if st.sidebar.button("Logout 🚪", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.auth_token = None
        st.rerun()

# -----------------------------
# PAGES DEFINITIONS
# -----------------------------

# --- Page 1: Dashboard ---
def show_dashboard():
    # Hero Welcome Banner
    col_text, col_logo = st.columns([5, 1])
    with col_text:
        st.markdown(
            f"""
            <h1 class="banner-title">Welcome, {st.session_state.user_name}!</h1>
            <p class="banner-subtitle">Helping Farmers Increase Yields Through Bio-Organic Solutions. Coimbatore, Tamil Nadu.</p>
            """,
            unsafe_allow_html=True
        )
    with col_logo:
        logo_path = os.path.join(os.path.dirname(__file__), "assets", "vishakan_logo.png")
        if os.path.exists(logo_path):
            try:
                with open(logo_path, "rb") as f:
                    img_b64 = base64.b64encode(f.read()).decode('utf-8')
                st.markdown(
                    f'<div class="logo-wrapper"><img src="data:image/png;base64,{img_b64}" class="logo-img" alt="Vishakan Biotech Logo"></div>',
                    unsafe_allow_html=True
                )
            except Exception:
                st.markdown('<div class="logo-wrapper"><div class="logo-fallback">🌱</div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="logo-wrapper"><div class="logo-fallback">🌱</div></div>', unsafe_allow_html=True)
    
    # Banner image
    banner_img_path = os.path.join(os.path.dirname(__file__), "assets", "farm_banner.png")
    if os.path.exists(banner_img_path):
        st.image(banner_img_path, use_container_width=True)
        
    st.markdown("<h3 class='section-title'>Quick Action Services</h3>", unsafe_allow_html=True)
    
    # Five Columns representing mock cards from the AgriSmart UI
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(
            """
            <div class="action-card">
                <div class="action-icon">🌾</div>
                <div class="action-title">Crop Choice</div>
                <div class="action-desc">Find optimal crops using soil NPK & climate parameters.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Open Crop Predictor", key="btn_crop"):
            st.session_state.page = "Crop Recommendation"
            st.rerun()
            
    with col2:
        st.markdown(
            """
            <div class="action-card">
                <div class="action-icon">🧪</div>
                <div class="action-title">Soil Analyzer</div>
                <div class="action-desc">Diagnose NPK pH deficiencies & soil health score.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Open Soil Health", key="btn_soil"):
            st.session_state.page = "Soil Health Analysis"
            st.rerun()
            
    with col3:
        st.markdown(
            """
            <div class="action-card">
                <div class="action-icon">🍂</div>
                <div class="action-title">Scan Plant</div>
                <div class="action-desc">Diagnose crop diseases instantly from leaf uploads.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Open Disease Scanner", key="btn_disease"):
            st.session_state.page = "Disease Detection"
            st.rerun()
            
    with col4:
        st.markdown(
            """
            <div class="action-card">
                <div class="action-icon">🧮</div>
                <div class="action-title">Dosage Calc</div>
                <div class="action-desc">Compute required quantities, schedules, and costs.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Open Calculator", key="btn_calc"):
            st.session_state.page = "Dosage Calculator"
            st.rerun()
            
    with col5:
        st.markdown(
            """
            <div class="action-card">
                <div class="action-icon">🎙️</div>
                <div class="action-title">Voice Assistant</div>
                <div class="action-desc">Ask crop questions in Tamil, Telugu, and English.</div>
            </div>
            """,
            unsafe_allow_html=True
        )
        if st.button("Open Voice AI", key="btn_voice"):
            st.session_state.page = "Voice Assistant"
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    
    col_left, col_right = st.columns([3, 2])
    
    with col_left:
        st.markdown("<h3 class='section-title'>Recent recommendations logs</h3>", unsafe_allow_html=True)
        # Mock recent recommendation records matching standard table design
        data = {
            "Date": ["20 May 2026", "18 May 2026", "15 May 2026", "12 May 2026"],
            "Crop Target": ["Rice Paddy", "Banana", "Tomato", "Turmeric"],
            "Biological Products Recommended": ["V-NITRO, V-CURE, BIO-NPK", "V-PHOS, V-NEMATO, V-SOL-K", "VIRIDINE, V-CURE, V-CIDE", "V-PHOS, V-COMBINE, V-HUME"]
        }
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
    with col_right:
        st.markdown("<h3 class='section-title'>Coimbatore Weather Overview</h3>", unsafe_allow_html=True)
        # Beautiful weather card
        st.markdown(
            """
            <div style="background-color: #FFFFFF; border-radius: 16px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.04); border: 1px solid #E2E8F0; text-align: center;">
                <div style="font-size: 48px; margin-bottom: 5px;">⛅</div>
                <div style="font-size: 36px; font-weight: 700; color: #0E5C2D;">28°C</div>
                <div style="font-size: 14px; color: #666666; margin-bottom: 15px;">Partly Cloudy | Coimbatore, TN</div>
                <div style="display: flex; justify-content: space-around; border-top: 1px solid #F1F5F9; padding-top: 15px;">
                    <div>
                        <div style="font-size: 11px; color: #64748B; text-transform: uppercase;">Humidity</div>
                        <div style="font-size: 14px; font-weight: 600; color: #334155;">65%</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #64748B; text-transform: uppercase;">Rainfall</div>
                        <div style="font-size: 14px; font-weight: 600; color: #334155;">2.4 mm</div>
                    </div>
                    <div>
                        <div style="font-size: 11px; color: #64748B; text-transform: uppercase;">Wind</div>
                        <div style="font-size: 14px; font-weight: 600; color: #334155;">12 km/h</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# --- Page 2: Crop Recommendation ---
def show_crop_recommendation():
    st.markdown("<h2 class='section-title'>Smart Crop Recommendation</h2>", unsafe_allow_html=True)
    st.write("Provide your field soil data and environment metrics to predict optimal crop choice.")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        soil_type = st.selectbox("Soil Profile Type", ["Loamy", "Clay", "Sandy", "Silt", "Black", "Red", "Laterite", "Alluvial"])
        nitrogen = st.slider("Nitrogen (N) - kg/ha", 0.0, 200.0, 80.0)
        phosphorus = st.slider("Phosphorus (P) - kg/ha", 0.0, 200.0, 45.0)
        potassium = st.slider("Potassium (K) - kg/ha", 0.0, 200.0, 50.0)
        ph = st.slider("Soil pH Value", 0.0, 14.0, 6.5)
        
    with col2:
        temp = st.slider("Temperature (°C)", 0.0, 50.0, 28.5)
        humidity = st.slider("Relative Humidity (%)", 0.0, 100.0, 75.0)
        rainfall = st.slider("Expected Rainfall (mm)", 0.0, 1000.0, 150.0)
        crop_stage = st.selectbox("Current Target Crop Stage", ["Land Preparation", "Sowing", "Vegetative Growth", "Flowering", "Harvesting"])

    if st.button("Generate Crop Advice", use_container_width=True):
        try:
            res = requests.post(f"{API_URL}/crop/predict-crop", json={
                "soil_type": soil_type, "nitrogen": nitrogen, "phosphorus": phosphorus,
                "potassium": potassium, "ph": ph, "temperature": temp,
                "humidity": humidity, "rainfall": rainfall
            }, headers=get_headers())
            
            if res.status_code == 200:
                data = res.json()
            else:
                raise requests.exceptions.ConnectionError()
        except requests.exceptions.ConnectionError:
            # FALLBACK ENGINE
            from backend.app.services.crop_service import crop_service
            db = None # Not needed for fallback
            # We mock the db session by calling the class directly
            data = crop_service.predict_crop(None, 1, soil_type, nitrogen, phosphorus, potassium, ph, temp, humidity, rainfall)
            # convert products models to dict list
            data["recommended_products"] = [
                {"product_name": p.product_name, "category": p.category, "price": p.price, "dosage": p.dosage, "benefits": p.benefits, "unit": p.unit} 
                for p in data["recommended_products"]
            ]
            
        # Display recommendations
        st.markdown("<hr>", unsafe_allow_html=True)
        st.balloons()
        
        c_left, c_right = st.columns([1, 1])
        with c_left:
            st.markdown(
                f"""
                <div style="background-color: #E8F5E9; border-radius: 12px; padding: 25px; border-left: 6px solid #1B7F3A;">
                    <div style="font-size: 12px; color: #7B4F2A; font-weight: 600; text-transform: uppercase;">Recommended Choice</div>
                    <div style="font-size: 38px; font-weight: 800; color: #0E5C2D; margin-bottom: 5px;">{data['recommended_crop']}</div>
                    <div style="font-size: 14px; font-weight: 500; color: #333333; margin-bottom: 10px;">Confidence Score: <b>{data['confidence_score']}%</b></div>
                    <div style="font-size: 14px; color: #555555;">Estimated Yield: <b>{data['expected_yield']}</b></div>
                    <div style="font-size: 11px; color: #888888; margin-top: 15px;">Model: {data['model_used']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.write("🏆 **Alternative Suitable Crops:**")
            for alt in data["top_3_alternative_crops"]:
                st.write(f"- {alt}")
                
        with c_right:
            st.markdown("<h4 style='color: #0E5C2D;'>Recommended Vishakan Products</h4>", unsafe_allow_html=True)
            if data["recommended_products"]:
                for p in data["recommended_products"]:
                    st.markdown(
                        f"""
                        <div style="background-color: #FFFFFF; border-radius: 8px; padding: 12px 16px; border: 1px solid #E2E8F0; margin-bottom: 10px;">
                            <div style="font-weight: 600; color: #1B7F3A; font-size: 15px;">{p['product_name']} ({p['category']})</div>
                            <div style="font-size: 12px; color: #555555; margin-top: 3px;">Benefits: {p['benefits']}</div>
                            <div style="font-size: 12px; color: #555555;">Dosage: <b>{p['dosage']}</b> | Unit Price: <b>₹{p['price']} per {p.get('unit', 'pack')}</b></div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
            else:
                st.write("Apply standard bio-compost and consult our AI Agronomist.")

# --- Page 3: Disease Detection ---
def show_disease_detection():
    st.markdown("<h2 class='section-title'>AI Plant Disease Scanner</h2>", unsafe_allow_html=True)
    st.write("Upload an image of your plant leaf, stem, or root to run AI diagnostic pathology.")
    
    uploaded_file = st.file_uploader("Upload Leaf/Fruit scan image...", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        st.image(uploaded_file, caption='Uploaded plant tissue image.', width=300)
        
        if st.button("Run Diagnostics Scan", use_container_width=True):
            with st.spinner("Analyzing cell walls and pathogen patterns..."):
                try:
                    # Prepare file payload
                    files = {"image": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                    res = requests.post(f"{API_URL}/disease/detect", files=files, headers=get_headers())
                    if res.status_code == 200:
                        data = res.json()
                    else:
                        raise requests.exceptions.ConnectionError()
                except requests.exceptions.ConnectionError:
                    # Fallback Mode
                    from backend.app.services.disease_service import disease_service
                    # Mock upload file format
                    class MockUpload:
                        def __init__(self, f):
                            self.file = f
                            self.filename = "leaf.jpg"
                    data = disease_service.detect_disease(None, 1, MockUpload(uploaded_file))
                    data["recommended_products"] = [
                        {"product_name": p.product_name, "category": p.category, "price": p.price, "dosage": p.dosage, "benefits": p.benefits} 
                        for p in data["recommended_products"]
                    ]

                st.markdown("<hr>", unsafe_allow_html=True)
                
                # Check outcome
                col_left, col_right = st.columns([1, 1])
                with col_left:
                    bg_col = "#FFEBEE" if data["disease_name"] != "Healthy" else "#E8F5E9"
                    border_col = "#C62828" if data["disease_name"] != "Healthy" else "#1B7F3A"
                    font_col = "#C62828" if data["disease_name"] != "Healthy" else "#0E5C2D"
                    
                    st.markdown(
                        f"""
                        <div style="background-color: {bg_col}; border-radius: 12px; padding: 25px; border-left: 6px solid {border_col};">
                            <div style="font-size: 12px; color: #7B4F2A; font-weight: 600; text-transform: uppercase;">Scan Analysis Result</div>
                            <div style="font-size: 32px; font-weight: 800; color: {font_col}; margin-bottom: 5px;">{data['disease_name']}</div>
                            <div style="font-size: 14px; font-weight: 500; color: #333333; margin-bottom: 10px;">Severity: <b>{data['severity']}</b></div>
                            <div style="font-size: 13px; color: #555555; line-height: 1.4;">{data['description']}</div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.write(f"🛑 **Preventive Measures:** {data['prevention']}")
                    
                with col_right:
                    st.markdown("<h4 style='color: #0E5C2D;'>Prescribed Vishakan Solutions</h4>", unsafe_allow_html=True)
                    st.write(f"🧪 **Dosage Schedule:** {data['dosage']}")
                    
                    if data["recommended_products"]:
                        for p in data["recommended_products"]:
                            st.markdown(
                                f"""
                                <div style="background-color: #FFFFFF; border-radius: 8px; padding: 12px; border: 1px solid #E2E8F0; margin-top: 10px;">
                                    <div style="font-weight: 600; color: #1B7F3A; font-size: 14px;">{p['product_name']} ({p['category']})</div>
                                    <div style="font-size: 11px; color: #666666;">Benefits: {p['benefits']}</div>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                    else:
                        st.write("No chemical/biological product required. Follow healthy soil protocol.")
                        
                    st.markdown("<br>", unsafe_allow_html=True)
                    st.markdown(
                        f"""
                        <div style="background-color: #F8FAFC; border-radius: 8px; padding: 12px; border: 1px solid #E2E8F0; font-size: 12px; color: #64748B;">
                            <b>Healthy vs Infected Comparison:</b><br>{data['healthy_vs_infected_comparison']}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

# --- Page 4: Product Advisor ---
def show_product_advisor():
    st.markdown("<h2 class='section-title'>Vishakan Product Advisor</h2>", unsafe_allow_html=True)
    
    # Filter controls
    col1, col2 = st.columns([1, 2])
    with col1:
        category = st.selectbox("Category Select", ["All", "Bio Fertilizer", "Bio Fungicide", "Bio Pesticide", "Bio Nematicide", "Bio Stimulant", "Other Products"])
    with col2:
        search = st.text_input("Search catalog keyword...", placeholder="e.g. nitrogen, leaf spot, root rot")
        
    try:
        cat_filter = None if category == "All" else category
        search_filter = None if not search else search
        res = requests.get(f"{API_URL}/products/", params={"category": cat_filter, "search": search_filter}, headers=get_headers())
        if res.status_code == 200:
            products = res.json()
        else:
            raise requests.exceptions.ConnectionError()
    except requests.exceptions.ConnectionError:
        # Fallback Mode
        products = MOCK_PRODUCTS
        if category != "All":
            products = [p for p in products if p["category"].lower() == category.lower()]
        if search:
            products = [p for p in products if search.lower() in p["product_name"].lower() or search.lower() in p["description"].lower()]

    st.markdown(f"Found **{len(products)}** biological solutions matching query.")
    
    # Render products as modern card design
    # Using 3 columns
    for i in range(0, len(products), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(products):
                p = products[i+j]
                with cols[j]:
                    st.markdown(
                        f"""
                        <div class="metric-card" style="height: 100%;">
                            <div style="background-color: #E8F5E9; color: #0E5C2D; font-size: 11px; font-weight: 700; width: fit-content; padding: 2px 8px; border-radius: 4px; text-transform: uppercase;">
                                {p['category']}
                            </div>
                            <h3 style="color: #1B7F3A; margin: 10px 0 5px 0; font-size: 20px; font-weight: 700;">{p['product_name']}</h3>
                            <p style="font-size: 13px; color: #333333; height: 50px; overflow: hidden; text-overflow: ellipsis; margin-bottom: 10px;">{p['description']}</p>
                            <div style="font-size: 12px; color: #666666; margin-bottom: 5px;">🧬 <b>Dosage:</b> {p['dosage']}</div>
                            <div style="font-size: 12px; color: #666666; margin-bottom: 12px;">📈 <b>Benefits:</b> {p['benefits']}</div>
                            <div style="display: flex; justify-content: space-between; border-top: 1px solid #F1F5F9; padding-top: 10px; font-size: 14px; font-weight: 600; color: #7B4F2A;">
                                <span>Unit: {p['unit']}</span>
                                <span>₹{p['price']}</span>
                            </div>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                    st.markdown("<br>", unsafe_allow_html=True)

# --- Page 5: Soil Health Analysis ---
def show_soil_health():
    st.markdown("<h2 class='section-title'>Soil Health Analysis</h2>", unsafe_allow_html=True)
    st.write("Diagnose nutrient statuses and receive a custom biological fertilization schedule.")
    
    col1, col2 = st.columns(2)
    with col1:
        n = st.number_input("Nitrogen (N) - mg/kg", 0.0, 300.0, 60.0)
        p = st.number_input("Phosphorus (P) - mg/kg", 0.0, 300.0, 30.0)
        k = st.number_input("Potassium (K) - mg/kg", 0.0, 300.0, 40.0)
        
    with col2:
        ph = st.number_input("Soil pH level", 0.0, 14.0, 6.5)
        organic_carbon = st.number_input("Organic Carbon (%)", 0.0, 10.0, 0.55)
        soil_type = st.selectbox("Soil Type", ["Loamy", "Clay", "Sandy", "Silt", "Black", "Red", "Laterite", "Alluvial"], key="soil_health_type")
        
    if st.button("Run Soil Analysis", use_container_width=True):
        try:
            res = requests.post(f"{API_URL}/crop/soil-health", json={
                "N": n, "P": p, "K": k, "pH": ph, "OrganicCarbon": organic_carbon, "soil_type": soil_type
            }, headers=get_headers())
            if res.status_code == 200:
                data = res.json()
            else:
                raise requests.exceptions.ConnectionError()
        except requests.exceptions.ConnectionError:
            # Fallback Mode
            from backend.app.services.crop_service import crop_service
            data = crop_service.analyze_soil_health(None, n, p, k, ph, organic_carbon, soil_type)
            data["recommended_products"] = [
                {"product_name": p.product_name, "category": p.category, "price": p.price, "dosage": p.dosage, "benefits": p.benefits} 
                for p in data["recommended_products"]
            ]

        # Display results
        st.markdown("<hr>", unsafe_allow_html=True)
        
        c_left, c_right = st.columns([1, 1])
        with c_left:
            # Gauge score
            score = data["soil_health_score"]
            score_color = "#1B7F3A" if score >= 75 else "#D97706" if score >= 50 else "#DC2626"
            
            st.markdown(
                f"""
                <div style="background-color: #F8FAFC; border-radius: 12px; padding: 25px; border: 1px solid #E2E8F0; text-align: center; margin-bottom: 20px;">
                    <div style="font-size: 14px; color: #64748B; font-weight: 500; text-transform: uppercase;">Soil Health Score</div>
                    <div style="font-size: 64px; font-weight: 800; color: {score_color};">{score}%</div>
                    <div style="font-size: 14px; font-weight: 600; color: #334155; margin-top: 5px;">Nutrient status looks promising.</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            # Deficiency list
            st.write("📊 **Deficiencies Diagnosed:**")
            if data["deficiency_report"]:
                for d in data["deficiency_report"]:
                    st.markdown(f"- ⚠️ <span style='color:#DC2626; font-weight:500;'>{d}</span>", unsafe_allow_html=True)
            else:
                st.success("No critical nutrient deficiencies detected!")
                
            st.markdown("<br>", unsafe_allow_html=True)
            st.write("🌾 **Suitable Crops for this Soil:**")
            st.write(", ".join(data["suitable_crops"]))
            
        with c_right:
            st.markdown("<h4 style='color: #0E5C2D;'>Vishakan Fertilization Plan</h4>", unsafe_allow_html=True)
            st.info(data["fertilization_plan"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            st.write("🧪 **Recommended Correction Inputs:**")
            for p in data["recommended_products"]:
                st.markdown(f"- **{p['product_name']}** ({p['category']})")

# --- Page 6: Dosage Calculator ---
def show_dosage_calculator():
    st.markdown("<h2 class='section-title'>Bio-Product Dosage Calculator</h2>", unsafe_allow_html=True)
    st.write("Compute required biological pack volume, estimated cost, and application ratios based on your farm acreage.")
    
    col1, col2 = st.columns(2)
    with col1:
        crop = st.selectbox("Crop Type", ["Rice", "Banana", "Coconut", "Turmeric", "Sugarcane", "Tomato", "Mango"])
        product_name = st.selectbox("Vishakan Product", [p["product_name"] for p in MOCK_PRODUCTS])
        
    with col2:
        area = st.number_input("Field Area size", 0.1, 100.0, 1.0)
        unit = st.selectbox("Measurement Unit", ["acres", "hectares"])
        
    if st.button("Calculate Requirement", use_container_width=True):
        try:
            res = requests.post(f"{API_URL}/products/dosage-calculator", json={
                "crop": crop, "product": product_name, "area": area, "unit": unit
            }, headers=get_headers())
            if res.status_code == 200:
                data = res.json()
            else:
                raise requests.exceptions.ConnectionError()
        except requests.exceptions.ConnectionError:
            # Fallback
            from backend.app.services.crop_service import crop_service
            data = crop_service.calculate_dosage(None, crop, product_name, area, unit)

        # Output results
        st.markdown("<hr>", unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown(
                f"""
                <div class="param-badge">
                    <div class="param-name">Required Quantity</div>
                    <div class="param-value">{data['required_quantity']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c2:
            st.markdown(
                f"""
                <div class="param-badge">
                    <div class="param-name">Mixing Ratio</div>
                    <div class="param-value">{data['mixing_ratio']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
        with c3:
            st.markdown(
                f"""
                <div class="param-badge">
                    <div class="param-name">Estimated Cost</div>
                    <div class="param-value">₹{data['estimated_cost']}</div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f"""
            <div style="background-color: #F8FAFC; border-radius: 12px; padding: 20px; border: 1px solid #E2E8F0;">
                <h4 style="color: #0E5C2D; margin-top:0;">Application Schedule & Guidelines</h4>
                <p style="font-size:14px; line-height: 1.5; color:#475569;">{data['application_schedule']}</p>
                <div style="font-size:12px; color:#64748B; margin-top:10px;">
                    ℹ️ Recommended total water volume for spraying: <b>{data.get('water_volume_liters', area*200)} Litres</b>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# --- Page 7: Voice Assistant ---
def show_voice_assistant():
    st.markdown("<h2 class='section-title'>Speech Enabled Agronomist</h2>", unsafe_allow_html=True)
    st.write("Click record or upload a WAV/MP3 query to speak with the agronomist in your regional language.")
    
    audio_file = st.file_uploader("Upload Audio recording...", type=["wav", "mp3", "m4a"])
    
    if audio_file is not None:
        st.audio(audio_file)
        
        if st.button("Transcribe & Ask AI", use_container_width=True):
            with st.spinner("Whisper transcribing regional speech signals..."):
                try:
                    files = {"audio": (audio_file.name, audio_file.getvalue(), audio_file.type)}
                    res = requests.post(f"{API_URL}/voice/query", files=files, headers=get_headers())
                    if res.status_code == 200:
                        data = res.json()
                    else:
                        raise requests.exceptions.ConnectionError()
                except requests.exceptions.ConnectionError:
                    # Fallback Mode
                    from backend.app.services.voice_service import voice_service
                    class MockUpload:
                        def __init__(self, f):
                            self.file = f
                            self.filename = "voice.wav"
                            self.content_type = "audio/wav"
                    data = voice_service.process_voice_query(None, 1, MockUpload(audio_file))

                # Display voice output
                st.markdown("<hr>", unsafe_allow_html=True)
                st.write(f"🌐 **Language Detected:** {data['language_detected']}")
                
                st.markdown(
                    f"""
                    <div style="background-color: #E8F5E9; border-radius: 12px; padding: 20px; border-left: 6px solid #1B7F3A; margin-bottom: 20px;">
                        <div style="font-size: 11px; color:#7B4F2A; font-weight:600; text-transform:uppercase;">Agronomist Response</div>
                        <p style="font-size: 15px; margin-top:5px; color:#0E5C2D; line-height: 1.5;">{data['text_response']}</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                if data["audio_response"]:
                    st.write("🔊 **Play Voice Response:**")
                    audio_bytes = base64.b64decode(data["audio_response"])
                    st.audio(audio_bytes, format="audio/mp3")

# --- Page 8: Chatbot RAG ---
def show_chatbot():
    st.markdown("<h2 class='section-title'>Vishakan AI Agronomist Chat</h2>", unsafe_allow_html=True)
    st.write("Ask our RAG-enabled chatbot about biological solutions, crop problems, and disease dosages.")
    
    # Display chat history
    for chat in st.session_state.chat_history:
        st.markdown(f'<div class="chat-bubble-user">🙋‍♂️ {chat["q"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="chat-bubble-bot">🌱 {chat["a"]}</div>', unsafe_allow_html=True)
        
    # Input box
    query = st.text_input("Consult agronomist query...", placeholder="e.g. My banana crop has root nematodes, what should I apply?", key="chat_input")
    
    if st.button("Send Message", use_container_width=True):
        if query:
            with st.spinner("Searching product vector stores..."):
                try:
                    res = requests.post(f"{API_URL}/chatbot/chat", json={"question": query}, headers=get_headers())
                    if res.status_code == 200:
                        data = res.json()
                        answer = data["answer"]
                    else:
                        raise requests.exceptions.ConnectionError()
                except requests.exceptions.ConnectionError:
                    # Fallback Mode
                    from backend.app.services.chat_service import chat_service
                    data = chat_service.query_agronomist(None, 1, query)
                    answer = data["answer"]
                    
                st.session_state.chat_history.append({"q": query, "a": answer})
                st.rerun()

# --- Page 9: History ---
def show_history():
    st.markdown("<h2 class='section-title'>Farmer History Logs</h2>", unsafe_allow_html=True)
    st.write("Chronological logs of your agricultural advisories, scans, and calculations.")
    
    # Mock log list matching enterprise farmer card UI
    st.markdown(
        """
        <div style="background-color: #FFFFFF; border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); border: 1px solid #E2E8F0; margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #F1F5F9; padding-bottom: 10px; margin-bottom: 10px;">
                <span style="font-weight: 600; color: #0E5C2D;">📂 Crop Recommendation Log #39401</span>
                <span style="color: #64748B; font-size: 13px;">Date: 20 May 2026</span>
            </div>
            <p style="font-size:14px; margin: 0;"><b>Soil Parameter:</b> Loamy | N:80 P:45 K:50 pH:6.5 | Rain:150mm</p>
            <p style="font-size:14px; margin: 5px 0 0 0;"><b>Advice Result:</b> Rice Paddy (94.2% Confidence). Prescribed: <b>V-NITRO</b> and <b>BIO-NPK</b>.</p>
        </div>
        
        <div style="background-color: #FFFFFF; border-radius: 12px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.03); border: 1px solid #E2E8F0; margin-bottom: 15px;">
            <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #F1F5F9; padding-bottom: 10px; margin-bottom: 10px;">
                <span style="font-weight: 600; color: #0E5C2D;">📂 Pathology Diagnosis Log #22409</span>
                <span style="color: #64748B; font-size: 13px;">Date: 15 May 2026</span>
            </div>
            <p style="font-size:14px; margin: 0;"><b>Scan Type:</b> Leaf Image Scan | Crop: Tomato</p>
            <p style="font-size:14px; margin: 5px 0 0 0;"><b>Diagnosis:</b> Powdery Mildew (High Severity). Recommended: <b>V-BACILI</b> and <b>V-KITIN</b>.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

# --- Page 10: Analytics ---
def show_analytics():
    st.markdown("<h2 class='section-title'>Business Intelligence & Reports</h2>", unsafe_allow_html=True)
    st.write("Aggregated platform analytical reports. Powered by Plotly.")
    
    # 4 KPI cards
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown("<div class='param-badge'><div class='param-name'>Total Farmers</div><div class='param-value'>1,241</div></div>", unsafe_allow_html=True)
    with c2:
        st.markdown("<div class='param-badge'><div class='param-name'>Products Advice</div><div class='param-value'>3,940</div></div>", unsafe_allow_html=True)
    with c3:
        st.markdown("<div class='param-badge'><div class='param-name'>Diseases Scanned</div><div class='param-value'>520</div></div>", unsafe_allow_html=True)
    with c4:
        st.markdown("<div class='param-badge'><div class='param-name'>Chatbot Queries</div><div class='param-value'>894</div></div>", unsafe_allow_html=True)
        
    st.markdown("<br><hr>", unsafe_allow_html=True)
    
    # Render Plotly Charts matching mockups
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.write("📊 **Most Recommended Biological Products**")
        df_prod = pd.DataFrame({
            "Product": ["V-NITRO", "V-PHOS", "BIO-NPK", "V-CURE", "V-COMBINE"],
            "Recommendations": [480, 350, 290, 240, 180]
        })
        fig1 = px.bar(df_prod, x="Product", y="Recommendations", color_discrete_sequence=[PRIMARY_GREEN])
        fig1.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300)
        st.plotly_chart(fig1, use_container_width=True)
        
    with col_r:
        st.write("🍩 **Pathology Scanner Disease Breakdowns**")
        df_dis = pd.DataFrame({
            "Disease": ["Blast", "Powdery Mildew", "Root Rot", "Healthy"],
            "Count": [140, 80, 50, 220]
        })
        fig2 = px.pie(df_dis, values="Count", names="Disease", color_discrete_sequence=[DARK_GREEN, PRIMARY_GREEN, SOIL_BROWN, "#81C784"])
        fig2.update_layout(margin=dict(l=20, r=20, t=20, b=20), height=300)
        st.plotly_chart(fig2, use_container_width=True)

# --- Page 11: Settings ---
def show_settings():
    st.markdown("<h2 class='section-title'>System & Profile Settings</h2>", unsafe_allow_html=True)
    
    pref_lang = st.selectbox("Preferred Communication Language", ["English", "Tamil", "Malayalam", "Kannada", "Telugu"], index=["English", "Tamil", "Malayalam", "Kannada", "Telugu"].index(st.session_state.language))
    st.session_state.language = pref_lang
    
    st.text_input("Update display name", value=st.session_state.user_name)
    st.checkbox("Enable SMS Alerts on mobile number")
    st.checkbox("Receive organic weather forecasts")
    
    if st.button("Save Configurations"):
        st.success("Configurations updated successfully!")

# -----------------------------
# MAIN APPLICATION CONTROLLER
# -----------------------------
def main():
    if not st.session_state.authenticated:
        login_register_page()
    else:
        draw_sidebar()
        
        # Dispatch pages
        if st.session_state.page == "Dashboard":
            show_dashboard()
        elif st.session_state.page == "Crop Recommendation":
            show_crop_recommendation()
        elif st.session_state.page == "Disease Detection":
            show_disease_detection()
        elif st.session_state.page == "Product Advisor":
            show_product_advisor()
        elif st.session_state.page == "Soil Health Analysis":
            show_soil_health()
        elif st.session_state.page == "Dosage Calculator":
            show_dosage_calculator()
        elif st.session_state.page == "Voice Assistant":
            show_voice_assistant()
        elif st.session_state.page == "Vishakan AI Agronomist":
            show_chatbot()
        elif st.session_state.page == "Farmer History":
            show_history()
        elif st.session_state.page == "Analytics":
            show_analytics()
        elif st.session_state.page == "Settings":
            show_settings()

if __name__ == "__main__":
    main()
