import streamlit as st
import pandas as pd
import numpy as np
import joblib
import io
import datetime
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# ---------------------------------------------------------
# PAGE CONFIGURATION
# ---------------------------------------------------------
st.set_page_config(
    page_title="Predictive Healthcare for Police Personnel",
    page_icon="—Pngtree—gold police officer badge_7258551.png",
    layout="wide"
)

# ---------------------------------------------------------
# LIGHT THEME STYLE
# ---------------------------------------------------------
st.markdown("""
<style>
body {
    background-color: #f8f9fa;
    color: #212529;
    font-family: "Helvetica", sans-serif;
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

# ---------------------------------------------------------
# HEADER SECTION
# ---------------------------------------------------------
col_logo, col_title = st.columns([1, 4])
with col_logo:
    st.image("—Pngtree—gold police officer badge_7258551.png", width=100)
with col_title:
    st.title("Predictive Healthcare for Police Personnel")
    st.caption("Personalized Risk Assessment and Preventive Suggestions")

# ---------------------------------------------------------
# LOAD DATA & MODEL
# ---------------------------------------------------------
df = pd.read_csv("police_health_dataset.csv")
ct_encoder = joblib.load("ct_encoder.pkl")
xgb_model = joblib.load("xgb_model.pkl")

# ---------------------------------------------------------
# DEMOGRAPHIC SECTION
# ---------------------------------------------------------
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
        pollution_index = 0.0
        city_workload_index = 0.0
    pollution_index = st.text_input("City Pollution Index", value=pollution_index, disabled=True)
    city_workload_index = st.text_input("City Workload Index", value=city_workload_index, disabled=True)
    height_cm = st.number_input("Height (cm)", min_value=120, max_value=250)
    weight_kg = st.number_input("Weight (kg)", min_value=30, max_value=200)

bmi = round(weight_kg / ((height_cm / 100) ** 2), 1)
st.text_input("BMI", value=bmi, disabled=True)

# ---------------------------------------------------------
# VITAL SIGNS SECTION (Low / Normal / High)
# ---------------------------------------------------------
st.header("❤️ Vital Signs (Categorical Levels)")

def get_bp_value(category):
    if category == "Low":
        return 95, 65
    elif category == "Normal":
        return 120, 80
    else:
        return 150, 100

col1, col2, col3 = st.columns(3)
with col1:
    bp_level = st.selectbox("Blood Pressure Level", ["Low", "Normal", "High"])
    systolic_bp, diastolic_bp = get_bp_value(bp_level)
with col2:
    heart_status = st.selectbox("Heart Rate Level", ["Low", "Normal", "High"])
    heart_rate = 55 if heart_status == "Low" else 80 if heart_status == "Normal" else 110
with col3:
    spo2_status = st.selectbox("Oxygen Level", ["Low", "Normal"])
    spo2 = 92 if spo2_status == "Low" else 98

col1, col2 = st.columns(2)
with col1:
    sugar_status = st.selectbox("Fasting Blood Sugar Level", ["Low", "Normal", "High"])
    fasting_blood_sugar = 80 if sugar_status == "Low" else 100 if sugar_status == "Normal" else 125
with col2:
    chol_status = st.selectbox("Cholesterol Level", ["Low", "Normal", "High"])
    cholesterol = 150 if chol_status == "Low" else 200 if chol_status == "Normal" else 270

chronic_disease = st.selectbox("Chronic Disease", df['chronic_disease'].unique())
chronic_disease_other = st.text_input("Specify if Other") if chronic_disease == "Other" else None

# ---------------------------------------------------------
# LIFESTYLE SECTION (Exercise conditional)
# ---------------------------------------------------------
st.header("🏋️ Lifestyle & Physical Health")

do_exercise = st.radio("Do you exercise?", ["Yes", "No"])
if do_exercise == "Yes":
    col1, col2, col3 = st.columns(3)
    with col1:
        exercise_mins_per_week = st.number_input("Exercise Minutes per Week", min_value=10, max_value=1000)
    with col2:
        sleep_hours = st.number_input("Sleep Hours per Day", min_value=1, max_value=24)
    with col3:
        water_intake_liters = st.number_input("Daily Water Intake (Liters)", min_value=0.0, max_value=10.0, step=0.1)
else:
    exercise_mins_per_week = 0
    col2, col3 = st.columns(2)
    with col2:
        sleep_hours = st.number_input("Sleep Hours per Day", min_value=1, max_value=24)
    with col3:
        water_intake_liters = st.number_input("Daily Water Intake (Liters)", min_value=0.0, max_value=10.0, step=0.1)

col1, col2 = st.columns(2)
with col1:
    smoking = st.selectbox("Do You Smoke?", ["No", "Occasionally", "Regularly"])
with col2:
    alcohol = st.selectbox("Do You Consume Alcohol?", ["No", "Occasionally", "Regularly"])

# Wellness Program (moved below Alcohol)
wellness_program = st.radio("Wellness Program Provided?", ["Yes", "No", "Sometimes"])

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

stress_level = 5
if sleep_hours < 6: stress_level += 2
if working_hours_per_week > 50: stress_level += 2
if exercise_mins_per_week < 60: stress_level += 1
if shift_pattern in ["Night", "Rotational"]: stress_level += 1
stress_level = int(np.clip(stress_level, 1, 10))

mood = st.selectbox("Your Current Mood", ["😊 Happy", "😐 Neutral", "😔 Sad", "😟 Stressed", "😡 Angry"])
st.progress(stress_level / 10, text=f"Stress Level: {stress_level}/10")

# ---------------------------------------------------------
# PREDICTION SECTION
# ---------------------------------------------------------
st.markdown("---")
st.header("🩺 Risk Prediction")

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
        'chronic_disease': [chronic_disease_other if chronic_disease == "Other" and chronic_disease_other else chronic_disease],
        'sleep_hours': [sleep_hours],
        'exercise_mins_per_week': [exercise_mins_per_week],
        'smoking': [smoking],
        'alcohol': [alcohol],
        'stress_level': [stress_level],
        'shift_pattern': [shift_pattern],
        'working_hours_per_week': [working_hours_per_week],
        'healthcare_scheme': [df['healthcare_scheme'].unique()[0]],
        'technological_support': ["Low"],
        'predictive_system_usage': ["Yes"]
    })

    input_data.fillna("Unknown", inplace=True)

    categorical_cols = [
        'post', 'posted_city', 'gender', 'chronic_disease', 'smoking', 'alcohol',
        'shift_pattern', 'healthcare_scheme', 'technological_support', 'predictive_system_usage'
    ]
    for col in categorical_cols:
        input_data[col] = input_data[col].astype(str)

    try:
        input_encoded = ct_encoder.transform(input_data)
    except Exception:
        for col in categorical_cols:
            if col in input_data.columns:
                input_data[col] = input_data[col].apply(lambda x: x if x in df[col].unique() else df[col].unique()[0])
        input_encoded = ct_encoder.transform(input_data)

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

    st.subheader("📊 Health Risk Result")
    st.write(f"**Risk Score:** {risk_score:.1f}")
    st.write(f"**Category:** {risk_category}")

    # ---------------------------------------------------------
    # PDF REPORT
    # ---------------------------------------------------------
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Predictive Healthcare Report", styles['Title']))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1, 20))

    # Replace numeric vitals with text labels
    input_data_display = input_data.copy()
    input_data_display['Blood Pressure'] = bp_level
    input_data_display['Heart Rate'] = heart_status
    input_data_display['SpO2'] = spo2_status
    input_data_display['Fasting Sugar'] = sugar_status
    input_data_display['Cholesterol'] = chol_status
    input_data_display['Exercise'] = "No Exercise" if exercise_mins_per_week == 0 else f"{exercise_mins_per_week} mins/week"

    # --- Table ---
    elements.append(Paragraph("Personnel & Health Information", styles['Heading2']))
    data_rows = [[k, str(v[0])] for k, v in input_data_display.to_dict().items()]
    table = Table(data_rows, colWidths=[200, 300])
    table.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 9),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph("Risk Assessment Summary", styles['Heading2']))
    elements.append(Paragraph(f"Risk Score: {risk_score:.1f}", styles['Normal']))
    elements.append(Paragraph(f"Risk Category: {risk_category}", styles['Normal']))
    elements.append(Spacer(1, 20))

    pdf.build(elements)
    buffer.seek(0)

    st.download_button(
        label="📥 Download Full PDF Report",
        data=buffer,
        file_name=f"police_health_report_{personnel_id}.pdf",
        mime="application/pdf"
    )

# ---------------------------------------------------------
# FOOTER
# ---------------------------------------------------------
st.markdown("---")
st.caption("© 2025 Police Health Analytics | Developed for Research and Awareness")
