import streamlit as st
import pandas as pd
import numpy as np
import joblib
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
import datetime

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="Predictive Healthcare for Police Personnel",
    page_icon="—Pngtree—gold police officer badge_7258551.png",
    layout="wide"
)

# =========================================================
# SIMPLE LIGHT DESIGN
# =========================================================
st.markdown("""
<style>
body {
    background-color: #f8f9fa;
    color: #212529;
    font-family: "Segoe UI", sans-serif;
}
h1, h2, h3, h4 {
    color: #0a2647;
}
.stButton > button {
    background-color: #0a2647;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 0.6em 1.5em;
    font-weight: 600;
}
.stButton > button:hover {
    background-color: #144272;
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# HEADER
# =========================================================
col_logo, col_title = st.columns([1, 4])
with col_logo:
    st.image("—Pngtree—gold police officer badge_7258551.png", width=100)
with col_title:
    st.title("Predictive Healthcare for Police Personnel")
    st.caption("Personalized Risk Assessment and Preventive Suggestions")

# =========================================================
# LOAD MODEL & DATA
# =========================================================
df = pd.read_csv("police_health_dataset.csv")
ct_encoder = joblib.load("ct_encoder.pkl")
xgb_model = joblib.load("xgb_model.pkl")

# =========================================================
# DEMOGRAPHICS
# =========================================================
st.header("👤 Demographic Information")
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
    city_data = df[df['posted_city'] == posted_city]
    if not city_data.empty:
        pollution_index = float(city_data['pollution_index'].iloc[0])
        city_workload_index = float(city_data['city_workload_index'].iloc[0])
    else:
        pollution_index = 0
        city_workload_index = 0
    height_cm = st.number_input("Height (cm)", min_value=120, max_value=250)
    weight_kg = st.number_input("Weight (kg)", min_value=30, max_value=200)
bmi = round(weight_kg / ((height_cm / 100) ** 2), 1)
st.text_input("BMI", value=bmi, disabled=True)

# =========================================================
# VITAL SIGNS (QUALITATIVE)
# =========================================================
st.header("❤️ Vital Signs")
def get_vital_value(level, low, normal, high):
    return low if level == "Low" else normal if level == "Normal" else high

col1, col2, col3 = st.columns(3)
with col1:
    bp_level = st.selectbox("Blood Pressure Level", ["Low", "Normal", "High"])
    systolic_bp = get_vital_value(bp_level, 95, 120, 150)
    diastolic_bp = get_vital_value(bp_level, 65, 80, 100)
with col2:
    heart_level = st.selectbox("Heart Rate", ["Low", "Normal", "High"])
    heart_rate = get_vital_value(heart_level, 55, 80, 110)
with col3:
    sugar_level = st.selectbox("Fasting Blood Sugar", ["Low", "Normal", "High"])
    fasting_blood_sugar = get_vital_value(sugar_level, 70, 100, 125)

col1, col2 = st.columns(2)
with col1:
    cholesterol_level = st.selectbox("Cholesterol", ["Low", "Normal", "High"])
    cholesterol = get_vital_value(cholesterol_level, 150, 200, 270)
with col2:
    spo2_level = st.selectbox("Oxygen Level", ["Low", "Normal"])
    spo2 = get_vital_value(spo2_level, 92, 98, 98)

chronic_disease = st.selectbox("Chronic Disease", df['chronic_disease'].unique())
if chronic_disease == "Other":
    chronic_disease_other = st.text_input("Specify if Other")
else:
    chronic_disease_other = chronic_disease

# =========================================================
# LIFESTYLE
# =========================================================
st.header("🏋️ Physical Health & Lifestyle")

do_exercise = st.radio("Do you exercise?", ["Yes", "No"])
if do_exercise == "Yes":
    exercise_mins_per_week = st.number_input("Exercise Minutes per Week", min_value=10, max_value=1000)
else:
    exercise_mins_per_week = 0

sleep_hours = st.number_input("Sleep Hours per Day", min_value=1, max_value=24)
smoking = st.selectbox("Do you Smoke?", ["No", "Occasionally", "Regularly"])
alcohol = st.selectbox("Do you Consume Alcohol?", ["No", "Occasionally", "Regularly"])
wellness_program = st.radio("Wellness Program Provided?", ["Yes", "No", "Sometimes"])
water_intake_liters = st.number_input("Daily Water Intake (Liters)", min_value=0.0, max_value=10.0, step=0.1)

# =========================================================
# NEW DIET SECTION
# =========================================================
st.header("🍱 Diet and Cholesterol Impact")

has_lunch = st.radio("Do you have lunch every day?", ["Yes", "No"])
cholesterol_score = 0
diet_category = "Normal"
food_selected = None

if has_lunch == "Yes":
    food_type = st.radio("Type of Food", ["Veg", "Non-Veg"])
    if food_type == "Veg":
        food_selected = st.multiselect("Select the food items you eat regularly", 
            ["Pohe", "Vada Pav", "Chapati Bhaji", "Chaha"])
        cholesterol_score = len(food_selected) * 5
    else:
        food_selected = st.multiselect("Select the non-veg food items you eat regularly", 
            ["Egg", "Egg Roll", "Fish", "Chicken", "Mutton"])
        cholesterol_score = len(food_selected) * 10

    if cholesterol_score <= 10:
        diet_category = "Low"
    elif cholesterol_score <= 25:
        diet_category = "Normal"
    else:
        diet_category = "High"
else:
    diet_category = "Low"

st.info(f"Based on your eating habits, your cholesterol impact level is **{diet_category}**.")

# =========================================================
# OCCUPATIONAL & MENTAL HEALTH
# =========================================================
st.header("💼 Occupational Health & 🧠 Mental Wellbeing")

col1, col2 = st.columns(2)
with col1:
    shift_pattern = st.selectbox("Shift Pattern", ["Day", "Night", "Rotational"])
with col2:
    working_hours_per_week = st.number_input("Working Hours per Week", min_value=1, max_value=120)

stress_level = 5
if sleep_hours < 6: stress_level += 2
if working_hours_per_week > 50: stress_level += 2
if exercise_mins_per_week < 60: stress_level += 1
if shift_pattern in ["Night", "Rotational"]: stress_level += 1
stress_level = int(np.clip(stress_level, 1, 10))

st.progress(stress_level / 10, text=f"Stress Level: {stress_level}/10")

# =========================================================
# PREDICTION
# =========================================================
st.header("🩺 Risk Prediction")
if st.button("Predict My Risk & Download Report"):
    input_data = pd.DataFrame({
        'personnel_id':[personnel_id],
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
        'chronic_disease':[chronic_disease_other],
        'sleep_hours':[sleep_hours],
        'exercise_mins_per_week':[exercise_mins_per_week],
        'smoking':[smoking],
        'alcohol':[alcohol],
        'stress_level':[stress_level],
        'shift_pattern':[shift_pattern],
        'working_hours_per_week':[working_hours_per_week],
        'healthcare_scheme':[df['healthcare_scheme'].iloc[0]],
        'technological_support':["Low"],
        'predictive_system_usage':["Yes"]
    })

    for col in ['post','posted_city','gender','chronic_disease','smoking','alcohol',
                'shift_pattern','healthcare_scheme','technological_support','predictive_system_usage']:
        input_data[col] = input_data[col].astype(str)

    input_encoded = ct_encoder.transform(input_data)
    risk_score = float(xgb_model.predict(input_encoded)[0])
    if smoking == "Occasionally": risk_score += 5
    elif smoking == "Regularly": risk_score += 10
    if alcohol == "Occasionally": risk_score += 3
    elif alcohol == "Regularly": risk_score += 8

    risk_category = "✅ Normal" if risk_score < 40 else "⚠ Borderline" if risk_score < 70 else "❌ High Risk"
    st.success(f"Your Risk Category: {risk_category}")

    # Overall Summary
    categories = [bp_level, heart_level, sugar_level, cholesterol_level, diet_category]
    summary = {"High": categories.count("High"), "Normal": categories.count("Normal"), "Low": categories.count("Low")}
    st.info(f"Overall Health Summary → High: {summary['High']} | Normal: {summary['Normal']} | Low: {summary['Low']}")

    # =========================================================
    # PDF REPORT
    # =========================================================
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Predictive Healthcare Report", styles['Title']))
    elements.append(Spacer(1, 10))
    elements.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 20))

    data = [
        ["Blood Pressure", bp_level],
        ["Heart Rate", heart_level],
        ["Fasting Blood Sugar", sugar_level],
        ["Cholesterol", cholesterol_level],
        ["Diet Cholesterol Impact", diet_category],
        ["Exercise", "No Exercise" if exercise_mins_per_week == 0 else "Regular"],
        ["Stress Level", str(stress_level)],
        ["Overall Summary", f"High: {summary['High']} | Normal: {summary['Normal']} | Low: {summary['Low']}"]
    ]

    table = Table(data, colWidths=[200, 300])
    table.setStyle(TableStyle([
        ('GRID',(0,0),(-1,-1),0.5,colors.grey),
        ('FONTNAME',(0,0),(-1,-1),'Helvetica'),
        ('FONTSIZE',(0,0),(-1,-1),10),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"Risk Category: {risk_category}", styles['Heading2']))
    pdf.build(elements)
    buffer.seek(0)

    st.download_button(
        label="📥 Download Full PDF Report",
        data=buffer,
        file_name=f"police_health_report_{personnel_id}.pdf",
        mime="application/pdf"
    )

# =========================================================
# FOOTER
# =========================================================
st.markdown("---")
st.caption("© 2025 Police Health Analytics | Developed for Research and Awareness")
