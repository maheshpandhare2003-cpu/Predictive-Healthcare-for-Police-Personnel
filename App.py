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

# ---------------------------------------------------------
# BASIC PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Predictive Healthcare for Police Personnel",
    page_icon="—Pngtree—gold police officer badge_7258551.png",
    layout="centered"
)

# ---------------------------------------------------------
# HEADER SECTION
# ---------------------------------------------------------
st.image("—Pngtree—gold police officer badge_7258551.png", width=100)
st.title("Predictive Healthcare for Police Personnel")
st.caption("Get your personalized risk assessment and preventive suggestions")

# ---------------------------------------------------------
# LOAD MODEL AND DATA
# ---------------------------------------------------------
df = pd.read_csv("police_health_dataset.csv")
ct_encoder = joblib.load("ct_encoder.pkl")
xgb_model = joblib.load("xgb_model.pkl")

# ---------------------------------------------------------
# DEMOGRAPHIC SECTION
# ---------------------------------------------------------
st.header("👤 Demographic Information")

col1, col2 = st.columns(2)
with col1:
    personnel_id = st.number_input("Personnel ID", min_value=1, step=1)
    age = st.number_input("Age (years)", min_value=18, max_value=100)
    gender = st.radio("Gender", ["Male", "Female", "Other"])
    years_of_service = st.number_input("Years of Service", min_value=0, step=1)
with col2:
    post = st.selectbox("Post", df['post'].unique())
    posted_city = st.selectbox("Posted City", df['posted_city'].unique())
    city_data = df[df['posted_city'] == posted_city].iloc[0]
    pollution_index = st.text_input("City Pollution Index", value=city_data['pollution_index'], disabled=True)
    city_workload_index = st.text_input("City Workload Index", value=city_data['city_workload_index'], disabled=True)

height_cm = st.number_input("Height (cm)", min_value=120, max_value=250)
weight_kg = st.number_input("Weight (kg)", min_value=30, max_value=200)
bmi = round(weight_kg / ((height_cm / 100) ** 2), 1)
st.text_input("BMI", value=bmi, disabled=True)

# ---------------------------------------------------------
# HEALTHCARE SECTION
# ---------------------------------------------------------
st.header("🏥 Healthcare Scheme & Awareness")
col1, col2 = st.columns(2)
with col1:
    healthcare_scheme = st.selectbox("Healthcare Scheme", df['healthcare_scheme'].unique())
    healthcare_scheme_other = st.text_input("Specify if Other") if healthcare_scheme == "Other" else None
with col2:
    wellness_program = st.radio("Wellness Program Provided?", ["Yes", "No", "Sometimes"])

# ---------------------------------------------------------
# VITAL SIGNS SECTION
# ---------------------------------------------------------
st.header("❤️ Vital Signs")

col1, col2, col3 = st.columns(3)
with col1:
    systolic_bp = st.number_input("Systolic BP (90–180)", min_value=90, max_value=180)
    diastolic_bp = st.number_input("Diastolic BP (60–120)", min_value=60, max_value=120)
with col2:
    heart_rate = st.number_input("Heart Rate (bpm)", min_value=50, max_value=120)
    spo2 = st.number_input("SpO₂ (%)", min_value=90, max_value=100)
with col3:
    fasting_blood_sugar = st.number_input("Fasting Blood Sugar (mg/dL)", min_value=70, max_value=130)
    cholesterol = st.number_input("Cholesterol (mg/dL)", min_value=100, max_value=300)

chronic_disease = st.selectbox("Chronic Disease", df['chronic_disease'].unique())
chronic_disease_other = st.text_input("Specify if Other") if chronic_disease == "Other" else None

# ---------------------------------------------------------
# LIFESTYLE SECTION
# ---------------------------------------------------------
st.header("🏋️ Lifestyle & Physical Health")

col1, col2 = st.columns(2)
with col1:
    exercise_mins_per_week = st.number_input("Exercise Minutes per Week", min_value=0, max_value=1000)
    sleep_hours = st.number_input("Sleep Hours per Day", min_value=1, max_value=24)
with col2:
    smoking = st.selectbox("Do You Smoke?", ["No", "Occasionally", "Regularly"])
    alcohol = st.selectbox("Do You Consume Alcohol?", ["No", "Occasionally", "Regularly"])

water_intake_liters = st.number_input("Daily Water Intake (Liters)", min_value=0.0, max_value=10.0, step=0.1)

# ---------------------------------------------------------
# OCCUPATIONAL SECTION
# ---------------------------------------------------------
st.header("💼 Occupational Health")
col1, col2 = st.columns(2)
with col1:
    shift_pattern = st.selectbox("Shift Pattern", ["Day", "Night", "Rotational"])
with col2:
    working_hours_per_week = st.number_input("Working Hours per Week", min_value=1, max_value=120)

# ---------------------------------------------------------
# MENTAL HEALTH SECTION
# ---------------------------------------------------------
st.header("🧠 Mental Health & Wellbeing")

# Basic stress calculator
stress_level = 5
if sleep_hours < 6: stress_level += 2
if working_hours_per_week > 50: stress_level += 2
if exercise_mins_per_week < 60: stress_level += 1
if shift_pattern in ["Night", "Rotational"]: stress_level += 1
stress_level = int(np.clip(stress_level, 1, 10))

mood = st.selectbox("Your Current Mood", ["😊 Happy", "😐 Neutral", "😔 Sad", "😟 Stressed", "😡 Angry"])
st.progress(stress_level / 10, text=f"Stress Level: {stress_level}/10")

# ---------------------------------------------------------
# PREDICTION BUTTON
# ---------------------------------------------------------
if st.button("🔍 Predict My Risk"):
    input_data = pd.DataFrame({
        'personnel_id': [personnel_id],
        'post': [post],
        'posted_city': [posted_city],
        'pollution_index': [pollution_index],
        'city_workload_index': [city_workload_index],
        'age': [age],
        'gender': [gender],
        'years_of_service': [years_of_service],
        'height_cm': [height_cm],
        'weight_kg': [weight_kg],
        'bmi': [bmi],
        'systolic_bp': [systolic_bp],
        'diastolic_bp': [diastolic_bp],
        'heart_rate': [heart_rate],
        'spo2': [spo2],
        'fasting_blood_sugar': [fasting_blood_sugar],
        'cholesterol': [cholesterol],
        'chronic_disease': [chronic_disease if chronic_disease != "Other" else chronic_disease_other],
        'sleep_hours': [sleep_hours],
        'exercise_mins_per_week': [exercise_mins_per_week],
        'smoking': [smoking],
        'alcohol': [alcohol],
        'stress_level': [stress_level],
        'shift_pattern': [shift_pattern],
        'working_hours_per_week': [working_hours_per_week],
        'healthcare_scheme': [healthcare_scheme if healthcare_scheme != "Other" else healthcare_scheme_other],
        'technological_support': ["Low"],
        'predictive_system_usage': ["Yes"]
    })

    # Ensure numeric columns
    numeric_cols = ['pollution_index','city_workload_index','age','years_of_service','height_cm','weight_kg','bmi',
                    'systolic_bp','diastolic_bp','heart_rate','spo2','fasting_blood_sugar','cholesterol',
                    'sleep_hours','exercise_mins_per_week','stress_level','working_hours_per_week']
    for col in numeric_cols:
        input_data[col] = pd.to_numeric(input_data[col], errors='coerce')

    input_encoded = ct_encoder.transform(input_data)
    risk_score = float(xgb_model.predict(input_encoded)[0])

    # Adjust risk based on lifestyle
    if smoking == "Occasionally": risk_score += 5
    elif smoking == "Regularly": risk_score += 10
    if alcohol == "Occasionally": risk_score += 3
    elif alcohol == "Regularly": risk_score += 8

    # Risk category
    if risk_score < 40:
        risk_category = "✅ Normal"
    elif risk_score < 70:
        risk_category = "⚠ Borderline"
    else:
        risk_category = "❌ High Risk"

    # Display results
    st.subheader("📊 Health Risk Result")
    st.write(f"**Risk Score:** {risk_score:.1f}")
    st.write(f"**Category:** {risk_category}")

    # ---------------------------------------------------------
    # RECOMMENDATIONS
    # ---------------------------------------------------------
    st.subheader("💡 Personalized Recommendations")
    if risk_category == "✅ Normal":
        st.success("Maintain your current healthy lifestyle and continue regular check-ups.")
    elif risk_category == "⚠ Borderline":
        st.warning("Pay attention to your diet, exercise regularly, and monitor your vital signs.")
    else:
        st.error("High risk detected! Consult a healthcare professional for immediate advice.")

    # ---------------------------------------------------------
    # PDF REPORT DOWNLOAD
    # ---------------------------------------------------------
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Predictive Healthcare Report", styles['Title']))
    elements.append(Spacer(1, 12))
    data = [[k, str(v[0])] for k, v in input_data.to_dict().items()]
    table = Table(data, colWidths=[200, 300])
    table.setStyle(TableStyle([('GRID', (0,0), (-1,-1), 0.5, colors.grey)]))
    elements.append(table)
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Risk Score: {risk_score:.1f}", styles['Normal']))
    elements.append(Paragraph(f"Risk Category: {risk_category}", styles['Normal']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Report Generated On: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))

    pdf.build(elements)
    buffer.seek(0)

    st.download_button(
        label="📥 Download PDF Report",
        data=buffer,
        file_name=f"police_health_report_{personnel_id}.pdf",
        mime="application/pdf"
    )

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("---")
st.caption("© 2025 Police Health Analytics | Developed for Research and Awareness")

