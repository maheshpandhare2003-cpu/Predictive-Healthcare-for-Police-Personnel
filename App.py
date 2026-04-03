```python
# App.py (Final Updated Version with Website UI + Alphanumeric ID)

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import io
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# -----------------------------------------------------------
# PAGE CONFIG
# -----------------------------------------------------------

st.set_page_config(
    page_title="Predictive Healthcare for Police Personnel",
    page_icon="🚓",
    layout="wide"
)

# -----------------------------------------------------------
# WEBSITE STYLE
# -----------------------------------------------------------

st.markdown("""
<style>

body{
background-color:#f4f6f9;
font-family:Segoe UI;
}

.main-title{
font-size:40px;
font-weight:700;
color:white;
text-align:center;
}

.hero{
background:linear-gradient(90deg,#0a2647,#144272);
padding:30px;
border-radius:12px;
margin-bottom:20px;
}

.section-card{
background:white;
padding:25px;
border-radius:12px;
box-shadow:0 2px 10px rgba(0,0,0,0.08);
margin-bottom:20px;
}

.stButton>button{
background:#0a2647;
color:white;
border-radius:8px;
padding:0.6em 1.2em;
font-weight:600;
}

</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# HEADER
# -----------------------------------------------------------

st.markdown("""
<div class="hero">
<div class="main-title">
Predictive Healthcare System for Police Personnel
</div>
</div>
""", unsafe_allow_html=True)

# -----------------------------------------------------------
# POLICE IMAGE BANNER
# -----------------------------------------------------------

img1, img2, img3 = st.columns(3)

with img1:
    st.image("https://images.unsplash.com/photo-1581091870627-3c0f8a9d5a4e")

with img2:
    st.image("https://images.unsplash.com/photo-1598514982901-6a7f8c6c4e64")

with img3:
    st.image("https://images.unsplash.com/photo-1593113630400-ea4288922497")

# -----------------------------------------------------------
# LOAD DATA & MODEL FILES
# -----------------------------------------------------------

df = pd.read_csv("police_health_dataset.csv")
ct_encoder = joblib.load("ct_encoder.pkl")
xgb_model = joblib.load("xgb_model.pkl")

# -----------------------------------------------------------
# HELPER FUNCTIONS
# -----------------------------------------------------------

def get_numeric_from_level(level, low, normal, high):
    return low if level == "Low" else normal if level == "Normal" else high


def safe_transform(encoder, X, df_ref, categorical_cols):
    try:
        return encoder.transform(X)

    except Exception:

        X2 = X.copy()

        for col in categorical_cols:

            if col in X2.columns and col in df_ref.columns:

                known = list(df_ref[col].dropna().unique())

                X2[col] = X2[col].apply(
                    lambda v: v if v in known else known[0]
                )

            else:

                X2[col] = "Unknown"

        return encoder.transform(X2)


# -----------------------------------------------------------
# DEMOGRAPHICS
# -----------------------------------------------------------

st.markdown('<div class="section-card">', unsafe_allow_html=True)

st.header("👤 Demographics Information")

col1, col2, col3 = st.columns(3)

with col1:

    personnel_id = st.text_input(
        "Personnel ID (Example: MH1234 / POLICE01)"
    )

    age = st.number_input(
        "Age (years)",
        min_value=18,
        max_value=100
    )

    gender = st.radio(
        "Gender",
        ["Male", "Female", "Other"]
    )

with col2:

    years_of_service = st.number_input(
        "Years of Service",
        min_value=0
    )

    post = st.selectbox(
        "Post",
        df['post'].unique()
    )

    posted_city = st.selectbox(
        "Posted City",
        df['posted_city'].unique()
    )

with col3:

    city_row = df[df['posted_city'] == posted_city]

    if not city_row.empty:

        pollution_index = float(
            city_row['pollution_index'].iloc[0]
        )

        city_workload_index = float(
            city_row['city_workload_index'].iloc[0]
        )

    else:

        pollution_index = 0.0
        city_workload_index = 0.0

    st.metric(
        "City Pollution Index",
        f"{pollution_index:.2f}"
    )

    st.metric(
        "City Workload Index",
        f"{city_workload_index:.2f}"
    )

    height_cm = st.number_input(
        "Height (cm)",
        min_value=120,
        max_value=250
    )

    weight_kg = st.number_input(
        "Weight (kg)",
        min_value=30,
        max_value=200
    )

bmi = round(
    weight_kg / ((height_cm / 100) ** 2), 1
) if height_cm > 0 else 0

st.text_input(
    "BMI",
    value=bmi,
    disabled=True
)

st.markdown('</div>', unsafe_allow_html=True)

# -----------------------------------------------------------
# HEALTH SCHEMES
# -----------------------------------------------------------

st.header("🩺 Police Personnel Using Schemes / System")

health_conditions = st.multiselect(

    "Select schemes/systems or current conditions:",

    [
        "High BP",
        "Low BP",
        "Cholesterol",
        "Diabetes",
        "Thyroid",
        "Heart Disease",
        "Asthma",
        "MPKAY",
        "Family Health Scheme",
        "Dhanwantari",
        "MJPJAY",
        "Preventive Camps",
        "Digital Health Records",
        "Police Hospitals",
        "None"
    ]
)

current_health_details = (
    ", ".join(health_conditions)
    if health_conditions
    else "None"
)

# -----------------------------------------------------------
# VITAL SIGNS
# -----------------------------------------------------------

st.header("❤️ Vital Signs")

bp_level = st.selectbox(
    "BP Level",
    ["Low", "Medium", "High"]
)

systolic_bp = get_numeric_from_level(
    bp_level, 95, 120, 150
)

diastolic_bp = get_numeric_from_level(
    bp_level, 65, 80, 100
)

cholesterol_level = st.selectbox(
    "Cholesterol Level",
    ["Low", "Medium", "High"]
)

cholesterol = get_numeric_from_level(
    cholesterol_level,
    150,
    200,
    270
)

diabetes_level = st.selectbox(
    "Diabetes Level",
    ["Low", "Normal", "High"]
)

fasting_blood_sugar = get_numeric_from_level(
    diabetes_level,
    70,
    100,
    125
)

# -----------------------------------------------------------
# SPO2 ESTIMATION
# -----------------------------------------------------------

st.subheader("🫁 Oxygen Saturation (SpO₂) Estimation")

spo2_question = st.radio(

    "How do you currently feel?",

    [
        "Normal breathing, no fatigue",
        "Slight breathlessness or tiredness",
        "Severe breathlessness or using oxygen support"
    ]
)

spo2 = (

    98 if spo2_question
    == "Normal breathing, no fatigue"

    else 94 if spo2_question
    == "Slight breathlessness or tiredness"

    else 90
)

spo2_level = "Normal" if spo2 >= 95 else "Low"

st.info(
    f"Estimated SpO₂ Level: **{spo2_level} ({spo2}%)**"
)

heart_level = st.selectbox(
    "Heart Rate Level",
    ["Low", "Normal", "High"]
)

heart_rate = get_numeric_from_level(
    heart_level,
    55,
    80,
    110
)

# -----------------------------------------------------------
# PREDICTION
# -----------------------------------------------------------

st.markdown("---")

if st.button("Predict My Risk & Prepare Report"):

    personnel_numeric = int(

        ''.join(
            filter(str.isdigit, personnel_id)
        )

    ) if any(
        char.isdigit()
        for char in personnel_id
    ) else 0

    input_data = pd.DataFrame({

        'personnel_id':[personnel_numeric],
        'post':[post],
        'posted_city':[posted_city],
        'pollution_index':[pollution_index],
        'city_workload_index':[city_workload_index],
        'age':[age],
        'gender':[gender],
        'years_of_service':[years_of_service],
        'height_cm':[height_cm],
        'weight_kg':[weight_kg],
        'bmi':[bmi],
        'systolic_bp':[systolic_bp],
        'diastolic_bp':[diastolic_bp],
        'heart_rate':[heart_rate],
        'spo2':[spo2],
        'fasting_blood_sugar':[fasting_blood_sugar],
        'cholesterol':[cholesterol],
        'sleep_hours':[7],
        'exercise_mins_per_week':[0],
        'smoking':["No"],
        'alcohol':["No"],
        'stress_level':[5],
        'shift_pattern':["Day"],
        'working_hours_per_week':[40],
        'healthcare_scheme':["None"],
        'technological_support':["Low"],
        'predictive_system_usage':["Yes"]

    })

    categorical_cols = [

        'post',
        'posted_city',
        'gender',
        'smoking',
        'alcohol',
        'shift_pattern',
        'healthcare_scheme',
        'technological_support',
        'predictive_system_usage'
    ]

    input_encoded = safe_transform(
        ct_encoder,
        input_data,
        df,
        categorical_cols
    )

    risk_score = float(
        xgb_model.predict(input_encoded)[0]
    )

    st.subheader("📊 Risk Result")

    st.write(
        f"Risk Score: **{risk_score:.2f}**"
    )

st.markdown("---")

st.caption(
"© 2025 Police Health Analytics | Developed for Research"
)
```
