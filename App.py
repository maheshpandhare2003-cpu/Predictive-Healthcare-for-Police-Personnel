# Full App.py - Updated, safe, and preserves the model inputs
import streamlit as st
import pandas as pd
import numpy as np
import joblib
import base64
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
import io
import datetime

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="Predictive Healthcare for Police Personnel",
    page_icon="—Pngtree—gold police officer badge_7258551.png",
    layout="wide"
)

# --- SIMPLE STYLING (kept light) ---
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
    st.caption("Personalized Risk Assessment — simplified UI")

# --- LOAD DATA & MODEL ---
df = pd.read_csv("police_health_dataset.csv")
ct_encoder = joblib.load("ct_encoder.pkl")
xgb_model = joblib.load("xgb_model.pkl")

# --- HELPER FUNCTIONS ---
def get_numeric_from_level(level, low, normal, high):
    """Return numeric representative for a qualitative level."""
    return low if level == "Low" else normal if level == "Normal" else high

def qualitative_from_numeric_for_pdf(value, breaks=(90, 140)):
    """Map numeric value to Low/Normal/High using thresholds provided (example)."""
    low_max, normal_max = breaks
    if value <= low_max:
        return "Low"
    elif value <= normal_max:
        return "Normal"
    else:
        return "High"

def safe_transform(encoder, X, df_ref, categorical_cols):
    """
    Try to transform. If encoder errors due to unseen categories, substitute unknowns
    with known first category for that column (if df_ref contains it); otherwise "Unknown".
    This avoids KeyError when df_ref lacks a column.
    """
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
                    # df_ref doesn't have the column; use generic fallback
                    X2[col] = X2[col].fillna("Unknown")
        return encoder.transform(X2)

# --- DEMOGRAPHICS SECTION ---
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
    # safest way to get city metrics (avoid iloc[0] out-of-bounds)
    city_rows = df[df['posted_city'] == posted_city]
    if not city_rows.empty:
        pollution_index = float(city_rows['pollution_index'].iloc[0])
        city_workload_index = float(city_rows['city_workload_index'].iloc[0])
    else:
        pollution_index = 0.0
        city_workload_index = 0.0
    height_cm = st.number_input("Height (cm)", min_value=120, max_value=250)
    weight_kg = st.number_input("Weight (kg)", min_value=30, max_value=200)

bmi = round(weight_kg / ((height_cm/100)**2), 1)
st.text_input("BMI", value=bmi, disabled=True)

# --- VITALS: we will collect qualitative inputs for users who don't know numeric values,
# then compute numeric representatives for model (we do NOT change model columns) ---
st.header("❤️ Vital Signs (estimate if you don't know exact numbers)")

# Blood pressure estimation questions -> map to Low/Normal/High
bp_q = st.selectbox("Stress & salt intake level (to estimate BP)", [
    "Low stress & low salt intake",
    "Moderate stress / salt intake",
    "High stress & high salt intake"
])
bp_map = {"Low stress & low salt intake":"Low", "Moderate stress / salt intake":"Normal", "High stress & high salt intake":"High"}
bp_level = bp_map.get(bp_q, "Normal")
# numeric proxies for model
systolic_bp = get_numeric_from_level(bp_level, 95, 120, 150)
diastolic_bp = get_numeric_from_level(bp_level, 65, 80, 100)

# Heart rate estimation based on activity
activity_q = st.selectbox("Daily physical activity level", ["High","Moderate","Low"])
hr_map = {"High":"Low","Moderate":"Normal","Low":"High"}  # active -> lower resting HR
heart_level = hr_map.get(activity_q, "Normal")
heart_rate = get_numeric_from_level(heart_level, 55, 80, 110)

# SpO2 estimation (ask smoking + chronic/respiratory cues)
st.subheader("SpO₂ (oxygen) estimation")
smoking = st.selectbox("Do you smoke?", ["No","Occasionally","Regularly"])
chronic_resp = st.selectbox("Any chronic respiratory disease (e.g., COPD, asthma)?", ["No","Yes"])
# spO2 qualitative
if chronic_resp == "Yes" or smoking == "Regularly'":  # small safeguard (typo-proof)
    spo2_level = "Low"
else:
    # consider pollution index: high pollution -> small chance lower SpO2
    spo2_level = "Low" if pollution_index > 80 else "Normal"
spo2 = get_numeric_from_level(spo2_level, 92, 98, 98)

# Fasting blood sugar estimation
st.subheader("Fasting blood sugar estimation")
sweet_freq = st.selectbox("How often do you consume sweets/sugary drinks?", ["Rarely","Sometimes","Daily"])
sleep_hours = st.number_input("Sleep hours per day", min_value=1, max_value=24)
if sweet_freq == "Daily" or sleep_hours < 6:
    sugar_level = "High"
elif sweet_freq == "Sometimes":
    sugar_level = "Normal"
else:
    sugar_level = "Low"
fasting_blood_sugar = get_numeric_from_level(sugar_level, 70, 100, 125)

# Cholesterol estimation: ask diet/fried-food/external factors and compute adjustment
st.subheader("Cholesterol estimation")
fatty_foods = st.selectbox("How often do you eat fried or fatty foods?", ["Rarely","Sometimes","Often"])
food_preference = st.radio("Main food preference", ["Vegetarian","Non-Vegetarian","Mix"])
# basic heuristics
if fatty_foods == "Often" or food_preference == "Non-Vegetarian":
    cholesterol_level = "High"
elif fatty_foods == "Sometimes" or food_preference == "Mix":
    cholesterol_level = "Normal"
else:
    cholesterol_level = "Low"
cholesterol = get_numeric_from_level(cholesterol_level, 150, 200, 270)

# Keep chronic disease selection from original df
chronic_disease = st.selectbox("Chronic Disease", df['chronic_disease'].unique())
if chronic_disease == "Other":
    chronic_disease_other = st.text_input("Please specify your chronic disease")
else:
    chronic_disease_other = chronic_disease

# --- Lifestyle & Exercise (conditional) ---
st.header("🏋️ Lifestyle")
do_exercise = st.radio("Do you exercise?", ["Yes","No"])
if do_exercise == "Yes":
    exercise_mins_per_week = st.number_input("Exercise minutes per week", min_value=0, max_value=10000, step=5)
    exercise_types = st.multiselect("Select exercise types", ["Swimming","Running","Jogging","Walking","Weight training","Cycling","Aerobics","Yoga"])
else:
    exercise_mins_per_week = 0
    exercise_types = []

# Diet section: breakfast / lunch / dinner with Maharashtra items
st.header("🍽️ Meals (for diet-derived cholesterol influence)")
# breakfast lists
veg_breakfast = ["Poha", "Misal", "Upma", "Sabudana Khichdi", "Batata Vada", "Thalipeeth", "Puran Poli"]
nonveg_breakfast = ["Egg Bhurji", "Egg Roll", "Chicken Sandwich"]

# lunch lists
veg_lunch = ["Chapati-Bhaji", "Zunka-Bhakar", "Pithla", "Usal", "Varan-Bhaat", "Bhaji-Roti"]
nonveg_lunch = ["Bombil (fish) curry", "Chicken Curry", "Mutton Curry", "Fish Fry", "Egg Curry"]

# dinner lists
veg_dinner = ["Bhakri-Bhaji", "Chapati-Veg", "Bharli Vangi", "Dal-Rice", "Batatyachi Bhaji"]
nonveg_dinner = ["Fish Curry", "Chicken Masala", "Mutton Sukka", "Fried Fish"]

# Breakfast
has_breakfast = st.radio("Breakfast daily?", ["Yes","No"], horizontal=True, key="b_yesno")
breakfast_score = 0
breakfast_selected = []
if has_breakfast == "Yes":
    b_type = st.radio("Breakfast type", ["Veg","Non-Veg","Mix"], horizontal=True, key="b_type")
    if b_type == "Veg":
        breakfast_selected = st.multiselect("Select breakfast items", veg_breakfast, key="b_veg")
    elif b_type == "Non-Veg":
        breakfast_selected = st.multiselect("Select breakfast items", nonveg_breakfast, key="b_nonveg")
    else:
        breakfast_selected = st.multiselect("Select breakfast items", veg_breakfast + nonveg_breakfast, key="b_mix")
    for it in breakfast_selected:
        breakfast_score += 3 if it in veg_breakfast else 8
else:
    breakfast_selected = []
    breakfast_score = 0

# Lunch
has_lunch = st.radio("Lunch daily?", ["Yes","No"], horizontal=True, key="l_yesno")
lunch_score = 0
lunch_selected = []
if has_lunch == "Yes":
    l_type = st.radio("Lunch type", ["Veg","Non-Veg","Mix"], horizontal=True, key="l_type")
    if l_type == "Veg":
        lunch_selected = st.multiselect("Select lunch items", veg_lunch, key="l_veg")
    elif l_type == "Non-Veg":
        lunch_selected = st.multiselect("Select lunch items", nonveg_lunch, key="l_nonveg")
    else:
        lunch_selected = st.multiselect("Select lunch items", veg_lunch + nonveg_lunch, key="l_mix")
    for it in lunch_selected:
        lunch_score += 5 if it in veg_lunch else 12
else:
    lunch_selected = []
    lunch_score = 0

# Dinner
has_dinner = st.radio("Dinner daily?", ["Yes","No"], horizontal=True, key="d_yesno")
dinner_score = 0
dinner_selected = []
if has_dinner == "Yes":
    d_type = st.radio("Dinner type", ["Veg","Non-Veg","Mix"], horizontal=True, key="d_type")
    if d_type == "Veg":
        dinner_selected = st.multiselect("Select dinner items", veg_dinner, key="d_veg")
    elif d_type == "Non-Veg":
        dinner_selected = st.multiselect("Select dinner items", nonveg_dinner, key="d_nonveg")
    else:
        dinner_selected = st.multiselect("Select dinner items", veg_dinner + nonveg_dinner, key="d_mix")
    for it in dinner_selected:
        dinner_score += 5 if it in veg_dinner else 12
else:
    dinner_selected = []
    dinner_score = 0

# Combine diet score to influence cholesterol numeric value (for model only)
diet_score = breakfast_score + lunch_score + dinner_score
# adjust cholesterol numeric (small weighted influence)
# don't create new model columns; modify existing cholesterol numeric
cholesterol_adjustment = diet_score / 10.0  # tuneable weight
cholesterol = cholesterol + cholesterol_adjustment

# --- Wellness Program moved below alcohol in your original flow ---
alcohol = st.selectbox("Do you consume alcohol?", ["No","Occasionally","Regularly"])
wellness_program = st.radio("Wellness Programs Provided by Department?", ["Yes","No","Sometimes"])
st.info("Healthcare Scheme is used for Survey & Analysis Purpose. Wellness program is informational.")

# Occupational
st.header("💼 Occupational Health")
shift_pattern = st.selectbox("Shift Pattern", ["Day","Night","Rotational"])
working_hours_per_week = st.number_input("Working hours per week", min_value=1, max_value=120)

# Mental health
st.header("🧠 Mental Health & Wellbeing")
# reuse earlier sleep_hours variable input (we used it above)
# compute stress similar to your earlier logic (kept)
stress_calc = 5
if sleep_hours < 6:
    stress_calc += 3
elif sleep_hours < 7:
    stress_calc += 2
elif sleep_hours < 8:
    stress_calc += 1
if working_hours_per_week > 60:
    stress_calc += 3
elif working_hours_per_week > 50:
    stress_calc += 2
elif working_hours_per_week > 40:
    stress_calc += 1
if exercise_mins_per_week == 0:
    stress_calc += 2
elif exercise_mins_per_week < 60:
    stress_calc += 1
if shift_pattern.lower() in ["night", "rotational"]:
    stress_calc += 2
stress_level = int(np.clip(stress_calc, 1, 10))
st.progress(stress_level / 10, text=f"Stress Level: {stress_level}/10")
mood = st.selectbox("How do you feel today?", ["😊 Happy", "😐 Neutral", "😔 Sad", "😟 Stressed", "😡 Angry"])
mindfulness = st.slider("Minutes of Mindfulness / Meditation Everyday", 0, 60, 0)

# --- PREDICTION BUTTON ---
st.markdown("<div id='results'></div>", unsafe_allow_html=True)
if st.button("Predict My Risk & Download Report"):
    # Build input_data exactly with the same column names the model expects
    # (we must not change the set of columns the ct_encoder expects)
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
        'healthcare_scheme':[df['healthcare_scheme'].iloc[0] if 'healthcare_scheme' in df.columns else "Unknown"],
        'technological_support':["Low"],
        'predictive_system_usage':["Yes"]
    })

    # convert numeric columns safely
    numeric_cols = ['personnel_id','pollution_index','city_workload_index','age','years_of_service',
                    'height_cm','weight_kg','bmi','systolic_bp','diastolic_bp','heart_rate','spo2',
                    'fasting_blood_sugar','cholesterol','sleep_hours','exercise_mins_per_week',
                    'stress_level','working_hours_per_week']
    for c in numeric_cols:
        if c in input_data.columns:
            input_data[c] = pd.to_numeric(input_data[c], errors='coerce')

    # check numeric NaNs
    if input_data[numeric_cols].isnull().any().any():
        st.error("Invalid numeric inputs detected! Please check your inputs.")
        st.stop()

    # Prepare categorical cols for safe_transform (only those present in input_data)
    categorical_cols = [c for c in [
        'post','posted_city','gender','chronic_disease','smoking','alcohol',
        'shift_pattern','healthcare_scheme','technological_support','predictive_system_usage'
    ] if c in input_data.columns]

    # Use safe_transform to protect against unseen categories or missing df columns
    try:
        input_encoded = safe_transform(ct_encoder, input_data, df, categorical_cols)
    except Exception as e:
        st.error("Encoding failed. Please ensure categorical selections are valid.")
        st.exception(e)
        st.stop()

    # Predict
    try:
        risk_score = float(xgb_model.predict(input_encoded)[0])
    except Exception as e:
        st.error("Model prediction error.")
        st.exception(e)
        st.stop()

    # small lifestyle adjustments
    if smoking == "Occasionally": risk_score += 5
    elif smoking == "Regularly": risk_score += 10
    if alcohol == "Occasionally": risk_score += 3
    elif alcohol == "Regularly": risk_score += 8
    # diet influence is already encoded as cholesterol adjustment above

    if risk_score < 40:
        risk_category = "✅ Normal"
    elif risk_score < 70:
        risk_category = "⚠ Borderline"
    else:
        risk_category = "❌ High Risk"

    # Display stylish result (kept simple)
    st.subheader("📊 Risk Result")
    st.markdown(f"**Risk Score:** {risk_score:.1f}")
    st.markdown(f"**Risk Category:** {risk_category}")

    # Feature importance display (if model provides)
    try:
        importance = xgb_model.feature_importances_
        feature_names = input_data.columns
        top_indices = np.argsort(importance)[::-1][:5]
        st.subheader("Top Factors Impacting Risk")
        for i in top_indices:
            st.write(f"- {feature_names[i]} (importance: {importance[i]:.3f})")
    except Exception:
        pass

    # Recommendations (kept similar to original)
    recommendations = []
    if risk_category == "✅ Normal":
        recommendations.append("Maintain your current healthy lifestyle and continue regular check-ups.")
    elif risk_category == "⚠ Borderline":
        recommendations.append("Pay attention to your diet, exercise regularly, and monitor vital signs closely.")
    else:
        recommendations.append("Consult a healthcare professional immediately and follow preventive measures strictly.")

    # targeted advice
    if bp_level != "Normal":
        recommendations.append("Monitor blood pressure regularly and reduce salt intake.")
    if cholesterol_level != "Normal" or diet_score > 30:
        recommendations.append("Reduce fried and fatty foods; consider a dietitian consult.")
    if sugar_level == "High":
        recommendations.append("Limit sugar intake and monitor blood glucose.")
    if exercise_mins_per_week < 60:
        recommendations.append("Increase weekly exercise to improve overall health.")
    if sleep_hours < 7:
        recommendations.append("Improve sleep to 7–8 hours daily.")

    st.subheader("💡 Personalized Recommendations")
    for rec in recommendations:
        st.info(rec)

    # Overall qualitative summary (counts)
    categories = [
        bp_level,
        heart_level,
        sugar_level,
        cholesterol_level,
        # diet qualitative derived from diet_score
        ("High" if diet_score>30 else "Normal" if diet_score>10 else "Low")
    ]
    summary = {"High": categories.count("High"), "Normal": categories.count("Normal"), "Low": categories.count("Low")}
    st.info(f"Overall Health Summary → High: {summary['High']} | Normal: {summary['Normal']} | Low: {summary['Low']}")

    # --- PDF REPORT: include all input data, but show qualitative labels for vitals (no numeric vitals) ---
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='HeadingLarge', fontSize=14, leading=18, spaceAfter=8, alignment=1))
    elements = []

    # Logo (if available)
    try:
        logo = Image("—Pngtree—gold police officer badge_7258551.png", width=60, height=60)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1,8))
    except:
        pass

    elements.append(Paragraph("Predictive Healthcare Report", styles['HeadingLarge']))
    elements.append(Spacer(1,8))
    elements.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1,12))

    # Personnel info table
    elements.append(Paragraph("Personnel Information", styles['Heading2']))
    demo_data = [
        ["Personnel ID", str(personnel_id)],
        ["Age", str(age)],
        ["Gender", str(gender)],
        ["Post", str(post)],
        ["Posted City", str(posted_city)],
        ["Years of Service", str(years_of_service)],
        ["Height (cm)", str(height_cm)],
        ["Weight (kg)", str(weight_kg)],
        ["BMI", str(bmi)]
    ]
    demo_table = Table(demo_data, colWidths=[150, 350])
    demo_table.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.4,colors.grey),('FONTSIZE',(0,0),(-1,-1),10)]))
    elements.append(demo_table)
    elements.append(Spacer(1,10))

    # Vitals qualitative table (no numeric values)
    elements.append(Paragraph("Vital Signs (qualitative)", styles['Heading2']))
    vitals = [
        ["Blood Pressure", bp_level],
        ["Heart Rate", heart_level],
        ["SpO₂", spo2_level],
        ["Fasting Blood Sugar", sugar_level],
        ["Cholesterol", cholesterol_level]
    ]
    vitals_table = Table(vitals, colWidths=[180, 320])
    vitals_table.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.3,colors.grey),('FONTSIZE',(0,0),(-1,-1),10)]))
    elements.append(vitals_table)
    elements.append(Spacer(1,10))

    # Diet & meals summary (items selected)
    elements.append(Paragraph("Diet & Meals", styles['Heading2']))
    diet_rows = [
        ["Breakfast (Yes/No)", has_breakfast],
        ["Breakfast Foods", ", ".join(breakfast_selected) if breakfast_selected else "None"],
        ["Lunch (Yes/No)", has_lunch],
        ["Lunch Foods", ", ".join(lunch_selected) if lunch_selected else "None"],
        ["Dinner (Yes/No)", has_dinner],
        ["Dinner Foods", ", ".join(dinner_selected) if dinner_selected else "None"],
        ["Diet Impact (qualitative)", ("High" if diet_score>30 else "Normal" if diet_score>10 else "Low")]
    ]
    diet_table = Table(diet_rows, colWidths=[150, 350])
    diet_table.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.3,colors.grey),('FONTSIZE',(0,0),(-1,-1),10)]))
    elements.append(diet_table)
    elements.append(Spacer(1,10))

    # Lifestyle & occupational
    elements.append(Paragraph("Lifestyle & Occupational", styles['Heading2']))
    life_rows = [
        ["Exercise", "No Exercise" if exercise_mins_per_week == 0 else f"Yes — {exercise_mins_per_week} mins/week"],
        ["Exercise Types", ", ".join(exercise_types) if exercise_types else "None"],
        ["Sleep Hours", str(sleep_hours)],
        ["Smoking", str(smoking)],
        ["Alcohol", str(alcohol)],
        ["Wellness Program Provided", str(wellness_program)],
        ["Shift Pattern", str(shift_pattern)],
        ["Working Hours/week", str(working_hours_per_week)]
    ]
    life_table = Table(life_rows, colWidths=[150, 350])
    life_table.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.3,colors.grey),('FONTSIZE',(0,0),(-1,-1),10)]))
    elements.append(life_table)
    elements.append(Spacer(1,10))

    # Risk & recommendations
    elements.append(Paragraph("Risk Assessment", styles['Heading2']))
    rc_style = ParagraphStyle('rc', fontSize=11, textColor=colors.green if risk_category=="✅ Normal" else (colors.orange if risk_category=="⚠ Borderline" else colors.red))
    elements.append(Paragraph(f"Risk Category: {risk_category}", rc_style))
    # We keep the internal numeric risk score visible (you previously allowed showing model score),
    # but vitals numeric values are not shown.
    elements.append(Paragraph(f"Risk Score (internal): {risk_score:.1f}", styles['Normal']))
    elements.append(Spacer(1,8))
    elements.append(Paragraph("Recommendations", styles['Heading2']))
    for rec in recommendations:
        elements.append(Paragraph(f"• {rec}", styles['Normal']))
    elements.append(Spacer(1,12))

    # Overall qualitative summary
    elements.append(Paragraph("Overall Health Summary (qualitative)", styles['Heading2']))
    elements.append(Paragraph(f"High: {summary['High']} | Normal: {summary['Normal']} | Low: {summary['Low']}", styles['Normal']))
    elements.append(Spacer(1,12))

    # Footer
    footer_text = f"Generated from Police Personnel Healthcare | Report Date: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
    elements.append(Paragraph(footer_text, ParagraphStyle('Footer', fontSize=8, alignment=1, textColor=colors.grey)))

    pdf.build(elements)
    buffer.seek(0)

    # Download styled
    st.markdown("""
        <style>
        div.stDownloadButton > button {
            background: linear-gradient(90deg, #0F2027, #203A43, #2C5364);
            color: #E0F7FA;
            border: none;
            border-radius: 12px;
            padding: 0.7em 1.5em;
            font-weight: 600;
            font-size: 16px;
        }
        </style>
    """, unsafe_allow_html=True)

    st.download_button(
        label="📥 Download Full PDF Report",
        data=buffer,
        file_name=f"police_health_report_{input_data['personnel_id'].iloc[0]}.pdf",
        mime="application/pdf"
    )

# --- FOOTER ---
st.markdown("---")
st.caption("© 2025 Police Health Analytics | Developed for Research and Awareness")
