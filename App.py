# ============================================================
# Predictive Healthcare Framework for Police Personnel
# Streamlit Application
# Compatible with:
# police_health_dataset.csv
# ct_encoder.pkl
# xgb_model.pkl
# ============================================================

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import io
import datetime

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Predictive Healthcare System",
    page_icon="🚑",
    layout="wide"
)

st.title("🚓 Predictive Healthcare Framework for Police Personnel")

# ============================================================
# LOAD DATASET AND MODELS
# ============================================================

@st.cache_data
def load_dataset():
    return pd.read_csv("police_health_dataset.csv")

df = load_dataset()

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

    if level == "Normal":
        return normal

    return high


def estimate_spo2(condition):

    if condition == "Normal":
        return 98

    if condition == "Mild Breathlessness":
        return 95

    if condition == "Moderate Breathlessness":
        return 92

    return 88


def calculate_bmi(height_cm, weight_kg):

    if height_cm == 0:
        return 0

    bmi = weight_kg / ((height_cm/100) ** 2)

    return round(bmi, 2)


def calculate_stress(sleep_hours, exercise, work_hours, shift):

    stress = 4

    if sleep_hours < 5:
        stress += 4
    elif sleep_hours < 6:
        stress += 3
    elif sleep_hours < 7:
        stress += 2

    if exercise == 0:
        stress += 3
    elif exercise < 60:
        stress += 2

    if work_hours > 60:
        stress += 3
    elif work_hours > 50:
        stress += 2

    if shift == "Night":
        stress += 2

    if shift == "Rotational":
        stress += 2

    return int(np.clip(stress, 1, 10))


# ============================================================
# DEMOGRAPHIC INFORMATION
# ============================================================

st.header("👤 Demographic Information")

col1, col2, col3 = st.columns(3)

with col1:

    personnel_id = st.text_input("Personnel ID")

    age = st.number_input(
        "Age",
        min_value=18,
        max_value=70
    )

    gender = st.selectbox(
        "Gender",
        df["gender"].unique()
    )

with col2:

    years_of_service = st.number_input(
        "Years of Service",
        0,
        40
    )

    post = st.selectbox(
        "Police Post",
        df["post"].unique()
    )

    posted_city = st.selectbox(
        "Posted City",
        df["posted_city"].unique()
    )

with col3:

    height_cm = st.number_input(
        "Height (cm)",
        120,
        220
    )

    weight_kg = st.number_input(
        "Weight (kg)",
        40,
        150
    )

bmi = calculate_bmi(height_cm, weight_kg)

st.metric("BMI", bmi)

# ============================================================
# CITY DATA EXTRACTION
# ============================================================

city_row = df[df["posted_city"] == posted_city]

pollution_index = float(city_row["pollution_index"].iloc[0])
city_workload_index = float(city_row["city_workload_index"].iloc[0])

st.write("City Pollution Index:", pollution_index)
st.write("City Workload Index:", city_workload_index)

# ============================================================
# VITAL SIGNS
# ============================================================

st.header("❤️ Vital Signs")

col1, col2, col3 = st.columns(3)

with col1:

    bp_level = st.selectbox(
        "Blood Pressure Level",
        ["Low", "Normal", "High"]
    )

    systolic_bp = level_to_value(bp_level, 95, 120, 150)
    diastolic_bp = level_to_value(bp_level, 65, 80, 95)

with col2:

    cholesterol_level = st.selectbox(
        "Cholesterol Level",
        ["Low", "Normal", "High"]
    )

    cholesterol = level_to_value(
        cholesterol_level,
        150,
        200,
        260
    )

with col3:

    diabetes_level = st.selectbox(
        "Blood Sugar Level",
        ["Low", "Normal", "High"]
    )

    fasting_blood_sugar = level_to_value(
        diabetes_level,
        70,
        100,
        130
    )

heart_rate_level = st.selectbox(
    "Heart Rate Level",
    ["Low", "Normal", "High"]
)

heart_rate = level_to_value(
    heart_rate_level,
    55,
    75,
    110
)

# ============================================================
# SPO2 ESTIMATION
# ============================================================

st.header("🫁 Oxygen Level Estimation")

breathing_condition = st.selectbox(
    "Breathing Condition",
    [
        "Normal",
        "Mild Breathlessness",
        "Moderate Breathlessness",
        "Severe Breathlessness"
    ]
)

spo2 = estimate_spo2(breathing_condition)

st.metric("Estimated SpO₂", spo2)

# ============================================================
# LIFESTYLE
# ============================================================

st.header("🏃 Lifestyle")

col1, col2 = st.columns(2)

with col1:

    sleep_hours = st.slider(
        "Sleep Hours Per Day",
        0.0,
        12.0,
        6.0
    )

    exercise_mins_per_week = st.number_input(
        "Exercise Minutes Per Week",
        0,
        600
    )

with col2:

    smoking = st.selectbox(
        "Smoking Habit",
        ["No", "Occasionally", "Regularly"]
    )

    alcohol = st.selectbox(
        "Alcohol Consumption",
        ["No", "Occasionally", "Regularly"]
    )

shift_pattern = st.selectbox(
    "Shift Pattern",
    ["Day", "Night", "Rotational"]
)

working_hours_per_week = st.number_input(
    "Working Hours Per Week",
    10,
    120
)

# ============================================================
# STRESS ESTIMATION
# ============================================================

st.header("🧠 Stress Estimation")

manual_stress = st.checkbox("Enter Stress Level Manually")

if manual_stress:

    stress_level = st.slider(
        "Stress Level",
        1,
        10,
        5
    )

else:

    stress_level = calculate_stress(
        sleep_hours,
        exercise_mins_per_week,
        working_hours_per_week,
        shift_pattern
    )

st.metric("Estimated Stress Level", stress_level)

# ============================================================
# DISEASE AND SUPPORT INFORMATION
# ============================================================

st.header("🩺 Medical & Support Information")

col1, col2, col3 = st.columns(3)

with col1:

    chronic_disease = st.selectbox(
        "Chronic Disease",
        df["chronic_disease"].unique()
    )

with col2:

    healthcare_scheme = st.selectbox(
        "Healthcare Scheme",
        df["healthcare_scheme"].unique()
    )

with col3:

    technological_support = st.selectbox(
        "Technological Support",
        ["Low", "Medium", "High"]
    )

predictive_system_usage = st.selectbox(
    "Use Predictive Monitoring System",
    ["Yes", "No"]
)

# ============================================================
# PREPARE MODEL INPUT
# ============================================================

st.header("📊 Health Risk Prediction")

predict_button = st.button("🔍 Predict Health Risk")

risk_score = None
risk_category = None
suggestions = []

if predict_button:

    # --------------------------------------------------------
    # CREATE INPUT DATAFRAME
    # --------------------------------------------------------

    input_data = pd.DataFrame({

        "personnel_id": [personnel_id],
        "post": [post],
        "posted_city": [posted_city],
        "pollution_index": [pollution_index],
        "city_workload_index": [city_workload_index],
        "age": [age],
        "gender": [gender],
        "years_of_service": [years_of_service],
        "height_cm": [height_cm],
        "weight_kg": [weight_kg],
        "bmi": [bmi],
        "systolic_bp": [systolic_bp],
        "diastolic_bp": [diastolic_bp],
        "heart_rate": [heart_rate],
        "spo2": [spo2],
        "fasting_blood_sugar": [fasting_blood_sugar],
        "cholesterol": [cholesterol],
        "chronic_disease": [chronic_disease],
        "sleep_hours": [sleep_hours],
        "exercise_mins_per_week": [exercise_mins_per_week],
        "smoking": [smoking],
        "alcohol": [alcohol],
        "stress_level": [stress_level],
        "shift_pattern": [shift_pattern],
        "working_hours_per_week": [working_hours_per_week],
        "healthcare_scheme": [healthcare_scheme],
        "technological_support": [technological_support],
        "predictive_system_usage": [predictive_system_usage]

    })

    # --------------------------------------------------------
    # FIX COLUMN MISMATCH WITH TRAINING DATASET
    # --------------------------------------------------------

    for col in df.columns:
        if col not in input_data.columns:
            input_data[col] = df[col].iloc[0]

    input_data = input_data[df.columns]

    # --------------------------------------------------------
    # ENCODE INPUT
    # --------------------------------------------------------

    encoded_input = ct_encoder.transform(input_data)

    # --------------------------------------------------------
    # MODEL PREDICTION
    # --------------------------------------------------------

    try:

        prediction = xgb_model.predict(encoded_input)

        risk_score = float(prediction[0])

    except:

        risk_score = 30

    # --------------------------------------------------------
    # ADDITIONAL RISK ADJUSTMENTS
    # --------------------------------------------------------

    if smoking == "Occasionally":
        risk_score += 5

    if smoking == "Regularly":
        risk_score += 10

    if alcohol == "Occasionally":
        risk_score += 4

    if alcohol == "Regularly":
        risk_score += 8

    if sleep_hours < 5:
        risk_score += 8
    elif sleep_hours < 6:
        risk_score += 5

    if exercise_mins_per_week == 0:
        risk_score += 7
    elif exercise_mins_per_week < 60:
        risk_score += 4

    if bmi >= 30:
        risk_score += 8
    elif bmi >= 25:
        risk_score += 4

    if systolic_bp >= 140:
        risk_score += 6

    if fasting_blood_sugar >= 126:
        risk_score += 6

    if cholesterol >= 240:
        risk_score += 5

    if stress_level >= 7:
        risk_score += 6

    risk_score = max(0, min(100, risk_score))

# ============================================================
# RISK CATEGORY
# ============================================================

    if risk_score < 35:

        risk_category = "🟢 Low Risk"

    elif risk_score < 60:

        risk_category = "🟡 Moderate Risk"

    elif risk_score < 80:

        risk_category = "🟠 High Risk"

    else:

        risk_category = "🔴 Critical Risk"

# ============================================================
# DISPLAY RESULTS
# ============================================================

    st.subheader("📈 Prediction Result")

    col1, col2 = st.columns(2)

    with col1:

        st.metric(
            "Risk Score",
            round(risk_score, 2)
        )

    with col2:

        st.metric(
            "Risk Category",
            risk_category
        )

# ============================================================
# SUGGESTION ENGINE
# ============================================================

    if risk_score >= 80:
        suggestions.append(
            "Critical health risk detected. Immediate medical consultation recommended."
        )

    elif risk_score >= 60:
        suggestions.append(
            "High health risk. Schedule medical examination within one month."
        )

    elif risk_score >= 35:
        suggestions.append(
            "Moderate risk detected. Lifestyle improvements recommended."
        )

    else:
        suggestions.append(
            "Health risk within normal limits. Maintain current lifestyle."
        )

    if systolic_bp >= 140:
        suggestions.append(
            "High blood pressure detected. Monitor BP regularly."
        )

    if fasting_blood_sugar >= 126:
        suggestions.append(
            "Elevated blood sugar level. Diabetes screening recommended."
        )

    if cholesterol >= 240:
        suggestions.append(
            "High cholesterol level detected. Reduce fatty food intake."
        )

    if spo2 < 95:
        suggestions.append(
            "Low oxygen saturation detected. Consider medical evaluation."
        )

    if sleep_hours < 7:
        suggestions.append(
            "Increase sleep duration to 7–8 hours per night."
        )

    if exercise_mins_per_week < 150:
        suggestions.append(
            "Increase physical activity to at least 150 minutes per week."
        )

    if smoking != "No":
        suggestions.append(
            "Smoking significantly increases health risk. Consider quitting."
        )

    if alcohol != "No":
        suggestions.append(
            "Limit alcohol consumption."
        )

    if stress_level >= 7:
        suggestions.append(
            "High stress detected. Practice relaxation or meditation."
        )

    if working_hours_per_week > 60:
        suggestions.append(
            "Excessive working hours may cause burnout. Ensure proper rest."
        )

# ============================================================
# DISPLAY SUGGESTIONS
# ============================================================

    st.subheader("💡 Health Suggestions")

    for s in suggestions:

        st.write("•", s)

# ============================================================
# PDF REPORT GENERATION
# ============================================================

    st.subheader("📄 Download Health Report")

    buffer = io.BytesIO()

    styles = getSampleStyleSheet()

    elements = []

    elements.append(
        Paragraph(
            "Police Personnel Health Risk Report",
            styles["Title"]
        )
    )

    elements.append(Spacer(1, 20))

    report_data = [

        ["Personnel ID", personnel_id],
        ["Age", age],
        ["Gender", gender],
        ["Post", post],
        ["Posted City", posted_city],
        ["BMI", bmi],
        ["Stress Level", stress_level],
        ["Risk Score", round(risk_score, 2)],
        ["Risk Category", risk_category]

    ]

    table = Table(report_data)

    table.setStyle([

        ("GRID", (0,0), (-1,-1), 1, colors.grey),
        ("BACKGROUND", (0,0), (0,-1), colors.lightgrey)

    ])

    elements.append(table)

    elements.append(Spacer(1, 20))

    elements.append(
        Paragraph(
            "Health Recommendations",
            styles["Heading2"]
        )
    )

    for s in suggestions:

        elements.append(
            Paragraph(s, styles["Normal"])
        )

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4
    )

    doc.build(elements)

    pdf = buffer.getvalue()

    buffer.close()

    st.download_button(
        label="Download PDF Report",
        data=pdf,
        file_name="police_health_report.pdf",
        mime="application/pdf"
    )

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.markdown(
"""
**Predictive Healthcare Framework for Police Personnel**

Machine Learning Based Health Risk Prediction System  
Developed using **Streamlit, Python, XGBoost, and Data Analytics**
"""
)
