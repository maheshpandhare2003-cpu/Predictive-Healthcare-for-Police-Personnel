import streamlit as st
import base64
# App Title and Header
st.set_page_config(
    page_title="Predictive Healthcare for Police Personnel",
    page_icon="—Pngtree—gold police officer badge_7258551.png",
    layout="wide"
)

import base64
# Convert logo image to base64
with open("—Pngtree—gold police officer badge_7258551.png", "rb") as img_file:
    encoded_logo = base64.b64encode(img_file.read()).decode()

# Header Section
st.markdown(
    f"""
    <style>
        @keyframes gradientShift {{
            0% {{ background-position: 0% 50%; }}
            50% {{ background-position: 100% 50%; }}
            100% {{ background-position: 0% 50%; }}
        }}

        .app-header {{
            text-align: center;
            padding: 25px;
            color: white;
            border-radius: 15px;
            background: linear-gradient(135deg, #0F2027, #203A43, #2C5364);
            background-size: 300% 300%;
            animation: gradientShift 10s ease infinite;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.6);
        }}

        .app-header img {{
            width: 110px;
            border-radius: 50%;
            box-shadow: 0 0 15px rgba(255, 255, 255, 0.6);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .app-header img:hover {{
            transform: scale(1.05);
            box-shadow: 0 0 25px rgba(0, 191, 255, 0.9);
        }}

        .app-header h1 {{
            margin-top: 10px;
            font-size: 2.2em;
            font-weight: 700;
            letter-spacing: 1px;
            color: #E0F7FA;
            text-shadow: 0 0 10px rgba(0, 0, 0, 0.4);
        }}

        .app-header p {{
            font-size: 1.1em;
            color: #B3E5FC;
            text-shadow: 0 0 5px rgba(0, 0, 0, 0.3);
        }}
    </style>

    <div class='app-header'>
        <img src='data:image/png;base64,{encoded_logo}' alt='Police Logo'>
        <h1>Predictive Healthcare for Police Personnel</h1>
        <p>Get your personalized risk assessment and preventive suggestions</p>
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
    diet_quality = st.text_input("Diet Quality (Enter your description)")

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
    technological_support = st.radio("Technology Support Level Usage of Health Apps or Smart-Watches", ["High", "Medium", "Low"])
with col2:
    predictive_system_usage = st.radio("Use of Predictive System? (This Application) ", ["Yes", "No"])

st.subheader("📝 Awareness Section")

awareness_questions = [
    "I am fully aware of the healthcare policies designed for police personnel in my department.",
    "I regularly participate in healthcare or wellness programs provided by the department.",
    "The process for accessing departmental healthcare services is straightforward.",
    "I am satisfied with the healthcare benefits offered to me as a police officer.",
    "The healthcare policies are well communicated to all personnel.",
    "Department policies have improved my health and wellbeing."
]

# Store responses
awareness_responses = {}

for q in awareness_questions:
    awareness_responses[q] = st.radio(
        q,
        ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"],
        index=2  # Default to 'Neutral'
    )

import joblib
import numpy as np

# Load Encoder and Model
ct_encoder = joblib.load("ct_encoder.pkl")
xgb_model = joblib.load("xgb_model.pkl")

# Action Button
if st.button("Predict My Risk & Recommendations"):

    # Show spinner while computing
    with st.spinner("Calculating your risk score..."):

        # Prepare input data
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
            'technological_support': [technological_support],
            'predictive_system_usage': [predictive_system_usage]
        })

        # --- Convert numeric columns to float ---
        numeric_cols = [
            'personnel_id','pollution_index','city_workload_index','age','years_of_service',
            'height_cm','weight_kg','bmi','systolic_bp','diastolic_bp','heart_rate','spo2',
            'fasting_blood_sugar','cholesterol','sleep_hours','exercise_mins_per_week',
            'stress_level','working_hours_per_week'
        ]

        for col in numeric_cols:
            input_data[col] = pd.to_numeric(input_data[col], errors='coerce')  # converts invalid values to NaN

        # Check for invalid numeric input
        if input_data[numeric_cols].isnull().any().any():
            st.error("Some numeric inputs are invalid. Please check your entries.")
            st.stop()  # stop execution if invalid

        # --- Ensure categorical columns are strings ---
        categorical_cols = [
            'post','posted_city','gender','chronic_disease','smoking','alcohol',
            'shift_pattern','healthcare_scheme','technological_support','predictive_system_usage'
        ]
        for col in categorical_cols:
            input_data[col] = input_data[col].astype(str).fillna("Unknown")

        # Encode categorical features
        input_encoded = ct_encoder.transform(input_data)

        # Predict Risk Score
        risk_score = xgb_model.predict(input_encoded)[0]

        # Map risk score to category
        if risk_score < 40:
            risk_category = "✅ Normal"
            color = "green"
        elif risk_score < 70:
            risk_category = "⚠ Borderline"
            color = "yellow"
        else:
            risk_category = "❌ High Risk"
            color = "red"

        # Display Risk Score
        st.markdown(f"<h2 style='color:{color}'>Risk Score: {risk_score:.1f}</h2>", unsafe_allow_html=True)
        st.markdown(f"<h3 style='color:{color}'>Risk Category: {risk_category}</h3>", unsafe_allow_html=True)

        # Feature Importance (Top 5)
        importance = xgb_model.feature_importances_
        feature_names = input_data.columns
        top_indices = np.argsort(importance)[::-1][:5]

        st.subheader("📊 Top Factors Impacting Risk")
        for i in top_indices:
            st.progress(min(int(importance[i]*100), 100), text=f"{feature_names[i]}")

        # Placeholder for Recommendations
        

# Personalized Recommendations (Safe Version)
if 'risk_category' in locals():  # Check if risk_category exists
    st.subheader("💡 Personalized Recommendations")
    st.info("Based on your risk profile, recommended preventive measures will be displayed here.")

    recommendations = []

    # General advice based on risk category
    if risk_category == "✅ Normal":
        recommendations.append("Maintain your current healthy lifestyle and continue regular check-ups.")
    elif risk_category == "⚠ Borderline":
        recommendations.append("Pay attention to your diet, exercise regularly, and monitor vital signs closely with Healthcare Proffessional.")
    else:  # High Risk
        recommendations.append("Consult a healthcare professional immediately and follow preventive measures strictly.")

    # Targeted advice based on top 3 features
    top_features = [feature_names[i] for i in top_indices[:3]]  # top 3 impacting features
    for feature in top_features:
        if feature == "systolic_bp" or feature == "diastolic_bp":
            recommendations.append("Monitor your blood pressure regularly and reduce salt intake.")
        elif feature == "cholesterol":
            recommendations.append("Maintain a low-fat diet and avoid processed foods.")
        elif feature == "fasting_blood_sugar":
            recommendations.append("Check blood sugar regularly and limit sugary foods.")
        elif feature == "exercise_mins_per_week":
            recommendations.append("Increase your weekly exercise to improve overall health.")
        elif feature == "sleep_hours":
            recommendations.append("Ensure adequate sleep (7–8 hours) daily.")
        elif feature == "stress_level":
            recommendations.append("Practice stress management techniques like meditation or yoga.")
        elif feature == "smoking":
            recommendations.append("Consider quitting smoking to reduce health risks.")
        elif feature == "alcohol":
            recommendations.append("Limit alcohol consumption to improve health.")

    # Display recommendations
    for rec in recommendations:
        st.success(rec)


st.subheader("💬 Suggestions / Comments")
user_comments = st.text_area("Enter your comments or feedback here (optional):")

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import io
import datetime
import streamlit as st

if 'risk_score' in locals():
    st.subheader("📄 Download PDF Report")

    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=30, 
        leftMargin=30,
        topMargin=30, 
        bottomMargin=30
    )

    elements = []
    styles = getSampleStyleSheet()

    # Custom styles (renamed to avoid KeyError)
    styles.add(ParagraphStyle(name='HeadingLarge', fontSize=16, leading=20, spaceAfter=10, alignment=1, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='SubHeading', fontSize=14, leading=18, spaceAfter=8, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='NormalText', fontSize=12, leading=16, fontName='Helvetica'))
    styles.add(ParagraphStyle(name='BoldText', fontSize=12, leading=16, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='FooterText', fontSize=10, leading=12, alignment=1, textColor=colors.grey))
    from reportlab.platypus import Image ,Spacer

    # Add logo at top
    try:
     logo = Image("—Pngtree—gold police officer badge_7258551.png", width=60, height=60)
     logo.hAlign = 'CENTER'
     elements.append(logo)
     elements.append(Spacer(1, 8))
    except Exception as e:
     st.warning(f"Logo not loaded: {e}")

    # Title
    elements.append(Paragraph("Predictive Healthcare Report", styles['HeadingLarge']))
    elements.append(Spacer(1, 12))

    # Personnel Info Table
    elements.append(Paragraph("Personnel Information", styles['SubHeading']))
    data = [[col, str(input_data[col].iloc[0])] for col in input_data.columns]
    table = Table(data, colWidths=[150, 350])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Risk Assessment
    elements.append(Paragraph("Risk Assessment", styles['SubHeading']))

    if risk_category == "✅ Normal":
        color = colors.green
    elif risk_category == "⚠ Borderline":
        color = colors.orange
    else:
        color = colors.red

    elements.append(Paragraph(f"Risk Score: {risk_score:.1f}", ParagraphStyle('RiskScore', textColor=color, fontSize=12, leading=16)))
    elements.append(Paragraph(f"Risk Category: {risk_category}", ParagraphStyle('RiskCat', textColor=color, fontSize=12, leading=16)))
    elements.append(Spacer(1, 12))

    # Top Features
    elements.append(Paragraph("Top Factors Impacting Risk", styles['SubHeading']))
    for i in top_indices[:5]:
        elements.append(Paragraph(f"{feature_names[i]} (Importance: {xgb_model.feature_importances_[i]:.2f})", styles['NormalText']))
    elements.append(Spacer(1, 12))

    # Recommendations
    elements.append(Paragraph("Personalized Recommendations", styles['SubHeading']))
    for rec in recommendations:
        elements.append(Paragraph(f"• {rec}", styles['NormalText']))
    elements.append(Spacer(1, 12))

    # Footer / Timestamp
    footer_text = f"Generated from Police Personnel Healthcare | Developed by Pranita Marodkar | Report Date: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
    elements.append(Paragraph(footer_text, styles['FooterText']))

    # Build PDF
    pdf.build(elements)

    buffer.seek(0)
    st.download_button(
        label="📥 Download PDF Report",
        data=buffer,
        file_name=f"police_health_report_{input_data['personnel_id'].iloc[0]}.pdf",
        mime="application/pdf"
    )














