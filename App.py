# App.py (Final Updated Version with Auto SpO₂ Estimation, Sleep in PDF, Manual Stress Override, and Suggestions)
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
    st.caption("Personalized Risk Assessment — simplified and enhanced UI")

# --- LOAD DATA & MODEL ---
# NOTE: Ensure these files are present in the same directory as this script.
df = pd.read_csv("police_health_dataset.csv")
ct_encoder = joblib.load("ct_encoder.pkl")
xgb_model = joblib.load("xgb_model.pkl")

# --- HELPER FUNCTIONS ---
def get_numeric_from_level(level, low, normal, high):
    """Convert qualitative level to numeric value for model."""
    return low if level == "Low" else normal if level == "Normal" else high

def safe_transform(encoder, X, df_ref, categorical_cols):
    """Handle unseen categorical levels gracefully."""
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

# --- DEMOGRAPHICS ---
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

# --- CURRENT HEALTH DETAILS ---
st.header("🏥 Police Personnel Current Health / Disease Details")
health_conditions = st.multiselect(
    "Select current health conditions (if any):",
    ["High BP", "Low BP", "Cholesterol", "Diabetes", "Thyroid", "Heart Disease", "Asthma", "None"]
)
current_health_details = ", ".join(health_conditions) if health_conditions else "None"

# --- VITAL SIGNS ---
st.header("❤️ Vital Signs")

# BP issue
bp_issue = st.radio("Do you have a BP issue?", ["No", "Yes"])
if bp_issue == "Yes":
    bp_level = st.selectbox("BP Level", ["Low", "Normal", "High"])
else:
    bp_level = "Normal"
systolic_bp = get_numeric_from_level(bp_level, 95, 120, 150)
diastolic_bp = get_numeric_from_level(bp_level, 65, 80, 100)

# Cholesterol
has_cholesterol = st.radio("Do you have Cholesterol issues?", ["No", "Yes"])
if has_cholesterol == "Yes":
    cholesterol_level = st.selectbox("Cholesterol Level", ["Low", "Medium", "High"])
else:
    cholesterol_level = "Medium"
cholesterol = get_numeric_from_level(cholesterol_level, 150, 200, 270)

# --- AUTO SPO₂ ESTIMATION ---
st.subheader("🫁 Oxygen Saturation (SpO₂) Estimation")
spo2_question = st.radio(
    "How do you currently feel regarding breathing or energy?",
    ["Normal breathing, no fatigue", 
     "Slight breathlessness or tiredness", 
     "Severe breathlessness or using oxygen support"]
)
if spo2_question == "Normal breathing, no fatigue":
    spo2_level = "Normal"
    spo2 = 98
elif spo2_question == "Slight breathlessness or tiredness":
    spo2_level = "Low"
    spo2 = 94
else:
    spo2_level = "Low"
    spo2 = 90

st.info(f"Estimated SpO₂ Level: **{spo2_level} ({spo2}%)** based on your response")

# Sugar level
sugar_level = st.selectbox("Sugar Level ", ["Low", "Normal", "High"])
fasting_blood_sugar = get_numeric_from_level(sugar_level, 70, 100, 125)

# Heart rate
heart_level = st.selectbox("Heart Rate Level", ["Low", "Normal", "High"])
heart_rate = get_numeric_from_level(heart_level, 55, 80, 110)

# --- CHRONIC DISEASE ---
chronic_disease = st.selectbox("Chronic Disease", df['chronic_disease'].unique())
if chronic_disease == "Other":
    chronic_disease_other = st.text_input("Please specify your chronic disease")
else:
    chronic_disease_other = chronic_disease

# --- LIFESTYLE ---
st.header("🏋️ Lifestyle")
do_exercise = st.radio("Do you exercise?", ["Yes", "No"])
if do_exercise == "Yes":
    exercise_mins_per_week = st.number_input("Exercise minutes per week", min_value=0, max_value=10000, step=5)
    exercise_types = st.multiselect("Select exercise types", ["Swimming","Running","Jogging","Walking","Weight training","Cycling","Aerobics","Yoga"])
else:
    exercise_mins_per_week = 0
    exercise_types = []

diet_type = st.selectbox("Diet Type", ["Balanced", "High-calorie", "Low-calorie", "High-sugar", "Custom"])
diet_custom = st.text_input("Describe your diet (optional)") if diet_type == "Custom" else ""

sleep_hours = st.number_input("Sleep hours per day", min_value=0.0, max_value=24.0, step=0.5)

smoking = st.selectbox("Do you smoke?", ["No", "Occasionally", "Regularly"])
alcohol = st.selectbox("Do you consume alcohol?", ["No", "Occasionally", "Regularly"])
water_intake_liters = st.number_input("Daily Water Intake (Liters)", min_value=0.0, max_value=10.0, step=0.1)

technological_devices = st.multiselect("Technological Devices Used", ["Wearable (smartwatch)", "Mobile Health App", "Telehealth Services", "BP Monitor", "Glucometer", "None"])

wellness_program = st.radio("Wellness Programs Provided by Department?", ["Yes", "No", "Sometimes"])
healthcare_scheme = st.selectbox("Healthcare Scheme Used", df['healthcare_scheme'].unique() if 'healthcare_scheme' in df.columns else ["Unknown"])
technological_support = st.selectbox("Use of Technology in Health Monitoring", ["Low", "Medium", "High"])

# --- OCCUPATIONAL & MENTAL HEALTH ---
st.header("💼 Occupational & Mental Health")
shift_pattern = st.selectbox("Shift Pattern", ["Day", "Night", "Rotational"])
working_hours_per_week = st.number_input("Working hours per week", min_value=1, max_value=120)

# Stress calculation (auto)
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

# Present option to override auto stress with Quick Select
st.markdown("**Stress Level Selection**")
stress_override = st.selectbox("Choose stress level input method", ["Auto-calculated", "Low", "Normal", "High"])
if stress_override == "Auto-calculated":
    stress_level = auto_stress_level
else:
    # Map manual selection to representative numeric value
    if stress_override == "Low":
        stress_level = 2
    elif stress_override == "Normal":
        stress_level = 5
    else:  # High
        stress_level = 8

if stress_level <= 3:
    stress_category = "Low"
elif stress_level <= 6:
    stress_category = "Normal"
else:
    stress_category = "High"

# Show a progress bar (visual) and text
st.progress(min(max(stress_level / 10.0, 0.0), 1.0))
st.write(f"Stress Level: {stress_level}/10 — {stress_category}")

mood = st.selectbox("How do you feel today?", ["😊 Happy", "😐 Neutral", "😔 Sad", "😟 Stressed", "😡 Angry"])
mindfulness = st.slider("Minutes of Mindfulness / Meditation Everyday", 0, 60, 0)

# --- PREDICTION ---
st.markdown("---")
if st.button("Predict My Risk & Download Report"):
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
        'chronic_disease':[chronic_disease_other if chronic_disease_other else chronic_disease],
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

    # Encode safely
    input_encoded = safe_transform(ct_encoder, input_data, df, categorical_cols)
    # Model prediction
    risk_score = float(xgb_model.predict(input_encoded)[0])

    # Minor heuristic adjustments
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

    st.subheader("📊 Risk Result")
    st.write(f"**Risk Score:** {risk_score:.1f}")
    st.write(f"**Risk Category:** {risk_category}")

    # --- PDF REPORT ---
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
        ["BMI", bmi]
    ]
    elements.append(Paragraph("Personnel & Demographics", styles['Heading2']))
    elements.append(Table(demo_data, colWidths=[180, 300], style=[('GRID',(0,0),(-1,-1),0.3,colors.grey), ('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    elements.append(Spacer(1,10))

    # VITALS
    vitals_data = [
        ["BP Issue", bp_issue],
        ["BP Level", bp_level],
        ["Systolic", f"{systolic_bp} mmHg"],
        ["Diastolic", f"{diastolic_bp} mmHg"],
        ["Cholesterol Level", cholesterol_level],
        ["Cholesterol", f"{cholesterol} mg/dL"],
        ["SpO₂ Level", spo2_level],
        ["SpO₂ Estimated", f"{spo2}%"],
        ["Sugar Level", sugar_level],
        ["Heart Rate Level", heart_level],
        ["Heart Rate", f"{heart_rate} bpm"],
        ["Sleep Hours (per day)", f"{sleep_hours}"]
    ]
    elements.append(Paragraph("Vital Signs & Sleep", styles['Heading2']))
    elements.append(Table(vitals_data, colWidths=[180, 300], style=[('GRID',(0,0),(-1,-1),0.3,colors.grey), ('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    elements.append(Spacer(1,10))

    # LIFESTYLE
    lifestyle_data = [
        ["Exercise", do_exercise],
        ["Exercise Minutes/Week", exercise_mins_per_week],
        ["Exercise Types", ", ".join(exercise_types) if exercise_types else "None"],
        ["Diet Type", diet_type if diet_type != "Custom" else f"Custom: {diet_custom}"],
        ["Smoking", smoking],
        ["Alcohol", alcohol],
        ["Water Intake (L)", water_intake_liters],
        ["Technological Devices", ", ".join(technological_devices) if technological_devices else "None"],
        ["Healthcare Scheme", healthcare_scheme],
        ["Tech Support (Dept.)", technological_support],
        ["Wellness Program", wellness_program]
    ]
    elements.append(Paragraph("Lifestyle, Diet & Technology", styles['Heading2']))
    elements.append(Table(lifestyle_data, colWidths=[180, 300], style=[('GRID',(0,0),(-1,-1),0.3,colors.grey), ('VALIGN',(0,0),(-1,-1),'TOP')]))
    elements.append(Spacer(1,10))

    # OCCUPATIONAL
    occ_data = [
        ["Shift Pattern", shift_pattern],
        ["Working Hours/Week", working_hours_per_week],
        ["Stress Level (1–10)", stress_level],
        ["Stress Category", stress_category],
        ["Mood", mood],
        ["Mindfulness (mins/day)", mindfulness],
        ["Current Health Details", current_health_details]
    ]
    elements.append(Paragraph("Occupational & Health Summary", styles['Heading2']))
    elements.append(Table(occ_data, colWidths=[180, 300], style=[('GRID',(0,0),(-1,-1),0.3,colors.grey), ('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    elements.append(Spacer(1,10))

    # RISK RESULT
    elements.append(Paragraph("Risk Assessment", styles['Heading2']))
    rc_style = ParagraphStyle('rc', fontSize=11, textColor=colors.green if risk_category=="✅ Normal" else (colors.orange if risk_category=="⚠ Borderline" else colors.red))
    elements.append(Paragraph(f"Risk Category: {risk_category}", rc_style))
    elements.append(Paragraph(f"Risk Score: {risk_score:.1f}", styles['Normal']))
    elements.append(Spacer(1,12))

    # SUGGESTIONS / RECOMMENDATIONS (tailored)
    elements.append(Paragraph("Suggestions & Recommendations", styles['Heading2']))
    suggestions = []

    # General suggestions based on risk category
    if risk_category == "✅ Normal":
        suggestions.append("Your current risk score is in the normal range. Continue with your healthy habits and periodic check-ups.")
    elif risk_category == "⚠ Borderline":
        suggestions.append("Borderline risk detected — consider lifestyle adjustments, schedule a medical check-up, and monitor key vitals regularly.")
    else:
        suggestions.append("High risk detected — seek medical evaluation promptly, review medications (if any), and follow a structured health program recommended by a clinician.")

    # Sleep-related suggestions
    if sleep_hours < 6:
        suggestions.append("Increase sleep duration to 7–8 hours per night to support recovery and reduce stress.")
    elif sleep_hours > 9:
        suggestions.append("Very long sleep may indicate fatigue or underlying issues; discuss with a health professional if persistent.")

    # BMI suggestions
    if bmi >= 25 and bmi < 30:
        suggestions.append("BMI indicates overweight — consider a balanced calorie-controlled diet and regular exercise.")
    elif bmi >= 30:
        suggestions.append("BMI indicates obesity — consult a clinician or dietitian for a structured weight management plan.")

    # Exercise suggestions
    if exercise_mins_per_week < 150:
        suggestions.append("Aim for at least 150 minutes of moderate aerobic exercise per week, or 75 minutes of vigorous activity, plus strength training twice weekly.")
    else:
        suggestions.append("Good exercise consistency — maintain and diversify workouts (cardio + strength + flexibility).")

    # Smoking & alcohol suggestions
    if smoking != "No":
        suggestions.append("Reducing or quitting smoking will significantly lower cardiovascular and respiratory risk. Seek support programs if needed.")
    if alcohol == "Regularly":
        suggestions.append("Consider reducing alcohol intake; consult services offering counseling or behavior change support if needed.")

    # SpO2 and breathing
    if spo2 < 95:
        suggestions.append("Your estimated SpO₂ is lower than typical. If you experience persistent breathlessness or low readings, seek prompt medical attention.")

    # Stress suggestions
    if stress_category == "High":
        suggestions.append("High stress levels noted. Consider stress-management strategies: regular mindfulness, short breaks during shift, counseling support, and better sleep hygiene.")

    # Technology & monitoring
    suggestions.append("Use wearable devices or periodic monitoring (BP monitor, glucometer) for trends rather than single readings. Share concerning patterns with your healthcare provider.")

    # Add suggestions to PDF (each as a bullet-like paragraph)
    for s in suggestions:
        elements.append(Paragraph(f"• {s}", styles['Normal']))
        elements.append(Spacer(1,4))

    elements.append(Spacer(1,12))

    # Closing note
    elements.append(Paragraph("Note: This report is a screening and educational tool. It does not replace professional medical diagnosis. Please consult licensed healthcare professionals for personalized advice.", styles['Small']))

    pdf.build(elements)
    buffer.seek(0)
    pdf_bytes = buffer.getvalue()

    st.download_button(
        label="📥 Download Full PDF Report",
        data=pdf_bytes,
        file_name=f"police_health_report_{personnel_id}.pdf",
        mime="application/pdf"
    )

# --- FOOTER ---
st.markdown("---")
st.caption("© 2025 Police Health Analytics | Developed for Research and Awareness")
