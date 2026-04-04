import streamlit as st
import pandas as pd
import numpy as np
import joblib
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(
    page_title="Predictive Healthcare System for Police Personnel",
    layout="wide"
)

# -----------------------------
# LOAD FILES
# -----------------------------
df = pd.read_csv("police_health_dataset.csv")
ct_encoder = joblib.load("ct_encoder.pkl")
xgb_model = joblib.load("xgb_model.pkl")

styles = getSampleStyleSheet()

# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def calculate_bmi(weight, height):
    if height == 0:
        return 0
    return round(weight / ((height / 100) ** 2), 2)


def bmi_category(bmi):

    if bmi < 18.5:
        return "Underweight"

    elif bmi < 25:
        return "Normal"

    elif bmi < 30:
        return "Overweight"

    else:
        return "Obese"


def estimate_spo2(smoking):

    spo2 = 98

    if smoking == "Regularly":
        spo2 -= 3
    elif smoking == "Occasionally":
        spo2 -= 1

    return spo2


def detect_stress(work_hours, sleep):

    score = 0

    if work_hours > 60:
        score += 2
    elif work_hours > 50:
        score += 1

    if sleep < 6:
        score += 2

    if score >= 3:
        return "High"
    elif score >= 1:
        return "Moderate"
    else:
        return "Low"


# -----------------------------
# UI
# -----------------------------

st.title("Predictive Healthcare Framework for Police Personnel")

st.markdown("---")

# -----------------------------
# PERSONAL DETAILS
# -----------------------------

st.header("Personnel Details")

col1, col2, col3 = st.columns(3)

with col1:
    personnel_id = st.text_input("Personnel ID")
    age = st.number_input("Age", 18, 100)
    gender = st.selectbox("Gender", df["gender"].unique())

with col2:
    years_of_service = st.number_input("Years of Service", 0, 40)
    post = st.selectbox("Post", df["post"].unique())
    posted_city = st.selectbox("Posted City", df["posted_city"].unique())

with col3:
    height_cm = st.number_input("Height (cm)", 120, 220)
    weight_kg = st.number_input("Weight (kg)", 40, 150)

    bmi = calculate_bmi(weight_kg, height_cm)

    st.metric("BMI", bmi)
    st.metric("BMI Category", bmi_category(bmi))

st.markdown("---")

# -----------------------------
# VITAL SIGNS
# -----------------------------

st.header("Vital Signs")

systolic_bp = st.number_input("Systolic BP", 80, 200, 120)
diastolic_bp = st.number_input("Diastolic BP", 60, 120, 80)

cholesterol = st.number_input("Cholesterol", 120, 300, 200)

fasting_blood_sugar = st.number_input("Fasting Blood Sugar", 70, 200, 100)

heart_rate = st.number_input("Heart Rate", 50, 130, 80)

st.markdown("---")

# -----------------------------
# LIFESTYLE
# -----------------------------

st.header("Lifestyle")

sleep_hours = st.slider("Sleep Hours", 0.0, 12.0, 6.0)

exercise_mins_per_week = st.slider("Exercise Minutes / Week", 0, 600, 0)

smoking = st.selectbox("Smoking", ["No", "Occasionally", "Regularly"])

alcohol = st.selectbox("Alcohol", ["No", "Occasionally", "Regularly"])

working_hours_per_week = st.slider("Working Hours per Week", 20, 100, 45)

shift_pattern = st.selectbox("Shift Pattern", df["shift_pattern"].unique())

st.markdown("---")

# -----------------------------
# PREDICTION
# -----------------------------

if st.button("Predict Health Risk"):

    smoking_val = 0 if smoking == "No" else 1 if smoking == "Occasionally" else 2
    alcohol_val = 0 if alcohol == "No" else 1 if alcohol == "Occasionally" else 2

    # MATCH TRAINING FEATURES
    input_data = pd.DataFrame({
        "age":[age],
        "years_of_service":[years_of_service],
        "height_cm":[height_cm],
        "weight_kg":[weight_kg],
        "bmi":[bmi],
        "systolic_bp":[systolic_bp],
        "diastolic_bp":[diastolic_bp],
        "cholesterol":[cholesterol],
        "fasting_blood_sugar":[fasting_blood_sugar],
        "heart_rate":[heart_rate],
        "sleep_hours":[sleep_hours],
        "exercise_mins_per_week":[exercise_mins_per_week],
        "working_hours_per_week":[working_hours_per_week],
        "smoking":[smoking_val],
        "alcohol":[alcohol_val],
        "gender":[gender],
        "post":[post],
        "posted_city":[posted_city],
        "shift_pattern":[shift_pattern]
    })

    # ENCODE
    encoded = ct_encoder.transform(input_data)

    # PREDICT
    risk_score = xgb_model.predict(encoded)[0]

    # ADDITIONAL ANALYSIS
    spo2 = estimate_spo2(smoking)
    stress = detect_stress(working_hours_per_week, sleep_hours)

    st.subheader("Health Results")

    col1, col2, col3 = st.columns(3)

    col1.metric("Risk Score", round(risk_score,2))
    col2.metric("Estimated SpO₂", str(spo2) + "%")
    col3.metric("Stress Level", stress)

    if risk_score < 30:
        st.success("Low Risk")
    elif risk_score < 60:
        st.warning("Moderate Risk")
    else:
        st.error("High Risk")

    # -----------------------------
    # PDF REPORT
    # -----------------------------

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=A4)

    elements = []

    elements.append(Paragraph("Police Personnel Health Report", styles["Title"]))
    elements.append(Spacer(1,20))

    table_data = [

        ["Personnel ID", personnel_id],
        ["Age", age],
        ["BMI", bmi],
        ["Risk Score", round(risk_score,2)],
        ["Stress Level", stress],
        ["SpO2", str(spo2)+"%"]

    ]

    table = Table(table_data)

    elements.append(table)

    doc.build(elements)

    pdf = buffer.getvalue()

    st.download_button(
        label="Download Health Report",
        data=pdf,
        file_name="health_report.pdf",
        mime="application/pdf"
    )
