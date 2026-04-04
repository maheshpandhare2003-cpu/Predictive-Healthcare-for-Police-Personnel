# App.py (Final Updated Version with Auto SpO₂ Estimation, Diet Options, Sleep in PDF,
# Manual Stress Override, and Suggestions — With ONLY Requested Changes Added)

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

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Predictive Healthcare for Police Personnel",
    page_icon="—Pngtree—gold police officer badge_7258551.png",
    layout="wide"
)

# --- STYLING ---
st.markdown("""
<style>
body { background-color: #f8f9fa; color: #212529; font-family: "Segoe UI", sans-serif; }
h1,h2,h3,h4 { color: #0a2647; }
.stButton > button { background-color:#0a2647; color:#fff; border-radius:8px; padding:0.6em 1.2em; font-weight:600;}
.stButton > button:hover { background-color:#144272; }
div.stDownloadButton > button { background-color:#0a2647; color:#fff; border-radius:8px; padding:0.5em 1em; }
</style>
""", unsafe_allow_html=True)

# --- HEADER ---
col_logo, col_title = st.columns([1, 4])
with col_logo:
    try:
        st.image("—Pngtree—gold police officer badge_7258551.png", width=90)
    except:
        pass
with col_title:
    st.title("Predictive Healthcare for Police Personnel")

# --- LOAD DATA & MODEL ---
df = pd.read_csv("police_health_dataset.csv")
ct_encoder = joblib.load("ct_encoder.pkl")
xgb_model = joblib.load("xgb_model.pkl")

# --- HELPER FUNCTIONS ---
def get_numeric_from_level(level, low, normal, high):
    return low if level == "Low" else normal if level == "Normal" else high

def safe_transform(encoder, X, df_ref, categorical_cols):
    try:
        return encoder.transform(X)
    except Exception:
        X2 = X.copy()
        for col in categorical_cols:
            if col in X2.columns and col in df_ref.columns:
                known = list(df_ref[col].dropna().unique())
                if known:
                    X2[col] = X2[col].apply(lambda v: v if v in known else known[0])
                else:
                    X2[col] = X2[col].fillna("Unknown")
            else:
                X2[col] = "Unknown"
        return encoder.transform(X2)

# -------------------------------------------------------------------
# DEMOGRAPHICS
# -------------------------------------------------------------------

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
    city_row = df[df['posted_city'] == posted_city]

    if not city_row.empty:
        pollution_index = float(city_row['pollution_index'].iloc[0])
        city_workload_index = float(city_row['city_workload_index'].iloc[0])
    else:
        pollution_index = 0.0
        city_workload_index = 0.0

    st.metric(label="City Pollution Index", value=f"{pollution_index:.2f}")
    st.metric(label="City Workload Index", value=f"{city_workload_index:.2f}")

    height_cm = st.number_input("Height (cm)", min_value=120, max_value=250)
    weight_kg = st.number_input("Weight (kg)", min_value=30, max_value=200)

bmi = round(weight_kg / ((height_cm / 100) ** 2), 1) if height_cm > 0 else 0.0
st.text_input("BMI", value=bmi, disabled=True)

# -------------------------------------------------------------------
# POLICE SCHEMES / HEALTH SYSTEMS
# -------------------------------------------------------------------

st.header("🩺 Police personnel using Schemes / System")

health_conditions = st.multiselect(
    "Select schemes/systems or current conditions:",
    ["High BP", "Low BP", "Cholesterol", "Diabetes", "Thyroid", "Heart Disease",
     "Asthma", "MPKAY", "Family Health Scheme", "Dhanwantari", "MJPJAY",
     "Preventive Camps", "Digital Health Records", "Police Hospitals",
     "Other", "None"]
)

# OTHER OPTION ADDED
if "Other" in health_conditions:
    other_scheme = st.text_input("Enter Other Scheme / Condition")
else:
    other_scheme = ""

health_list = [x for x in health_conditions if x != "Other"]

if other_scheme:
    health_list.append(other_scheme)

current_health_details = ", ".join(health_list) if health_list else "None"

# -------------------------------------------------------------------
# VITAL SIGNS
# -------------------------------------------------------------------

st.header("❤️ Vital Signs")

bp_level = st.selectbox("BP Level", ["Low", "Medium", "High"])
systolic_bp = get_numeric_from_level(bp_level, 95, 120, 150)
diastolic_bp = get_numeric_from_level(bp_level, 65, 80, 100)

cholesterol_level = st.selectbox("Cholesterol Level", ["Low", "Medium", "High"])
cholesterol = get_numeric_from_level(cholesterol_level, 150, 200, 270)

diabetes_level = st.selectbox("Diabetes Level", ["Low", "Normal", "High"])
fasting_blood_sugar = get_numeric_from_level(diabetes_level, 70, 100, 125)

st.subheader("🫁 Oxygen Saturation (SpO₂) Estimation")

spo2_question = st.radio(
    "How do you currently feel?",
    [
        "Normal breathing, no fatigue",
        "Slight breathlessness or tiredness",
        "Severe breathlessness or using oxygen support"
    ]
)

spo2 = 98 if spo2_question == "Normal breathing, no fatigue" else (94 if spo2_question == "Slight breathlessness or tiredness" else 90)

spo2_level = "Normal" if spo2 >= 95 else "Low"

st.info(f"Estimated SpO₂ Level: **{spo2_level} ({spo2}%)**")

heart_level = st.selectbox("Heart Rate Level", ["Low", "Normal", "High"])
heart_rate = get_numeric_from_level(heart_level, 55, 80, 110)

chronic_disease = st.selectbox("Chronic Disease", df['chronic_disease'].unique())

if chronic_disease == "Other":
    chronic_disease_other = st.text_input("Please specify your chronic disease")
else:
    chronic_disease_other = chronic_disease

# -------------------------------------------------------------------
# OCCUPATIONAL HEALTH
# -------------------------------------------------------------------

st.header("👮 Occupational Health")

col1, col2, col3 = st.columns(3)

with col1:
    duty_hours = st.slider("Daily Duty Hours", 6, 18, 10)

with col2:
    sleep_hours = st.slider("Sleep Hours", 3, 10, 6)

with col3:
    exercise_freq = st.selectbox("Exercise Frequency", ["None", "Occasional", "Regular"])

# -------------------------------------------------------------------
# LIFESTYLE
# -------------------------------------------------------------------

st.header("🍎 Lifestyle Information")

col1, col2 = st.columns(2)

with col1:
    smoking = st.selectbox("Smoking", ["No", "Yes"])

with col2:
    alcohol = st.selectbox("Alcohol Consumption", ["No", "Occasional", "Regular"])

diet_type = st.selectbox("Diet Type", ["Vegetarian", "Mixed", "High Protein"])

# -------------------------------------------------------------------
# STRESS OVERRIDE
# -------------------------------------------------------------------

st.header("🧠 Stress Level")

stress_level = st.selectbox("Stress Level", ["Low", "Medium", "High"])

# -------------------------------------------------------------------
# PREPARE DATA FOR MODEL
# -------------------------------------------------------------------

input_data = pd.DataFrame({
    "age":[age],
    "gender":[gender],
    "years_of_service":[years_of_service],
    "post":[post],
    "posted_city":[posted_city],
    "pollution_index":[pollution_index],
    "city_workload_index":[city_workload_index],
    "bmi":[bmi],
    "systolic_bp":[systolic_bp],
    "diastolic_bp":[diastolic_bp],
    "cholesterol":[cholesterol],
    "fasting_blood_sugar":[fasting_blood_sugar],
    "spo2":[spo2],
    "heart_rate":[heart_rate],
    "chronic_disease":[chronic_disease_other],
    "duty_hours":[duty_hours],
    "sleep_hours":[sleep_hours],
    "exercise_freq":[exercise_freq],
    "smoking":[smoking],
    "alcohol":[alcohol],
    "diet_type":[diet_type],
    "stress_level":[stress_level]
})

categorical_cols = input_data.select_dtypes(include=['object']).columns

X_transformed = safe_transform(ct_encoder, input_data, df, categorical_cols)

# -------------------------------------------------------------------
# PREDICTION
# -------------------------------------------------------------------

st.header("📊 Health Risk Prediction")

if st.button("Predict Health Risk"):

    prediction = xgb_model.predict(X_transformed)[0]

    if prediction == 0:
        result = "Low Risk"
    elif prediction == 1:
        result = "Moderate Risk"
    else:
        result = "High Risk"

    st.success(f"Predicted Health Risk: **{result}**")

# -------------------------------------------------------------------
# DIET SUGGESTIONS
# -------------------------------------------------------------------

st.header("🥗 Diet Suggestions")

if bmi > 25:
    diet_suggestion = "Reduce sugar and oily food. Increase vegetables and fruits."
elif bmi < 18:
    diet_suggestion = "Increase protein intake such as eggs, milk, and nuts."
else:
    diet_suggestion = "Maintain balanced diet with fruits, vegetables and proteins."

st.info(diet_suggestion)

# -------------------------------------------------------------------
# GENERAL HEALTH SUGGESTIONS
# -------------------------------------------------------------------

st.header("💡 Health Suggestions")

suggestions = []

if duty_hours > 12:
    suggestions.append("Reduce continuous duty hours and take short breaks.")

if sleep_hours < 6:
    suggestions.append("Improve sleep routine to maintain health.")

if smoking == "Yes":
    suggestions.append("Avoid smoking to reduce heart risk.")

if alcohol == "Regular":
    suggestions.append("Limit alcohol consumption.")

if not suggestions:
    suggestions.append("Maintain current healthy lifestyle.")

for s in suggestions:
    st.write("✔", s)

# -------------------------------------------------------------------
# PDF REPORT GENERATION
# -------------------------------------------------------------------

st.header("📄 Download Health Report")

buffer = io.BytesIO()

styles = getSampleStyleSheet()

elements = []

elements.append(Paragraph("Police Personnel Health Report", styles['Title']))
elements.append(Spacer(1,20))

data = [
["Personnel ID", personnel_id],
["Age", age],
["Gender", gender],
["Post", post],
["City", posted_city],
["BMI", bmi],
["Health Schemes / Conditions", current_health_details],
["BP", f"{systolic_bp}/{diastolic_bp}"],
["Cholesterol", cholesterol],
["Blood Sugar", fasting_blood_sugar],
["SpO₂", spo2],
["Heart Rate", heart_rate],
["Chronic Disease", chronic_disease_other],
["Duty Hours", duty_hours],
["Sleep Hours", sleep_hours],
["Exercise", exercise_freq],
["Smoking", smoking],
["Alcohol", alcohol],
["Diet", diet_type],
["Stress Level", stress_level],
]

table = Table(data)

table.setStyle(TableStyle([
("BACKGROUND",(0,0),(0,-1),colors.lightgrey),
("GRID",(0,0),(-1,-1),1,colors.black)
]))

elements.append(table)

elements.append(Spacer(1,20))

elements.append(Paragraph("Diet Suggestion:", styles['Heading3']))
elements.append(Paragraph(diet_suggestion, styles['Normal']))

elements.append(Spacer(1,10))

elements.append(Paragraph("Health Suggestions:", styles['Heading3']))

for s in suggestions:
    elements.append(Paragraph(s, styles['Normal']))

doc = SimpleDocTemplate(buffer, pagesize=A4)
doc.build(elements)

st.download_button(
    label="Download PDF Report",
    data=buffer.getvalue(),
    file_name=f"health_report_{personnel_id}.pdf",
    mime="application/pdf"
)
