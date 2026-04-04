# ============================================================
# Predictive Healthcare Framework for Police Personnel
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import io

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(page_title="Predictive Healthcare System", layout="wide")

st.title("🚓 Predictive Healthcare Framework for Police Personnel")


# ============================================================
# LOAD DATA
# ============================================================

@st.cache_data
def load_data():
    return pd.read_csv("police_health_dataset.csv")

df = load_data()

@st.cache_resource
def load_models():
    encoder = joblib.load("ct_encoder.pkl")
    model = joblib.load("xgb_model.pkl")
    return encoder, model

ct_encoder, xgb_model = load_models()


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def level_to_value(level, low, normal, high):
    if level == "Low":
        return low
    elif level == "Normal":
        return normal
    else:
        return high


def calculate_bmi(height, weight):
    if height == 0:
        return 0
    return round(weight / ((height/100)**2),2)


def estimate_spo2(condition):

    if condition == "Normal":
        return 98
    elif condition == "Mild Breathlessness":
        return 95
    elif condition == "Moderate Breathlessness":
        return 92
    else:
        return 88


def calculate_stress(sleep, exercise, work, shift):

    stress = 4

    if sleep < 5:
        stress += 4
    elif sleep < 6:
        stress += 3
    elif sleep < 7:
        stress += 2

    if exercise == 0:
        stress += 3
    elif exercise < 60:
        stress += 2

    if work > 60:
        stress += 3
    elif work > 50:
        stress += 2

    if shift == "Night":
        stress += 2

    return int(np.clip(stress,1,10))


# ============================================================
# DEMOGRAPHICS
# ============================================================

st.header("Demographic Information")

col1,col2,col3 = st.columns(3)

with col1:
    personnel_id = st.text_input("Personnel ID")
    age = st.number_input("Age",18,70)
    gender = st.selectbox("Gender",df["gender"].unique())

with col2:
    years_of_service = st.number_input("Years of Service",0,40)
    post = st.selectbox("Post",df["post"].unique())
    posted_city = st.selectbox("Posted City",df["posted_city"].unique())

with col3:
    height_cm = st.number_input("Height (cm)",120,220)
    weight_kg = st.number_input("Weight (kg)",40,150)

bmi = calculate_bmi(height_cm,weight_kg)

st.metric("BMI",bmi)


# ============================================================
# CITY DATA
# ============================================================

city_row = df[df["posted_city"]==posted_city]

if len(city_row) > 0:
    pollution_index = float(city_row["pollution_index"].iloc[0])
    city_workload_index = float(city_row["city_workload_index"].iloc[0])
else:
    pollution_index = df["pollution_index"].mean()
    city_workload_index = df["city_workload_index"].mean()


# ============================================================
# VITAL SIGNS
# ============================================================

st.header("Vital Signs")

bp_level = st.selectbox("Blood Pressure Level",["Low","Normal","High"])

systolic_bp = level_to_value(bp_level,95,120,150)
diastolic_bp = level_to_value(bp_level,65,80,95)

cholesterol_level = st.selectbox("Cholesterol Level",["Low","Normal","High"])

cholesterol = level_to_value(cholesterol_level,150,200,260)

sugar_level = st.selectbox("Blood Sugar Level",["Low","Normal","High"])

fasting_blood_sugar = level_to_value(sugar_level,70,100,130)

heart_rate_level = st.selectbox("Heart Rate Level",["Low","Normal","High"])

heart_rate = level_to_value(heart_rate_level,55,75,110)


# ============================================================
# SPO2
# ============================================================

st.header("Oxygen Level")

breathing_condition = st.selectbox(
    "Breathing Condition",
    ["Normal","Mild Breathlessness","Moderate Breathlessness","Severe Breathlessness"]
)

spo2 = estimate_spo2(breathing_condition)

st.metric("Estimated SpO2",spo2)


# ============================================================
# LIFESTYLE
# ============================================================

st.header("Lifestyle")

sleep_hours = st.slider("Sleep Hours",0.0,12.0,6.0)

exercise_mins_per_week = st.number_input("Exercise Minutes Per Week",0,600)

smoking = st.selectbox("Smoking",["No","Occasionally","Regularly"])

alcohol = st.selectbox("Alcohol",["No","Occasionally","Regularly"])

shift_pattern = st.selectbox("Shift Pattern",["Day","Night","Rotational"])

working_hours_per_week = st.number_input("Working Hours Per Week",10,120)


# ============================================================
# STRESS
# ============================================================

stress_level = calculate_stress(
    sleep_hours,
    exercise_mins_per_week,
    working_hours_per_week,
    shift_pattern
)

st.metric("Estimated Stress Level",stress_level)


# ============================================================
# DISEASE
# ============================================================

st.header("Medical Information")

chronic_disease = st.selectbox("Chronic Disease",df["chronic_disease"].unique())

healthcare_scheme = st.selectbox("Healthcare Scheme",df["healthcare_scheme"].unique())

technological_support = st.selectbox("Technological Support",["Low","Medium","High"])

predictive_system_usage = st.selectbox("Predictive Monitoring Usage",["Yes","No"])


# ============================================================
# PREDICT BUTTON
# ============================================================

if st.button("Predict Health Risk"):

    input_data = pd.DataFrame({

        "post":[post],
        "posted_city":[posted_city],
        "pollution_index":[pollution_index],
        "city_workload_index":[city_workload_index],
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
        "chronic_disease":[chronic_disease],
        "sleep_hours":[sleep_hours],
        "exercise_mins_per_week":[exercise_mins_per_week],
        "smoking":[smoking],
        "alcohol":[alcohol],
        "stress_level":[stress_level],
        "shift_pattern":[shift_pattern],
        "working_hours_per_week":[working_hours_per_week],
        "healthcare_scheme":[healthcare_scheme],
        "technological_support":[technological_support],
        "predictive_system_usage":[predictive_system_usage]

    })


    # ============================================================
    # MATCH TRAINING COLUMNS
    # ============================================================

    for col in df.columns:

        if col not in input_data.columns and col != "personnel_id":

            input_data[col] = df[col].mode()[0]

    input_data = input_data[[c for c in df.columns if c != "personnel_id"]]

    input_data = input_data.fillna(df.mean(numeric_only=True))


    # ============================================================
    # ENCODE
    # ============================================================

    try:
        encoded = ct_encoder.transform(input_data)
    except Exception as e:
        st.error("Encoding error occurred. Please check input categories.")
        st.stop()


    # ============================================================
    # PREDICT
    # ============================================================

    risk_score = float(xgb_model.predict(encoded)[0])

    risk_score = max(0,min(100,risk_score))


    # ============================================================
    # CATEGORY
    # ============================================================

    if risk_score < 35:
        risk_category = "Low Risk"
    elif risk_score < 60:
        risk_category = "Moderate Risk"
    elif risk_score < 80:
        risk_category = "High Risk"
    else:
        risk_category = "Critical Risk"


    st.subheader("Prediction Result")

    st.write("Risk Score:",round(risk_score,2))
    st.write("Risk Category:",risk_category)


    # ============================================================
    # PDF REPORT
    # ============================================================

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer,pagesize=A4)

    styles = getSampleStyleSheet()

    elements=[]

    elements.append(Paragraph("Police Health Risk Report",styles['Title']))

    elements.append(Spacer(1,20))

    data=[
        ["Personnel ID",personnel_id],
        ["Age",age],
        ["Gender",gender],
        ["Post",post],
        ["City",posted_city],
        ["BMI",bmi],
        ["Risk Score",round(risk_score,2)],
        ["Risk Category",risk_category]
    ]

    table = Table(data)

    table.setStyle([('GRID',(0,0),(-1,-1),1,colors.grey)])

    elements.append(table)

    doc.build(elements)

    pdf = buffer.getvalue()

    st.download_button(
        "Download PDF Report",
        data=pdf,
        file_name="health_report.pdf"
    )
