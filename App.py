import streamlit as st
import pandas as pd
import numpy as np
import joblib
import io
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# -----------------------
# PAGE CONFIG
# -----------------------
st.set_page_config(
    page_title="Predictive Healthcare for Police Personnel",
    page_icon="—Pngtree—gold police officer badge_7258551.png",
    layout="wide"
)

st.markdown("""
<style>
body { background-color: #f8f9fa; color: #212529; font-family: "Segoe UI", sans-serif; }
h1,h2,h3,h4 { color: #0a2647; }
.stButton > button { background-color:#0a2647; color:#fff; border-radius:8px; padding:0.6em 1.2em; font-weight:600;}
.stButton > button:hover { background-color:#144272; }
div.stDownloadButton > button { background-color:#0a2647; color:#fff; border-radius:8px; padding:0.5em 1em; }
</style>
""", unsafe_allow_html=True)

# -----------------------
# Header
# -----------------------
col_logo, col_title = st.columns([1, 4])
with col_logo:
    try:
        st.image("—Pngtree—gold police officer badge_7258551.png", width=90)
    except:
        pass
with col_title:
    st.title("Predictive Healthcare for Police Personnel")
    st.caption("Personalized Risk Assessment — with lifestyle-based vitals estimation")

# -----------------------
# Load dataset & model
# -----------------------
df = pd.read_csv("police_health_dataset.csv")
ct_encoder = joblib.load("ct_encoder.pkl")
xgb_model = joblib.load("xgb_model.pkl")

# -----------------------
# Helper functions
# -----------------------
def get_vital_value(level, low, normal, high):
    return low if level == "Low" else normal if level == "Normal" else high

def safe_transform(encoder, X, df_ref, categorical_cols):
    try:
        return encoder.transform(X)
    except Exception:
        X2 = X.copy()
        for col in categorical_cols:
            if col in X2.columns:
                known = list(df_ref[col].dropna().unique())
                if known:
                    X2[col] = X2[col].apply(lambda v: v if v in known else known[0])
        return encoder.transform(X2)

# -----------------------
# DEMOGRAPHICS
# -----------------------
st.header("👤 Demographics Information")
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
    city_df = df[df['posted_city'] == posted_city]
    if not city_df.empty:
        pollution_index = float(city_df['pollution_index'].iloc[0])
        city_workload_index = float(city_df['city_workload_index'].iloc[0])
    else:
        pollution_index = 0.0
        city_workload_index = 0.0
    height_cm = st.number_input("Height (cm)", min_value=120, max_value=250)
    weight_kg = st.number_input("Weight (kg)", min_value=30, max_value=200)

bmi = round(weight_kg / ((height_cm/100)**2), 1)
st.text_input("BMI", value=bmi, disabled=True)

# -----------------------
# ESTIMATED VITALS
# -----------------------
st.header("❤️ Vital Signs — Estimated Automatically")

# Blood Pressure
bp_level = st.selectbox("How would you describe your daily stress & salt intake?",
    ["Low stress, low salt", "Moderate stress & salt", "High stress, high salt"])
if bp_level == "Low stress, low salt":
    bp_status = "Low"
elif bp_level == "Moderate stress & salt":
    bp_status = "Normal"
else:
    bp_status = "High"
systolic_bp = get_vital_value(bp_status, 95, 120, 150)
diastolic_bp = get_vital_value(bp_status, 65, 80, 100)

# Heart Rate
activity = st.selectbox("How active are you physically?", ["Very active", "Moderately active", "Sedentary"])
if activity == "Very active":
    heart_status = "Low"
elif activity == "Moderately active":
    heart_status = "Normal"
else:
    heart_status = "High"
heart_rate = get_vital_value(heart_status, 60, 80, 110)

# Estimate Cholesterol
st.subheader("Estimate Cholesterol Level")
food_oil = st.selectbox("How often do you eat fried/oily food?", ["Rarely", "Sometimes", "Frequently"])
food_type = st.radio("Do you eat more of veg or non-veg?", ["Veg", "Non-Veg", "Mix"])
if food_oil == "Rarely" and food_type == "Veg":
    chol_status = "Low"
elif food_oil == "Sometimes" or food_type == "Mix":
    chol_status = "Normal"
else:
    chol_status = "High"
cholesterol = get_vital_value(chol_status, 150, 200, 270)

# Estimate Blood Sugar
st.subheader("Estimate Fasting Blood Sugar Level")
sweets = st.selectbox("How often do you eat sweets?", ["Rarely", "Sometimes", "Daily"])
sleep_hours = st.number_input("Sleep hours per day", min_value=1, max_value=24)
if sweets == "Daily" or sleep_hours < 6:
    sugar_status = "High"
elif sweets == "Sometimes":
    sugar_status = "Normal"
else:
    sugar_status = "Low"
fasting_blood_sugar = get_vital_value(sugar_status, 70, 100, 130)

# Estimate SpO2
st.subheader("Estimate Oxygen Level (SpO₂)")
smoking = st.selectbox("Do you smoke?", ["No", "Occasionally", "Regularly"])
if smoking == "Regularly" or pollution_index > 80:
    spo2_status = "Low"
else:
    spo2_status = "Normal"
spo2 = get_vital_value(spo2_status, 93, 98, 98)

chronic_disease = st.selectbox("Chronic Disease", df['chronic_disease'].unique())
if chronic_disease == "Other":
    chronic_disease_other = st.text_input("Please specify your chronic disease")
else:
    chronic_disease_other = chronic_disease

# -----------------------
# Exercise & Diet (shortened)
# -----------------------
st.header("🏋️ Lifestyle & Diet")
do_exercise = st.radio("Do you exercise regularly?", ["Yes", "No"])
exercise_mins_per_week = st.number_input("Minutes of exercise per week", min_value=0, max_value=2000, step=5) if do_exercise=="Yes" else 0

alcohol = st.selectbox("Do you consume alcohol?", ["No", "Occasionally", "Regularly"])
wellness_program = st.radio("Wellness Program Provided?", ["Yes","No","Sometimes"])

# Simple diet type indicator
diet_type = st.radio("Your usual food type?", ["Veg", "Non-Veg", "Mix"])
if diet_type == "Veg":
    diet_category = "Low"
elif diet_type == "Mix":
    diet_category = "Normal"
else:
    diet_category = "High"

# -----------------------
# Mental & Work
# -----------------------
st.header("💼 Work & Stress")
shift_pattern = st.selectbox("Shift Pattern", ["Day","Night","Rotational"])
working_hours_per_week = st.number_input("Working hours per week", min_value=20, max_value=120, step=1)
stress_level = int(np.clip(5 + (working_hours_per_week/20) + (0 if do_exercise=="Yes" else 2), 1, 10))
mood = st.selectbox("How do you feel today?", ["😊 Happy","😐 Neutral","😔 Sad","😟 Stressed","😡 Angry"])
mindfulness = st.slider("Minutes of Mindfulness / Meditation Everyday", 0, 60, 0)

# -----------------------
# Predict
# -----------------------
if st.button("Predict My Risk & Download PDF"):
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
        'predictive_system_usage':["Yes"],
        'diet_category':[diet_category]
    })

    categorical_cols = ['post','posted_city','gender','chronic_disease','smoking','alcohol',
                        'shift_pattern','healthcare_scheme','technological_support','predictive_system_usage','diet_category']
    input_encoded = safe_transform(ct_encoder, input_data, df, categorical_cols)
    risk_score = float(xgb_model.predict(input_encoded)[0])

    if smoking == "Occasionally": risk_score += 5
    elif smoking == "Regularly": risk_score += 10
    if alcohol == "Occasionally": risk_score += 3
    elif alcohol == "Regularly": risk_score += 8

    if risk_score < 40:
        risk_category = "✅ Normal"
    elif risk_score < 70:
        risk_category = "⚠ Borderline"
    else:
        risk_category = "❌ High Risk"

    st.subheader(f"Your Risk Category: {risk_category}")
    st.write(f"Estimated Risk Score: {risk_score:.1f}")

    # PDF
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Head', fontSize=14, spaceAfter=6, alignment=1))
    elems=[]
    elems.append(Paragraph("Predictive Healthcare Report", styles['Head']))
    elems.append(Spacer(1,8))
    table = Table([
        ["Blood Pressure", bp_status],
        ["Heart Rate", heart_status],
        ["Cholesterol", chol_status],
        ["Fasting Blood Sugar", sugar_status],
        ["SpO₂", spo2_status],
        ["Diet Type", diet_type],
        ["Exercise", do_exercise],
        ["Smoking", smoking],
        ["Alcohol", alcohol],
        ["Risk Category", risk_category]
    ], colWidths=[180,300])
    table.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.3,colors.grey),('FONTSIZE',(0,0),(-1,-1),10)]))
    elems.append(table)
    elems.append(Spacer(1,10))
    elems.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", styles['Normal']))
    pdf.build(elems)
    buffer.seek(0)
    st.download_button("📥 Download Full PDF Report", buffer, file_name=f"police_health_report_{personnel_id}.pdf", mime="application/pdf")
