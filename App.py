# App.py (FINAL STABLE VERSION)

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import io
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors


# PAGE CONFIG
st.set_page_config(
    page_title="Predictive Healthcare Framework for Police Personnel",
    layout="wide"
)

# HEADER
st.title("Predictive Healthcare for Police Personnel")


# LOAD DATA
df = pd.read_csv("police_health_dataset.csv")
ct_encoder = joblib.load("ct_encoder.pkl")
xgb_model = joblib.load("xgb_model.pkl")


# -----------------------------
# HELPER FUNCTIONS
# -----------------------------

def get_numeric_from_level(level, low, normal, high):
    return low if level == "Low" else normal if level == "Normal" else high


def safe_transform(encoder, X, df_ref, categorical_cols):

    try:
        return encoder.transform(X)

    except Exception:

        X2 = X.copy()

        for col in categorical_cols:

            if col in df_ref.columns:

                known = list(df_ref[col].dropna().unique())

                if known:

                    X2[col] = X2[col].apply(lambda v: v if v in known else known[0])

        return encoder.transform(X2)


def align_columns(X, encoder):

    try:
        cols = encoder.feature_names_in_
        return X[cols]
    except:
        return X


# -----------------------------
# DEMOGRAPHICS
# -----------------------------

st.header("Demographics Information")

col1, col2, col3 = st.columns(3)

with col1:

    personnel_id = st.text_input("Personnel ID")

    age = st.number_input("Age", 18, 100)

    gender = st.radio("Gender", ["Male", "Female", "Other"])


with col2:

    years_of_service = st.number_input("Years of Service", 0, 40)

    post = st.selectbox("Post", df["post"].unique())

    posted_city = st.selectbox("Posted City", df["posted_city"].unique())


with col3:

    height_cm = st.number_input("Height (cm)", 120, 250)

    weight_kg = st.number_input("Weight (kg)", 30, 200)


bmi = round(weight_kg / ((height_cm / 100) ** 2), 1) if height_cm > 0 else 0

st.metric("BMI", bmi)


# -----------------------------
# SCHEMES
# -----------------------------

st.header("Police Personnel Scheme Policy")

schemes = st.multiselect(
    "Select schemes",
    [
        "MPKAY",
        "MJPJAY",
        "ESIC",
        "MPFHS",
        "CGHS",
        "State Government Medical Reimbursement Scheme",
        "Cashless Treatment GR for Govt Employee",
        "None",
        "Other"
    ]
)


# -----------------------------
# VITAL SIGNS
# -----------------------------

st.header("Vital Signs")

bp_level = st.selectbox("BP Level", ["Low", "Normal", "High"])

systolic_bp = get_numeric_from_level(bp_level, 95, 120, 150)
diastolic_bp = get_numeric_from_level(bp_level, 65, 80, 100)


cholesterol_level = st.selectbox("Cholesterol Level", ["Low", "Normal", "High"])
cholesterol = get_numeric_from_level(cholesterol_level, 150, 200, 270)


diabetes_level = st.selectbox("Diabetes Level", ["Low", "Normal", "High"])
fasting_blood_sugar = get_numeric_from_level(diabetes_level, 70, 100, 125)


heart_level = st.selectbox("Heart Rate Level", ["Low", "Normal", "High"])
heart_rate = get_numeric_from_level(heart_level, 55, 80, 110)


# SPO2
st.subheader("Oxygen Saturation (SpO₂)")

spo2_question = st.radio(
    "How do you feel?",
    [
        "Normal breathing",
        "Slight breathlessness",
        "Severe breathlessness"
    ]
)

spo2 = 98 if spo2_question == "Normal breathing" else (94 if spo2_question == "Slight breathlessness" else 90)

st.write(f"Estimated SpO₂: {spo2}%")


# -----------------------------
# LIFESTYLE
# -----------------------------

st.header("Lifestyle")

sleep_hours = st.slider("Sleep hours", 0.0, 12.0, 6.0)

exercise_mins_per_week = st.slider("Exercise Minutes / Week", 0, 600, 0)

smoking = st.selectbox("Smoking", ["No", "Occasionally", "Regularly"])

alcohol = st.selectbox("Alcohol", ["No", "Occasionally", "Regularly"])


# -----------------------------
# WORK
# -----------------------------

st.header("Work Pattern")

shift_pattern = st.selectbox("Shift Pattern", ["Day", "Night", "Rotational"])

working_hours_per_week = st.slider("Working Hours per Week", 20, 100, 45)


# -----------------------------
# STRESS
# -----------------------------

stress_level = st.slider("Stress Level (1-10)", 1, 10, 5)


# -----------------------------
# PREDICTION
# -----------------------------

if st.button("Predict Health Risk"):

    try:
        personnel_id = int(personnel_id)
    except:
        personnel_id = 0


    input_data = pd.DataFrame({

        "personnel_id":[personnel_id],
        "post":[post],
        "posted_city":[posted_city],
        "age":[age],
        "gender":[gender],
        "years_of_service":[years_of_service],
        "height_cm":[height_cm],
        "weight_kg":[weight_kg],
        "bmi":[bmi],
        "systolic_bp":[systolic_bp],
        "diastolic_bp":[diastolic_bp],
        "heart_rate":[heart_rate],
        "spo2":[spo2],
        "fasting_blood_sugar":[fasting_blood_sugar],
        "cholesterol":[cholesterol],
        "sleep_hours":[sleep_hours],
        "exercise_mins_per_week":[exercise_mins_per_week],
        "smoking":[smoking],
        "alcohol":[alcohol],
        "stress_level":[stress_level],
        "shift_pattern":[shift_pattern],
        "working_hours_per_week":[working_hours_per_week],
        "predictive_system_usage":["Yes"]

    })


    categorical_cols = [
        "post","posted_city","gender","smoking","alcohol",
        "shift_pattern","predictive_system_usage"
    ]


    input_data = align_columns(input_data, ct_encoder)

    encoded = safe_transform(ct_encoder, input_data, df, categorical_cols)


    risk_score = float(xgb_model.predict(encoded)[0])


    if smoking == "Occasionally":
        risk_score += 5
    elif smoking == "Regularly":
        risk_score += 10

    if alcohol == "Occasionally":
        risk_score += 3
    elif alcohol == "Regularly":
        risk_score += 8


    st.subheader("Risk Result")

    st.metric("Risk Score", round(risk_score,1))


    if risk_score < 40:
        st.success("Normal Risk")
    elif risk_score < 70:
        st.warning("Borderline Risk")
    else:
        st.error("High Risk")


# -----------------------------
# PDF REPORT
# -----------------------------

    buffer = io.BytesIO()

    pdf = SimpleDocTemplate(buffer, pagesize=A4)

    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("Police Personnel Health Report", styles["Title"]))
    elements.append(Spacer(1,20))


    table_data = [

        ["Personnel ID", personnel_id],
        ["Age", age],
        ["BMI", bmi],
        ["Risk Score", round(risk_score,1)],
        ["Sleep Hours", sleep_hours],
        ["Stress Level", stress_level]

    ]

    table = Table(table_data)

    elements.append(table)

    pdf.build(elements)

    buffer.seek(0)


    st.download_button(
        label="Download PDF Report",
        data=buffer,
        file_name="health_report.pdf",
        mime="application/pdf"
    )
