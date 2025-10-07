import streamlit as st

# App Title and Header
st.set_page_config(page_title="Predictive Healthcare for Police Personnel", layout="wide")

# Header Section
st.markdown(
    """
    <div style='text-align: center; padding: 10px; background-color: #1E3A8A; color: white; border-radius: 10px;'>
        <h1>Predictive Healthcare for Police Personnel</h1>
        <p>Get your personalized risk assessment and preventive suggestions</p>
        <img src="—Pngtree—gold police officer badge_7258551.png" 
             width="80" alt="Police Logo">
    </div>
    """,
    unsafe_allow_html=True
)

import pandas as pd

# Load dataset for dropdowns
df = pd.read_csv("police_health_dataset.csv")

st.subheader("👤 Demographics")

col1, col2, col3 = st.columns(3)

with col1:
    personnel_id = st.number_input("Personnel ID", min_value=1, step=1)
    age = st.number_input("Age (years)", min_value=18, max_value=100)
    gender = st.radio("Gender", ["Male", "Female", "Other"])

with col2:
    years_of_service = st.number_input("Years of Service", min_value=0, step=1)
    post = st.selectbox("Post", df['post'].unique())
    posted_city = st.selectbox("Posted City", df['posted_city'].unique())

with col3:
    # Automatically set pollution_index & city_workload_index based on posted city
    city_data = df[df['posted_city'] == posted_city].iloc[0]
    pollution_index = st.text_input("Pollution Index", value=city_data['pollution_index'], disabled=True)
    city_workload_index = st.text_input("City Workload Index", value=city_data['city_workload_index'], disabled=True)
    height_cm = st.number_input("Height (cm)", min_value=120, max_value=250)
    weight_kg = st.number_input("Weight (kg)", min_value=30, max_value=200)

# Auto-calculate BMI
bmi = round(weight_kg / ((height_cm/100)**2), 1)
st.text_input("BMI", value=bmi, disabled=True)


st.subheader("❤️ Vital Signs")

col1, col2, col3 = st.columns(3)

with col1:
    systolic_bp = st.number_input("Systolic BP (mmHg) [90-180]", min_value=90, max_value=180)
    diastolic_bp = st.number_input("Diastolic BP (mmHg) [60-120]", min_value=60, max_value=120)
    heart_rate = st.number_input("Heart Rate (bpm) [50-120]", min_value=50, max_value=120)

with col2:
    spo2 = st.number_input("SpO₂ (%) [90-100]", min_value=90, max_value=100)
    fasting_blood_sugar = st.number_input("Fasting Blood Sugar (mg/dL) [70-130]", min_value=70, max_value=130)
    cholesterol = st.number_input("Cholesterol (mg/dL) [100-300]", min_value=100, max_value=300)

with col3:
    chronic_disease = st.selectbox("Chronic Disease", df['chronic_disease'].unique())
    if chronic_disease == "Other":
        chronic_disease_other = st.text_input("Please specify your chronic disease")

st.subheader("🏃 Lifestyle / Habits")

col1, col2, col3 = st.columns(3)

with col1:
    exercise_mins_per_week = st.number_input("Exercise minutes per week (0 if none)", min_value=0, max_value=1000)
    sleep_hours = st.number_input("Sleep hours per day", min_value=1, max_value=24)
    diet_quality = st.selectbox("Diet Quality", df['diet_quality'].unique())

with col2:
    stress_level = st.slider("Stress Level (1-10)", min_value=1, max_value=10)
    smoking = st.radio("Smoking", ["Yes", "No"])
    alcohol = st.radio("Alcohol Consumption", ["Yes", "No"])

with col3:
    shift_pattern = st.selectbox("Shift Pattern", ["Day", "Night", "Rotational"])
    working_hours_per_week = st.number_input("Working hours per week", min_value=1, max_value=120)
    healthcare_scheme = st.selectbox("Healthcare Scheme", df['healthcare_scheme'].unique())
    if healthcare_scheme == "Other":
        healthcare_scheme_other = st.text_input("Specify Healthcare Scheme")

# Technology & predictive system usage
st.subheader("💻 Technology & System Usage")
col1, col2 = st.columns(2)
with col1:
    technological_support = st.radio("Technology Support Level", ["High", "Medium", "Low"])
with col2:
    predictive_system_usage = st.radio("Use of Predictive System?", ["Yes", "No"])
