import streamlit as st
import json
import os
import numpy as np
from fuzzywuzzy import process
import pandas as pd

# Set Page Config
st.set_page_config(
    page_title="Diet GPT | AI Nutritionist",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for "Premium" Look
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Outfit', sans-serif;
    }

    .main {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }

    /* Global text color for main content to prevent white-on-white */
    .main p, .main span, .main label, .main div, .main li {
        color: #2c3e50 !important;
    }

    .stButton>button {
        width: 100%;
        border-radius: 12px;
        height: 3em;
        background-color: #2e7d32;
        color: white;
        font-weight: 600;
        border: none;
        transition: 0.3s;
    }

    .stButton>button:hover {
        background-color: #1b5e20;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }

    .card {
        background: rgba(255, 255, 255, 0.8);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        margin-bottom: 2rem;
    }

    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
    }

    .section-title {
        color: #1b5e20;
        font-weight: 700;
        font-size: 1.5rem;
        margin-bottom: 1rem;
        border-bottom: 2px solid #e8f5e9;
        padding-bottom: 0.5rem;
    }

    .diet-item {
        padding: 10px;
        margin: 5px 0;
        border-left: 4px solid #4caf50;
        background: #f1f8e9;
        border-radius: 0 8px 8px 0;
        color: #1e3c72 !important; /* Dark blue for meal text */
    }

    .card {
        background: rgba(255, 255, 255, 0.9);
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 8px 32px 0 rgba(31, 38, 135, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.18);
        margin-bottom: 2rem;
        color: #2c3e50 !important; /* Darker text for card content */
    }

    .card p, .card div, .card span, .card b {
        color: #2c3e50 !important;
    }
    /* Sidebar Styling - Force high contrast white text over dark blue */
    [data-testid="stSidebar"] {
        background-color: #1e3c72 !important;
    }
    
    [data-testid="stSidebar"] [data-testid="stVerticalBlock"] > div {
        color: white !important;
    }

    [data-testid="stSidebar"] .stMarkdown, 
    [data-testid="stSidebar"] label, 
    [data-testid="stSidebar"] .stHeader,
    [data-testid="stSidebar"] p,
    [data-testid="stSidebar"] span,
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 {
        color: white !important;
    }

    /* Ensure inputs in sidebar are readable (typically they should be dark text on white input background) */
    [data-testid="stSidebar"] input {
        color: #1e3c72 !important;
    }

    h1, h2, h3 {
        color: #1e3c72;
    }
</style>
""", unsafe_allow_html=True)

# --- Helper Functions (From fullde.py) ---

@st.cache_data
def load_json_data(file_path):
    try:
        if not os.path.exists(file_path):
            return None
        with open(file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except Exception:
        return None

def get_best_match(user_input, choices):
    return process.extractOne(user_input, choices) if choices else (None, 0)

def find_disease(disease_input, diet_data):
    if not diet_data or "diseases" not in diet_data:
        return None
    disease_names = [d["name"].strip().lower() for d in diet_data["diseases"]]
    
    # Exact match first
    matched_disease = next((d for d in diet_data["diseases"] if d["name"].strip().lower() == disease_input), None)
    if matched_disease:
        return matched_disease
    
    # Fuzzy match
    best_match, score = process.extractOne(disease_input, disease_names)
    if best_match and score > 70:
        return next(d for d in diet_data["diseases"] if d["name"].strip().lower() == best_match)
    return None

def fuzzy_membership(age, center, spread=5):
    return np.exp(-0.5 * ((age - center) / spread) ** 2)

def get_fuzzy_age_group(age):
    age_groups = {"20-30": 25, "30-40": 35, "40-50": 45, "50-60": 55}
    membership_scores = {group: fuzzy_membership(age, center) for group, center in age_groups.items()}
    return max(membership_scores, key=membership_scores.get)

def compute_similarity(user_age, user_height, user_weight, user_has_disease, user_disease_type, entry):
    age_score = fuzzy_membership(user_age, entry["age"], spread=10)
    height_score = fuzzy_membership(user_height, entry["height"], spread=0.1)
    weight_score = fuzzy_membership(user_weight, entry["weight"], spread=10)
    
    disease_type_entry = entry.get("disease_type", "No Disease").lower()
    user_disease_type_lower = user_disease_type.lower()
    
    disease_score = 1 if (user_has_disease == entry["has_disease"] and 
                         (not user_has_disease or user_disease_type_lower == disease_type_entry)) else 0

    match_count = sum([age_score > 0.5, height_score > 0.5, weight_score > 0.5, disease_score == 1])
    if match_count >= 2:
        return (age_score + height_score + weight_score + disease_score) / 4
    return 0

def get_diet_recommendation(data, user_age, user_height, user_weight, user_has_disease, user_disease_type):
    best_match = None
    highest_score = 0
    for entry in data:
        score = compute_similarity(user_age, user_height, user_weight, user_has_disease, user_disease_type, entry)
        if score > highest_score:
            highest_score = score
            best_match = entry
    return best_match

def get_diet_from_4(age_group, disease, data):
    if not data: return "No data."
    recommendations = data.get("diet_recommendations", [])
    all_age_groups = [entry["age_group"] for entry in recommendations]
    all_conditions = [entry["disease_condition"] for entry in recommendations]
    
    best_age_group, age_score = get_best_match(age_group, all_age_groups)
    best_disease, disease_score = get_best_match(disease, all_conditions)
    
    if age_score >= 80 and disease_score >= 80:
        for entry in recommendations:
            if entry["age_group"] == best_age_group and entry["disease_condition"] == best_disease:
                return entry
    return "No matching recommendation found."

def get_diet_from_6(age, condition, data):
    if not data: return "No data."
    age_group = get_fuzzy_age_group(age)
    for entry in data:
        if entry["entities"]["age_group"] == age_group:
            if entry["entities"]["condition"].lower() == condition.lower():
                return {
                    "response": entry["response"],
                    "genetic_marker": entry["entities"]["genetic_marker"],
                    "microbiome_profile": entry["entities"]["microbiome_profile"]
                }
    return "No matching recommendation found."

# --- Main App ---

def main():
    st.title("🥗 Diet GPT")
    st.markdown("### Personalized AI-Powered Nutrition Assistant")
    
    # Sidebar for User Input
    with st.sidebar:
        st.header("📇 User Information")
        age = st.number_input("Age", min_value=1, max_value=120, value=25)
        age_group = st.selectbox("Age Group", ["Infants", "Children", "Adolescents", "Adults", "Elderly", "Pregnant Women"])
        
        col1, col2 = st.columns(2)
        with col1:
            h_ft = st.number_input("Height (ft)", min_value=1, max_value=8, value=5)
        with col2:
            h_in = st.number_input("Height (in)", min_value=0, max_value=11, value=7)
        
        weight = st.number_input("Weight (kg)", min_value=1.0, max_value=300.0, value=65.0)
        
        has_disease = st.radio("Do you have any medical condition?", ["No", "Yes"])
        disease_condition = "None"
        if has_disease == "Yes":
            disease_condition = st.text_input("Enter condition (e.g., Diabetes, Hypertension)", "Hypertension")
        
        submit_btn = st.button("Generate Diet Plan ✨")

    # Height Conversion
    height_cm = (h_ft * 30.48) + (h_in * 2.54)
    height_m = height_cm / 100

    if submit_btn:
        # Load Data
        with st.spinner("Analyzing data and generating your profile..."):
            d1 = load_json_data("1.json")
            d3 = load_json_data("3.json")
            d4 = load_json_data("4.json")
            d5 = load_json_data("5gpt.json") or []
            d6 = load_json_data("6web.json")

            # 1. Combined Disease Recommendations (1.json & 3.json)
            combined_rec = {}
            if has_disease == "Yes":
                match1 = find_disease(disease_condition.lower(), d1)
                match3 = find_disease(disease_condition.lower(), d3)
                if match1:
                    for n, g in match1["diet_guidelines"].items(): combined_rec[n] = g
                if match3:
                    for n, g in match3["diet_guidelines"].items():
                        combined_rec[n] = combined_rec.get(n, "") + ("; " if n in combined_rec else "") + g

            # 2. Disease-specific (4.json)
            diet4 = get_diet_from_4(age_group, disease_condition, d4)

            # 3. Personalized (6web.json)
            diet6 = get_diet_from_6(age, disease_condition, d6)

            # 4. Best Match (5gpt.json)
            best_plan = get_diet_recommendation(d5, age, height_m, weight, (has_disease=="Yes"), disease_condition)

        # Dashboard Layout
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            st.markdown(f"<div class='metric-card'><h4>Age</h4><h2>{age}</h2><p>{age_group}</p></div>", unsafe_allow_html=True)
        with col_m2:
            st.markdown(f"<div class='metric-card'><h4>Height</h4><h2>{height_cm:.1f} cm</h2><p>{h_ft}'{h_in}\"</p></div>", unsafe_allow_html=True)
        with col_m3:
            st.markdown(f"<div class='metric-card'><h4>Weight</h4><h2>{weight} kg</h2><p>BMI: {weight/(height_m**2):.1f}</p></div>", unsafe_allow_html=True)

        st.divider()

        # Results Display
        res_col1, res_col2 = st.columns([1, 1])

        with res_col1:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<p class='section-title'>🍽️ Recommended Daily Menu</p>", unsafe_allow_html=True)
            if best_plan:
                bp = best_plan['diet_plan']
                st.markdown(f"<div class='diet-item'><b>🌅 Breakfast:</b> {bp['breakfast']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='diet-item'><b>☀️ Lunch:</b> {bp['lunch']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='diet-item'><b>🌙 Dinner:</b> {bp['dinner']}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='diet-item'><b>🥤 Drink:</b> {bp['drink']}</div>", unsafe_allow_html=True)
            else:
                st.info("No specific menu found for your profile. Try adjusting your inputs.")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<p class='section-title'>🧬 Genetic & Microbiome Insights</p>", unsafe_allow_html=True)
            if isinstance(diet6, dict):
                st.write(f"**Marker:** {diet6['genetic_marker']}")
                st.write(f"**Profile:** {diet6['microbiome_profile']}")
                st.success(diet6['response'])
            else:
                st.write(diet6)
            st.markdown("</div>", unsafe_allow_html=True)

        with res_col2:
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<p class='section-title'>🏥 Medical Context</p>", unsafe_allow_html=True)
            if has_disease == "Yes":
                st.write(f"**Condition:** {disease_condition}")
                if combined_rec:
                    for n, g in combined_rec.items():
                        st.markdown(f"**{n}:** {g}")
                else:
                    st.warning("Specific guidelines not found in medical database.")
            else:
                st.write("No medical conditions reported. Focus on a balanced diet!")
            st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("<div class='card'>", unsafe_allow_html=True)
            st.markdown("<p class='section-title'>🍎 Nutrient Focus</p>", unsafe_allow_html=True)
            if isinstance(diet4, dict):
                st.markdown(f"**Focus:** {', '.join(diet4['nutrient_focus'])}")
                st.markdown(f"**Best Foods:** {', '.join(diet4['recommended_foods'])}")
                st.markdown(f"**Advice:** {diet4['advice']}")
            else:
                st.write(diet4)
            st.markdown("</div>", unsafe_allow_html=True)
            
    else:
        # Welcome State
        st.markdown("""
        <div style='text-align: center; padding: 50px;'>
            <h2 style='color: #2e7d32;'>Ready to transform your health?</h2>
            <p style='font-size: 1.2rem; color: #555;'>Fill in your details on the left to get a personalized AI-recommended diet plan.</p>
            <img src='https://cdn-icons-png.flaticon.com/512/3059/3059441.png' width='200'>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
