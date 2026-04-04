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

# --- HELPER ---
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

# --------------------------------------------------------------------------
# --- DEMOGRAPHICS ---
# --------------------------------------------------------------------------
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

# --------------------------------------------------------------------------
# --- REQUIRED CHANGE 1: CHANGE HEADING NAME ---
# --------------------------------------------------------------------------
st.header("🩺 Police personnel using Schemes / System")

health_conditions = st.multiselect(
    "Select schemes/systems or current conditions:",
    ["High BP", "Low BP", "Cholesterol", "Diabetes", "Thyroid", "Heart Disease",
     "Asthma", "MPKAY", "Family Health Scheme", "Dhanwantari", "MJPJAY", "Preventive Camps",
     "Digital Health Records", "Police Hospitals", "None"]
)
current_health_details = ", ".join(health_conditions) if health_conditions else "None"

# --------------------------------------------------------------------------
# --- VITAL SIGNS ---
# --------------------------------------------------------------------------
st.header("❤️ Vital Signs")
bp_level = st.selectbox("BP Level", ["Low", "Medium", "High"])
systolic_bp = get_numeric_from_level(bp_level, 95, 120, 150)
diastolic_bp = get_numeric_from_level(bp_level, 65, 80, 100)

cholesterol_level = st.selectbox("Cholesterol Level", ["Low", "Medium", "High"])
cholesterol = get_numeric_from_level(cholesterol_level, 150, 200, 270)

diabetes_level = st.selectbox("Diabetes Level", ["Low", "Normal", "High"])
fasting_blood_sugar = get_numeric_from_level(diabetes_level, 70, 100, 125)

# SPO2
st.subheader("🫁 Oxygen Saturation (SpO₂) Estimation")
spo2_question = st.radio(
    "How do you currently feel?",
    ["Normal breathing, no fatigue",
     "Slight breathlessness or tiredness",
     "Severe breathlessness or using oxygen support"]
)
spo2 = 98 if spo2_question == "Normal breathing, no fatigue" else (94 if spo2_question == "Slight breathlessness or tiredness" else 90)
spo2_level = "Normal" if spo2 >= 95 else "Low"
st.info(f"Estimated SpO₂ Level: **{spo2_level} ({spo2}%)**")

heart_level = st.selectbox("Heart Rate Level", ["Low", "Normal", "High"])
heart_rate = get_numeric_from_level(heart_level, 55, 80, 110)

# Chronic disease
chronic_disease = st.selectbox("Chronic Disease", df['chronic_disease'].unique())
if chronic_disease == "Other":
    chronic_disease_other = st.text_input("Please specify your chronic disease")
else:
    chronic_disease_other = chronic_disease

# --------------------------------------------------------------------------
# --- REQUIRED CHANGE 2: CHANGE HEADING NAME ---
# --------------------------------------------------------------------------
st.header("🩺 Police Personnel latest Health details/Diseases")

do_exercise = st.radio("Do you exercise?", ["Yes", "No"])
if do_exercise == "Yes":
    exercise_mins_per_week = st.number_input("Exercise minutes per week", min_value=0, max_value=10000, step=5)
    exercise_types = st.multiselect("Select exercise types", ["Swimming","Running","Jogging","Walking","Weight training","Cycling","Aerobics","Yoga"])
else:
    exercise_mins_per_week = 0
    exercise_types = []

# --------------------------------------------------------------------------
# --- REQUIRED CHANGE 3: FULL DIET LOGIC (Veg / Non-Veg / Both) ---
# --------------------------------------------------------------------------
st.subheader("🍽 Diet Details (NEW)")

# New: Breakfast / Lunch / Dinner daily questions
have_breakfast = st.radio("Do you have Breakfast every day?", ["Yes", "No"])
have_lunch = st.radio("Do you have Lunch every day?", ["Yes", "No"])
have_dinner = st.radio("Do you have Dinner every day?", ["Yes", "No"])

# Meal lists (separated by meal and veg/non-veg)
veg_breakfast = [
    "Poha", "Upma", "Idli", "Dosa", "Uttapam", "Sabudana Khichdi",
    "Thepla", "Paratha", "Sprouts Salad", "Fruit Bowl"
]
nonveg_breakfast = [
    "Boiled Eggs", "Omelette", "Egg Bhurji", "Egg Sandwich"
]

veg_lunch = [
    "Chapati", "Dal Rice", "Veg Thali", "Puri Bhaji",
    "Vegetable Khichdi", "Paneer Curry", "Mix Veg Curry"
]
nonveg_lunch = [
    "Chicken Curry", "Chicken Fry", "Fish Curry",
    "Fish Fry", "Egg Curry", "Mutton Curry"
]

veg_dinner = [
    "Chapati", "Veg Thali", "Dal Tadka with Rice", "Khichdi",
    "Paneer Sabji", "Vegetable Soup"
]
nonveg_dinner = [
    "Chicken Curry", "Chicken Soup", "Mutton Curry",
    "Egg Bhurji", "Fish Curry"
]

def get_meal_selection(meal_name, have_meal, veg_items, nonveg_items):
    if have_meal == "Yes":
        pref = st.radio(f"{meal_name} Preference", ["Veg", "Non-Veg", "Both"],
                        key=f"{meal_name}_pref")
        
        if pref == "Veg":
            return st.multiselect(f"Select {meal_name} Items (Veg):", veg_items,
                                  key=f"{meal_name}_items")
        elif pref == "Non-Veg":
            return st.multiselect(f"Select {meal_name} Items (Non-Veg):", nonveg_items,
                                  key=f"{meal_name}_items")
        else:
            return st.multiselect(f"Select {meal_name} Items (Veg + Non-Veg):",
                                  veg_items + nonveg_items,
                                  key=f"{meal_name}_items")
    else:
        return []

breakfast_selected = get_meal_selection("Breakfast", have_breakfast,
                                        veg_breakfast, nonveg_breakfast)

lunch_selected = get_meal_selection("Lunch", have_lunch,
                                    veg_lunch, nonveg_lunch)

dinner_selected = get_meal_selection("Dinner", have_dinner,
                                     veg_dinner, nonveg_dinner)

# maintain compatibility with existing variable names used further down
diet_pref = "Breakfast/Lunch/Dinner logged"
diet_food_selected = breakfast_selected + lunch_selected + dinner_selected
# --------------------------------------------------------------------------
# --- Sleep, smoking, alcohol, tech ---
# --------------------------------------------------------------------------
sleep_hours = st.number_input("Sleep hours per day", min_value=0.0, max_value=24.0, step=0.5)
smoking = st.selectbox("Do you smoke?", ["No", "Occasionally", "Regularly"])
alcohol = st.selectbox("Do you consume alcohol?", ["No", "Occasionally", "Regularly"])
water_intake_liters = st.number_input("Daily Water Intake (Liters)", min_value=0.0, max_value=10.0, step=0.1)

technological_devices = st.multiselect(
    "Technological Devices Used",
    ["Wearable (smartwatch)", "Mobile Health App", "Telehealth Services", "BP Monitor", "Glucometer", "None"]
)

wellness_program = st.radio("Wellness Programs Provided by Department?", ["Yes", "No", "Sometimes"])
healthcare_scheme = st.selectbox("Healthcare Scheme Used", df['healthcare_scheme'].unique())
technological_support = st.selectbox("Use of Technology in Health Monitoring", ["Low", "Medium", "High"])
# --------------------------------------------------------------------------
# --- OCCUPATIONAL & MENTAL HEALTH ---
# --------------------------------------------------------------------------
st.header("💼 Occupational & Mental Health")
shift_pattern = st.selectbox("Shift Pattern", ["Day", "Night", "Rotational"])
working_hours_per_week = st.number_input("Working hours per week", min_value=1, max_value=120)

stress_calc = 5
if sleep_hours < 6: stress_calc += 3
elif sleep_hours < 7: stress_calc += 2
elif sleep_hours < 8: stress_calc += 1
if working_hours_per_week > 60: stress_calc += 3
elif working_hours_per_week > 50: stress_calc += 2
elif working_hours_per_week > 40: stress_calc += 1
if exercise_mins_per_week == 0: stress_calc += 2
elif exercise_mins_per_week < 60: stress_calc += 1
if shift_pattern.lower() in ["night", "rotational"]: stress_calc += 2
auto_stress_level = int(np.clip(stress_calc, 1, 10))

stress_override = st.selectbox("Choose stress level input method", ["Auto-calculated", "Low", "Normal", "High"])
if stress_override == "Auto-calculated":
    stress_level = auto_stress_level
else:
    stress_level = 2 if stress_override=="Low" else (5 if stress_override=="Normal" else 8)

stress_category = "Low" if stress_level <= 3 else ("Normal" if stress_level <= 6 else "High")

st.progress(min(max(stress_level / 10.0, 0.0), 1.0))
st.write(f"Stress Level: {stress_level}/10 — {stress_category}")

mood = st.selectbox("How do you feel today?", ["😊 Happy", "😐 Neutral", "😔 Sad", "😟 Stressed", "😡 Angry"])
mindfulness = st.slider("Minutes of Mindfulness / Meditation Everyday", 0, 60, 0)

# --------------------------------------------------------------------------
# --- PREDICTION AND PDF GENERATION ---
# --------------------------------------------------------------------------
st.markdown("---")

# Prepare breakfast/lunch/dinner text for PDF
breakfast_text = ", ".join(breakfast_selected) if breakfast_selected else ("Skipped" if have_breakfast=="No" else "Not specified")
lunch_text = ", ".join(lunch_selected) if lunch_selected else ("Skipped" if have_lunch=="No" else "Not specified")
dinner_text = ", ".join(dinner_selected) if dinner_selected else ("Skipped" if have_dinner=="No" else "Not specified")

if st.button("Predict My Risk & Prepare Report"):

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
        'chronic_disease':[chronic_disease_other],
        'sleep_hours':[sleep_hours],
        'exercise_mins_per_week':[exercise_mins_per_week],
        'smoking':[smoking],
        'alcohol':[alcohol],
        'stress_level':[stress_level],
        'shift_pattern':[shift_pattern],
        'working_hours_per_week':[working_hours_per_week],
        'healthcare_scheme':[healthcare_scheme],
        'technological_support':[technological_support],
        'predictive_system_usage':["Yes"]
    })

    numeric_cols = ['personnel_id','pollution_index','city_workload_index','age','years_of_service',
                    'height_cm','weight_kg','bmi','systolic_bp','diastolic_bp','heart_rate','spo2',
                    'fasting_blood_sugar','cholesterol','sleep_hours','exercise_mins_per_week',
                    'stress_level','working_hours_per_week']
    for c in numeric_cols:
        input_data[c] = pd.to_numeric(input_data[c], errors='coerce')

    categorical_cols = ['post','posted_city','gender','chronic_disease','smoking','alcohol',
                        'shift_pattern','healthcare_scheme','technological_support','predictive_system_usage']

    input_encoded = safe_transform(ct_encoder, input_data, df, categorical_cols)
    risk_score = float(xgb_model.predict(input_encoded)[0])

    if smoking == "Occasionally": risk_score += 5
    elif smoking == "Regularly": risk_score += 10
    if alcohol == "Occasionally": risk_score += 3
    elif alcohol == "Regularly": risk_score += 8

    risk_category = "✅ Normal" if risk_score < 40 else ("⚠ Borderline" if risk_score < 70 else "❌ High Risk")

    st.subheader("📊 Risk Result")
    st.write(f"**Risk Score:** {risk_score:.1f}")
    st.write(f"**Risk Category:** {risk_category}")

    # ----------------------------------------------------------------------
    # PDF START
    # ----------------------------------------------------------------------
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='CenterTitle', alignment=1, fontSize=14, spaceAfter=8))
    styles.add(ParagraphStyle(name='Small', fontSize=9))
    elements = []

    try:
        logo = Image("—Pngtree—gold police officer badge_7258551.png", width=60, height=60)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1,8))
    except:
        pass

    elements.append(Paragraph("Predictive Healthcare Report", styles['CenterTitle']))
    elements.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", styles['Small']))
    elements.append(Spacer(1,12))

    # DEMOGRAPHICS TABLE
    demo_data = [
        ["Personnel ID", personnel_id],
        ["Age", age],
        ["Gender", gender],
        ["Post", post],
        ["Posted City", posted_city],
        ["Years of Service", years_of_service],
        ["Pollution Index", f"{pollution_index:.2f}"],
        ["City Workload Index", f"{city_workload_index:.2f}"],
        ["BMI", bmi],
        ["Health / Schemes Used", current_health_details]
    ]

    elements.append(Paragraph("Personnel & Demographics", styles['Heading2']))
    elements.append(Table(demo_data, colWidths=[180, 300], style=[('GRID',(0,0),(-1,-1),0.3,colors.grey)]))
    elements.append(Spacer(1,10))

    # VITAL SIGNS
    vitals_data = [
        ["BP Level", bp_level],
        ["Systolic", f"{systolic_bp} mmHg"],
        ["Diastolic", f"{diastolic_bp} mmHg"],
        ["Cholesterol Level", cholesterol_level],
        ["Cholesterol", f"{cholesterol} mg/dL"],
        ["Diabetes Level", diabetes_level],
        ["Fasting Blood Sugar", f"{fasting_blood_sugar} mg/dL"],
        ["SpO₂ Level", spo2_level],
        ["SpO₂ Estimated", f"{spo2}%"],
        ["Heart Rate Level", heart_level],
        ["Heart Rate", f"{heart_rate} bpm"],
        ["Sleep Hours (per day)", f"{sleep_hours}"]
    ]
    elements.append(Paragraph("Vital Signs & Sleep", styles['Heading2']))
    elements.append(Table(vitals_data, colWidths=[180, 300], style=[('GRID',(0,0),(-1,-1),0.3,colors.grey)]))
    elements.append(Spacer(1,10))

    # LIFESTYLE TABLE (including breakfast, lunch & dinner)
    lifestyle_data = [
        ["Breakfast Taken?", have_breakfast],
        ["Breakfast Items", breakfast_text],
        ["Lunch Taken?", have_lunch],
        ["Lunch Items", lunch_text],
        ["Dinner Taken?", have_dinner],
        ["Dinner Items", dinner_text],
        ["Exercise (mins/week)", exercise_mins_per_week],
        ["Exercise Types", ", ".join(exercise_types) if exercise_types else "None"],
        ["Smoking", smoking],
        ["Alcohol", alcohol],
        ["Daily Water Intake (L)", water_intake_liters],
        ["Technological Devices", ", ".join(technological_devices) if technological_devices else "None"],
        ["Wellness Program", wellness_program],
        ["Healthcare Scheme", healthcare_scheme],
        ["Use of Technology", technological_support]
    ]

    elements.append(Paragraph("Lifestyle, Diet & Meals", styles['Heading2']))
    elements.append(
        Table(
            lifestyle_data,
            colWidths=[180, 300],
            style=[('GRID', (0,0), (-1,-1), 0.3, colors.grey)]
        )
    )
    elements.append(Spacer(1, 10))

    # OCCUPATIONAL
    occ_data = [
        ["Shift Pattern", shift_pattern],
        ["Working Hours/week", working_hours_per_week],
        ["Stress Level (1-10)", stress_level],
        ["Stress Category", stress_category],
        ["Mood Today", mood],
        ["Mindfulness (mins/day)", mindfulness]
    ]
    elements.append(Paragraph("Occupational & Mental Health", styles['Heading2']))
    elements.append(
        Table(
            occ_data,
            colWidths=[180, 300],
            style=[('GRID', (0,0), (-1,-1), 0.3, colors.grey)]
        )
    )
    elements.append(Spacer(1, 10))

    # SUGGESTIONS
    suggestion_list = []
    if risk_score >= 70:
        suggestion_list.append("High risk detected — immediate medical follow-up recommended.")
    elif risk_score >= 40:
        suggestion_list.append("Borderline risk — schedule a health check within 1–3 months.")
    else:
        suggestion_list.append("Risk within normal range — maintain routine monitoring.")

    if spo2 < 95:
        suggestion_list.append("Low SpO₂ — consider a proper oxygen saturation check.")
    if systolic_bp >= 140 or diastolic_bp >= 90:
        suggestion_list.append("High BP — regular monitoring recommended.")
    if fasting_blood_sugar >= 125:
        suggestion_list.append("High fasting sugar — follow up for diabetes screening.")
    if cholesterol >= 240:
        suggestion_list.append("High cholesterol — dietary adjustments needed.")
    if stress_level >= 7:
        suggestion_list.append("High stress — consider counseling or relaxation activities.")

    # Meal-based suggestions
    if have_breakfast == "No":
        suggestion_list.append("You are skipping breakfast — this affects metabolism and energy levels.")
    if have_lunch == "No":
        suggestion_list.append("You are skipping lunch — ensure mid-day nutrition.")
    if have_dinner == "No":
        suggestion_list.append("You are skipping dinner — avoid long fasting gaps.")

    suggestion_list.append("Maintain balanced diet, regular exercise, and 7–8 hours sleep.")
    suggestion_list.append("Limit tobacco/alcohol and stay hydrated.")
    suggestion_list.append("Use department health schemes and digital tools regularly.")

    elements.append(Paragraph("Risk Prediction & Suggestions", styles['Heading2']))
    elements.append(Paragraph(f"Risk Score: {risk_score:.1f} — {risk_category}", styles['Normal']))

    for s in suggestion_list:
        elements.append(Paragraph(f"• {s}", styles['Normal']))
        elements.append(Spacer(1, 4))

    elements.append(Spacer(1, 18))
    elements.append(Paragraph("© 2025 Police Health Analytics | Developed for Research", styles['Small']))

    pdf.build(elements)

    buffer.seek(0)
    pdf_bytes = buffer.getvalue()

    st.success("Report prepared — download below.")
    st.download_button(
        label="📥 Download Health Report (PDF)",
        data=pdf_bytes,
        file_name=f"health_report_{int(personnel_id)}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
        mime="application/pdf"
    )

st.markdown("---")
st.caption("© 2025 Police Health Analytics | Developed for Research and Awareness")
