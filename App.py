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
    technological_support = st.radio("Technology Support Level", ["High", "Medium", "Low"])
with col2:
    predictive_system_usage = st.radio("Use of Predictive System?", ["Yes", "No"])

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

from fpdf import FPDF
import streamlit as st
import datetime

if 'risk_score' in locals():
    st.subheader("📄 Download Styled PDF Report")

    class PDFReport(FPDF):
        def header(self):
            # Logo
            self.image("police_logo.png", 10, 8, 25)  # replace with your local logo
            self.set_font("Poppins", "B", 16)
            self.cell(0, 10, "Predictive Healthcare Report", ln=True, align="C")
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font("Poppins", "I", 10)
            self.set_text_color(128)
            self.cell(0, 10, f"Generated from YourSiteName | Developed by Pranita Marodkar | Page {self.page_no()}", 0, 0, "C")

    pdf = PDFReport('P', 'mm', 'A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Poppins", "", 12)

    # Section: User Info
    pdf.set_font("Poppins", "B", 14)
    pdf.cell(0, 10, "👤 Personnel Information", ln=True)
    pdf.set_font("Poppins", "", 12)
    for col in input_data.columns:
        pdf.cell(0, 8, f"{col}: {input_data[col].iloc[0]}", ln=True)

    pdf.ln(5)
    # Risk Info
    pdf.set_font("Poppins", "B", 14)
    pdf.cell(0, 10, "📊 Risk Assessment", ln=True)
    pdf.set_font("Poppins", "", 12)
    pdf.cell(0, 8, f"Risk Score: {risk_score:.1f}", ln=True)
    pdf.cell(0, 8, f"Risk Category: {risk_category}", ln=True)

    pdf.ln(5)
    # Top Features
    pdf.set_font("Poppins", "B", 14)
    pdf.cell(0, 10, "⚡ Top Factors Impacting Risk", ln=True)
    pdf.set_font("Poppins", "", 12)
    for i in top_indices[:5]:
        pdf.cell(0, 8, f"{feature_names[i]} (Importance: {xgb_model.feature_importances_[i]:.2f})", ln=True)

    pdf.ln(5)
    # Recommendations
    pdf.set_font("Poppins", "B", 14)
    pdf.cell(0, 10, "💡 Personalized Recommendations", ln=True)
    pdf.set_font("Poppins", "", 12)
    for rec in recommendations:
        pdf.multi_cell(0, 8, f"- {rec}")
    
    # Footer and date
    pdf.ln(5)
    pdf.set_font("Poppins", "I", 10)
    pdf.cell(0, 8, f"Report Generated on: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", ln=True)

    # Save PDF to buffer
    import io
    pdf_buffer = io.BytesIO()
    pdf.output(pdf_buffer)
    pdf_buffer.seek(0)

    # Download button
    st.download_button(
        label="📥 Download PDF Report",
        data=pdf_buffer,
        file_name=f"police_health_report_{personnel_id}.pdf",
        mime="application/pdf"
    )



