# =====================================================
# Predictive Healthcare Framework for Police Personnel
# Streamlit Application
# PART 1
# =====================================================

import streamlit as st
import pandas as pd
import numpy as np
import joblib
import datetime
import io

from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Predictive Healthcare Framework",
    layout="wide"
)

st.title("🚓 Predictive Healthcare Framework for Police Personnel")

st.markdown(
"""
This system predicts **health risk levels of police personnel**
using **machine learning and lifestyle indicators**.

It evaluates:

• Vital Signs  
• Work Pattern  
• Lifestyle Habits  
• Diet  
• Stress Levels  

Then generates a **Health Risk Score and Suggestions**.
"""
)

# =====================================================
# LOAD MODEL FILES
# =====================================================

@st.cache_resource
def load_model():

    model = joblib.load("xgb_model.pkl")
    encoder = joblib.load("ct_encoder.pkl")

    return model, encoder


xgb_model, ct_encoder = load_model()

# =====================================================
# LOAD DATASET
# =====================================================

@st.cache_data
def load_dataset():

    df = pd.read_csv("police_health_dataset.csv")
    return df


df = load_dataset()

# =====================================================
# HELPER FUNCTIONS
# =====================================================

def get_numeric_from_level(level, low, normal, high):

    if level == "Low":
        return low
    elif level == "Normal":
        return normal
    else:
        return high


def align_columns(X, encoder):

    try:
        cols = encoder.feature_names_in_
        return X[cols]
    except:
        return X


def safe_transform(encoder, X, df_ref, categorical_cols):

    try:
        return encoder.transform(X)

    except Exception:

        X2 = X.copy()

        for col in categorical_cols:

            if col in df_ref.columns:

                known = list(df_ref[col].dropna().unique())

                if known:

                    X2[col] = X2[col].apply(
                        lambda v: v if v in known else known[0]
                    )

        return encoder.transform(X2)


# =====================================================
# SECTION 1 — DEMOGRAPHICS
# =====================================================

st.header("👮 Personnel Demographics")

col1, col2, col3 = st.columns(3)

with col1:

    personnel_id = st.text_input("Personnel ID")

    age = st.number_input(
        "Age",
        min_value=18,
        max_value=100
    )

    gender = st.radio(
        "Gender",
        ["Male", "Female", "Other"]
    )


with col2:

    years_of_service = st.number_input(
        "Years of Service",
        min_value=0,
        max_value=40
    )

    post = st.selectbox(
        "Police Post",
        df["post"].dropna().unique()
    )

    posted_city = st.selectbox(
        "Posted City",
        df["posted_city"].dropna().unique()
    )


with col3:

    height_cm = st.number_input(
        "Height (cm)",
        min_value=120,
        max_value=250
    )

    weight_kg = st.number_input(
        "Weight (kg)",
        min_value=30,
        max_value=200
    )

# =====================================================
# BMI CALCULATION
# =====================================================

if height_cm > 0:
    bmi = round(weight_kg / ((height_cm / 100) ** 2), 1)
else:
    bmi = 0

st.metric("Body Mass Index (BMI)", bmi)

# =====================================================
# SCHEME POLICY
# =====================================================

st.header("🏥 Healthcare Scheme")

schemes = st.multiselect(
    "Select applicable schemes",
    [
        "MPKAY",
        "MJPJAY",
        "ESIC",
        "MPFHS",
        "CGHS",
        "State Medical Reimbursement",
        "Cashless Treatment GR",
        "None",
        "Other"
    ]
)

# =====================================================
# VITAL SIGNS
# =====================================================

st.header("❤️ Vital Signs")

col1, col2, col3 = st.columns(3)

with col1:

    bp_level = st.selectbox(
        "Blood Pressure Level",
        ["Low", "Normal", "High"]
    )

    systolic_bp = get_numeric_from_level(bp_level, 95, 120, 150)
    diastolic_bp = get_numeric_from_level(bp_level, 65, 80, 100)


with col2:

    cholesterol_level = st.selectbox(
        "Cholesterol Level",
        ["Low", "Normal", "High"]
    )

    cholesterol = get_numeric_from_level(
        cholesterol_level,
        150,
        200,
        270
    )


with col3:

    diabetes_level = st.selectbox(
        "Diabetes Level",
        ["Low", "Normal", "High"]
    )

    fasting_blood_sugar = get_numeric_from_level(
        diabetes_level,
        70,
        100,
        125
    )

# =====================================================
# HEART RATE
# =====================================================

heart_level = st.selectbox(
    "Heart Rate Level",
    ["Low", "Normal", "High"]
)

heart_rate = get_numeric_from_level(
    heart_level,
    55,
    80,
    110
)

# =====================================================
# SPO2 ESTIMATION
# =====================================================

st.subheader("🫁 Oxygen Saturation (SpO₂)")

spo2_condition = st.radio(
    "Breathing condition",
    [
        "Normal breathing",
        "Slight breathlessness",
        "Severe breathlessness"
    ]
)

if spo2_condition == "Normal breathing":
    spo2 = 98
elif spo2_condition == "Slight breathlessness":
    spo2 = 94
else:
    spo2 = 90

st.write("Estimated SpO₂:", spo2, "%")

# =====================================================
# LIFESTYLE SECTION
# =====================================================

st.header("🏃 Lifestyle")

col1, col2 = st.columns(2)

with col1:

    sleep_hours = st.slider(
        "Sleep hours per day",
        0.0,
        12.0,
        6.0
    )

    exercise_mins_per_day = st.number_input(
        "Exercise minutes per day",
        min_value=0,
        max_value=300,
        step=5
    )

    exercise_mins_per_week = exercise_mins_per_day * 7


with col2:

    smoking = st.selectbox(
        "Smoking Habit",
        ["No", "Occasionally", "Regularly"]
    )

    alcohol = st.selectbox(
        "Alcohol Consumption",
        ["No", "Occasionally", "Regularly"]
    )

# =====================================================
# WORK PATTERN
# =====================================================

st.header("🕒 Work Pattern")

col1, col2 = st.columns(2)

with col1:

    shift_pattern = st.selectbox(
        "Shift Pattern",
        ["Day", "Night", "Rotational"]
    )

with col2:

    working_hours_per_day = st.number_input(
        "Working hours per day",
        min_value=1,
        max_value=24
    )

    working_hours_per_week = working_hours_per_day * 7


# =====================================================
# DIET SECTION
# =====================================================

st.header("🍽 Diet Pattern")

col1, col2, col3 = st.columns(3)

with col1:

    have_breakfast = st.selectbox(
        "Breakfast",
        ["Yes", "No"]
    )

with col2:

    have_lunch = st.selectbox(
        "Lunch",
        ["Yes", "No"]
    )

with col3:

    have_dinner = st.selectbox(
        "Dinner",
        ["Yes", "No"]
    )
# =====================================================
# STRESS ESTIMATION
# =====================================================

st.header("🧠 Stress Level Estimation")

manual_stress = st.checkbox("Manually Enter Stress Level")

stress_level = None

if manual_stress:

    stress_level = st.slider(
        "Stress Level (1 = Very Low, 10 = Very High)",
        1,
        10,
        5
    )

else:

    stress_calc = 4

    if sleep_hours < 5:
        stress_calc += 4
    elif sleep_hours < 6:
        stress_calc += 3
    elif sleep_hours < 7:
        stress_calc += 2

    if working_hours_per_day > 12:
        stress_calc += 3
    elif working_hours_per_day > 10:
        stress_calc += 2
    elif working_hours_per_day > 8:
        stress_calc += 1

    if exercise_mins_per_day == 0:
        stress_calc += 3
    elif exercise_mins_per_day < 20:
        stress_calc += 2

    if bmi >= 30:
        stress_calc += 2

    if shift_pattern.lower() in ["night", "rotational"]:
        stress_calc += 2

    stress_level = int(np.clip(stress_calc, 1, 10))

st.metric("Estimated Stress Level", stress_level)


# =====================================================
# PREPARE MODEL INPUT
# =====================================================

st.header("📊 Health Risk Prediction")

input_data = pd.DataFrame({

    "age": [age],
    "gender": [gender],
    "years_of_service": [years_of_service],
    "post": [post],
    "posted_city": [posted_city],
    "bmi": [bmi],
    "sleep_hours": [sleep_hours],
    "exercise_mins_per_week": [exercise_mins_per_week],
    "smoking": [smoking],
    "alcohol": [alcohol],
    "working_hours_per_week": [working_hours_per_week],
    "shift_pattern": [shift_pattern],
    "stress_level": [stress_level],
    "systolic_bp": [systolic_bp],
    "diastolic_bp": [diastolic_bp],
    "cholesterol": [cholesterol],
    "fasting_blood_sugar": [fasting_blood_sugar],
    "heart_rate": [heart_rate],
    "spo2": [spo2],
    "breakfast": [have_breakfast],
    "lunch": [have_lunch],
    "dinner": [have_dinner]

})


# =====================================================
# ENCODING
# =====================================================

categorical_cols = [
    "gender",
    "post",
    "posted_city",
    "smoking",
    "alcohol",
    "shift_pattern",
    "breakfast",
    "lunch",
    "dinner"
]

try:

    input_encoded = safe_transform(
        ct_encoder,
        input_data,
        df,
        categorical_cols
    )

except:

    input_encoded = ct_encoder.transform(input_data)


# =====================================================
# PREDICTION
# =====================================================

predict_button = st.button("🔍 Predict Health Risk")

risk_score = None
risk_category = None
suggestion_list = []

if predict_button:

    try:

        model_prediction = float(
            xgb_model.predict(input_encoded)[0]
        )

    except:

        model_prediction = 30

    risk_score = model_prediction


# =====================================================
# RISK ADJUSTMENTS
# =====================================================

    if smoking == "Occasionally":
        risk_score += 6
    elif smoking == "Regularly":
        risk_score += 12

    if alcohol == "Occasionally":
        risk_score += 4
    elif alcohol == "Regularly":
        risk_score += 8

    if sleep_hours < 5:
        risk_score += 10
    elif sleep_hours < 6:
        risk_score += 7
    elif sleep_hours < 7:
        risk_score += 4

    if exercise_mins_per_day == 0:
        risk_score += 10
    elif exercise_mins_per_day < 20:
        risk_score += 5

    if working_hours_per_day > 12:
        risk_score += 10
    elif working_hours_per_day > 10:
        risk_score += 6

    if bmi >= 30:
        risk_score += 8
    elif bmi >= 25:
        risk_score += 4

    if systolic_bp >= 140 or diastolic_bp >= 90:
        risk_score += 8

    if cholesterol >= 240:
        risk_score += 7

    if fasting_blood_sugar >= 125:
        risk_score += 7

    if stress_level >= 7:
        risk_score += 6

    risk_score = max(0, min(100, risk_score))


# =====================================================
# RISK CATEGORY
# =====================================================

    if risk_score < 35:
        risk_category = "🟢 Low Risk"
    elif risk_score < 60:
        risk_category = "🟡 Moderate Risk"
    elif risk_score < 80:
        risk_category = "🟠 High Risk"
    else:
        risk_category = "🔴 Critical Risk"


# =====================================================
# DISPLAY RESULTS
# =====================================================

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


# =====================================================
# SUGGESTION ENGINE
# =====================================================

    if risk_score >= 80:
        suggestion_list.append(
            "Critical risk detected — immediate medical consultation required."
        )

    elif risk_score >= 60:
        suggestion_list.append(
            "High risk — schedule medical check-up within 1 month."
        )

    elif risk_score >= 35:
        suggestion_list.append(
            "Moderate risk — improve lifestyle and monitor health."
        )

    else:
        suggestion_list.append(
            "Risk within safe range — maintain current healthy lifestyle."
        )


    if systolic_bp >= 140 or diastolic_bp >= 90:
        suggestion_list.append(
            "High blood pressure detected — monitor BP regularly."
        )

    if fasting_blood_sugar >= 125:
        suggestion_list.append(
            "High blood sugar — consider diabetes screening."
        )

    if cholesterol >= 240:
        suggestion_list.append(
            "High cholesterol — reduce fatty food intake."
        )

    if spo2 < 95:
        suggestion_list.append(
            "Low oxygen saturation — perform proper SpO₂ test."
        )

    if sleep_hours < 7:
        suggestion_list.append(
            "Sleep less than recommended — aim for 7–8 hours daily."
        )

    if exercise_mins_per_day < 30:
        suggestion_list.append(
            "Increase physical activity — minimum 30 minutes daily."
        )

    if smoking != "No":
        suggestion_list.append(
            "Smoking increases cardiovascular risk — reduce or quit."
        )

    if alcohol != "No":
        suggestion_list.append(
            "Limit alcohol consumption."
        )

    if working_hours_per_day > 10:
        suggestion_list.append(
            "Long working hours may cause burnout — ensure rest breaks."
        )

    if stress_level >= 7:
        suggestion_list.append(
            "High stress detected — consider meditation or counseling."
        )

    if have_breakfast == "No":
        suggestion_list.append(
            "Skipping breakfast affects metabolism."
        )

    if have_lunch == "No":
        suggestion_list.append(
            "Skipping lunch may cause energy imbalance."
        )

    if have_dinner == "No":
        suggestion_list.append(
            "Avoid skipping dinner regularly."
        )

    suggestion_list.append(
        "Maintain balanced diet, hydration, and regular health checkups."
    )


# =====================================================
# DISPLAY SUGGESTIONS
# =====================================================

    st.subheader("💡 Health Suggestions")

    for s in suggestion_list:
        st.write("•", s)


# =====================================================
# PDF REPORT GENERATION
# =====================================================

    st.subheader("📄 Download Health Report")

    buffer = io.BytesIO()

    styles = getSampleStyleSheet()

    story = []

    story.append(Paragraph(
        "Police Health Risk Report",
        styles["Title"]
    ))

    story.append(Spacer(1, 20))

    story.append(Paragraph(
        f"Personnel ID: {personnel_id}",
        styles["Normal"]
    ))

    story.append(Paragraph(
        f"Age: {age}",
        styles["Normal"]
    ))

    story.append(Paragraph(
        f"BMI: {bmi}",
        styles["Normal"]
    ))

    story.append(Paragraph(
        f"Risk Score: {round(risk_score,2)}",
        styles["Normal"]
    ))

    story.append(Paragraph(
        f"Risk Category: {risk_category}",
        styles["Normal"]
    ))

    story.append(Spacer(1, 20))

    story.append(Paragraph(
        "Health Suggestions:",
        styles["Heading2"]
    ))

    for s in suggestion_list:
        story.append(Paragraph(s, styles["Normal"]))

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4
    )

    doc.build(story)

    pdf = buffer.getvalue()
    buffer.close()

    st.download_button(
        label="Download PDF Report",
        data=pdf,
        file_name="health_report.pdf",
        mime="application/pdf"
    )


# =====================================================
# FOOTER
# =====================================================

st.markdown("---")

st.markdown(
"""
Developed for **Police Personnel Health Monitoring System**

Predictive Healthcare Framework using Machine Learning.
"""
)
