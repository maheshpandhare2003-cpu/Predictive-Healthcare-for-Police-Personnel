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
# PAGE CONFIG (simplified)
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
    st.caption("Personalized Risk Assessment — simplified UI")

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

def qualitative_label_from_numeric(value, breaks):
    low_max, normal_max = breaks
    if value <= low_max:
        return "Low"
    elif value <= normal_max:
        return "Normal"
    else:
        return "High"

def safe_transform(encoder, X, df_ref, categorical_cols):
    """Safely transform even if some columns are missing in df_ref."""
    try:
        return encoder.transform(X)
    except Exception:
        X2 = X.copy()
        for col in categorical_cols:
            if col in X2.columns:
                if col in df_ref.columns:
                    known = list(df_ref[col].dropna().unique())
                    if known:
                        X2[col] = X2[col].apply(lambda v: v if v in known else known[0])
                    else:
                        X2[col] = X2[col].fillna("Unknown")
                else:
                    X2[col] = X2[col].fillna("Unknown")
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
# VITALS
# -----------------------
st.header("❤️ Vital Signs (select level — model uses numeric equivalents)")
col1, col2, col3 = st.columns(3)
with col1:
    bp_level = st.selectbox("Blood Pressure Level", ["Low","Normal","High"])
    systolic_bp = get_vital_value(bp_level, 95, 120, 150)
    diastolic_bp = get_vital_value(bp_level, 65, 80, 100)
with col2:
    heart_level = st.selectbox("Heart Rate Level", ["Low","Normal","High"])
    heart_rate = get_vital_value(heart_level, 55, 80, 110)
with col3:
    spo2_level = st.selectbox("SpO₂ Level", ["Low","Normal"])
    spo2 = get_vital_value(spo2_level, 92, 98, 98)

col1, col2 = st.columns(2)
with col1:
    sugar_level = st.selectbox("Fasting Blood Sugar Level", ["Low","Normal","High"])
    fasting_blood_sugar = get_vital_value(sugar_level, 70, 100, 125)
with col2:
    cholesterol_level = st.selectbox("Cholesterol Level", ["Low","Normal","High"])
    cholesterol = get_vital_value(cholesterol_level, 150, 200, 270)

chronic_disease = st.selectbox("Chronic Disease", df['chronic_disease'].unique())
if chronic_disease == "Other":
    chronic_disease_other = st.text_input("Please specify your chronic disease")
else:
    chronic_disease_other = chronic_disease

# -----------------------
# LIFESTYLE
# -----------------------
st.header("🏋️ Lifestyle & Physical Health")

do_exercise = st.radio("Do you exercise?", ["Yes", "No"])
if do_exercise == "Yes":
    exercise_mins_per_week = st.number_input("Exercise minutes per week", min_value=0, max_value=10000, step=5)
    exercise_types = st.multiselect("Select exercise types", ["Walking","Running","Jogging","Swimming","Cycling","Weight training","Yoga"])
else:
    exercise_mins_per_week = 0
    exercise_types = []

sleep_hours = st.number_input("Sleep hours per day", min_value=1, max_value=24)
smoking = st.selectbox("Do you smoke?", ["No","Occasionally","Regularly"])
alcohol = st.selectbox("Do you consume alcohol?", ["No","Occasionally","Regularly"])
wellness_program = st.radio("Wellness Program Provided by Department?", ["Yes","No","Sometimes"])

# -----------------------
# PREDICTION & REPORT
# -----------------------
st.markdown("---")
st.header("🩺 Prediction & Report")

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
        'chronic_disease':[chronic_disease_other if chronic_disease_other else "None"],
        'sleep_hours':[sleep_hours],
        'exercise_mins_per_week':[exercise_mins_per_week],
        'smoking':[smoking],
        'alcohol':[alcohol],
        'shift_pattern':["Day"],
        'stress_level':[5],
        'technological_support':["Low"],
        'predictive_system_usage':["Yes"]
    })

    input_data.fillna("Unknown", inplace=True)
    categorical_cols = [c for c in [
        'post','posted_city','gender','chronic_disease','smoking','alcohol',
        'shift_pattern','healthcare_scheme','technological_support','predictive_system_usage'
    ] if c in input_data.columns]

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

    st.markdown("### Results")
    st.write(f"**Risk Score:** {risk_score:.1f}")
    st.write(f"**Risk Category:** {risk_category}")

    recommendations = ["Maintain a healthy lifestyle."] if risk_category == "✅ Normal" else \
                      ["Pay attention to diet and rest."] if risk_category == "⚠ Borderline" else \
                      ["Consult a healthcare professional immediately."]

    # -----------------------
    # PDF Generation
    # -----------------------
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    try:
        logo = Image("—Pngtree—gold police officer badge_7258551.png", width=60, height=60)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1,8))
    except:
        pass

    elements.append(Paragraph("Predictive Healthcare Report", styles['Title']))
    elements.append(Spacer(1,8))
    elements.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1,12))

    vitals_rows = [
        ["Blood Pressure", bp_level],
        ["Heart Rate", heart_level],
        ["SpO₂", spo2_level],
        ["Fasting Blood Sugar", sugar_level],
        ["Cholesterol", cholesterol_level]
    ]
    vitals_table = Table(vitals_rows, colWidths=[180, 320])
    vitals_table.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.3,colors.grey)]))
    elements.append(vitals_table)
    elements.append(Spacer(1,10))

    elements.append(Paragraph(f"Risk Category: {risk_category}", styles['Heading2']))
    elements.append(Paragraph(f"Risk Score: {risk_score:.1f}", styles['Normal']))
    elements.append(Spacer(1,8))

    elements.append(Paragraph("Recommendations", styles['Heading2']))
    for rec in recommendations:
        elements.append(Paragraph(f"• {rec}", styles['Normal']))

    elements.append(Spacer(1,16))
    elements.append(Paragraph("© 2025 Police Health Analytics", ParagraphStyle('Footer', fontSize=8, alignment=1)))

    pdf.build(elements)
    buffer.seek(0)

    st.download_button(
        label="📥 Download Full PDF Report",
        data=buffer,
        file_name=f"police_health_report_{personnel_id}.pdf",
        mime="application/pdf"
    )

st.markdown("---")
st.caption("© 2025 Police Health Analytics | Developed for Research and Awareness")
