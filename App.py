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

# -----------------------
# PAGE CONFIG (simplified)
# -----------------------
st.set_page_config(
    page_title="Predictive Healthcare for Police Personnel",
    page_icon="—Pngtree—gold police officer badge_7258551.png",
    layout="wide"
)

st.markdown("""
<style>
body { background-color: #f8f9fa; color: #212529; font-family: "Segoe UI", sans-serif; }
h1,h2,h3,h4 { color: #0a2647; }
.stButton > button { background-color:#0a2647; color:#fff; border-radius:8px; padding:0.6em 1.2em; font-weight:600;}
.stButton > button:hover { background-color:#144272; }
div.stDownloadButton > button { background-color:#0a2647; color:#fff; border-radius:8px; padding:0.5em 1em; }
</style>
""", unsafe_allow_html=True)

# -----------------------
# Header
# -----------------------
col_logo, col_title = st.columns([1, 4])
with col_logo:
    try:
        st.image("—Pngtree—gold police officer badge_7258551.png", width=90)
    except:
        pass
with col_title:
    st.title("Predictive Healthcare for Police Personnel")
    st.caption("Personalized Risk Assessment — simplified UI")

# -----------------------
# Load dataset & model
# -----------------------
df = pd.read_csv("police_health_dataset.csv")
ct_encoder = joblib.load("ct_encoder.pkl")
xgb_model = joblib.load("xgb_model.pkl")

# -----------------------
# Helper functions
# -----------------------
def get_vital_value(level, low, normal, high):
    return low if level == "Low" else normal if level == "Normal" else high

def qualitative_label_from_numeric(value, breaks):
    # breaks: (low_max, normal_max) threshold approach
    low_max, normal_max = breaks
    if value <= low_max:
        return "Low"
    elif value <= normal_max:
        return "Normal"
    else:
        return "High"

def safe_transform(encoder, X, df_ref, categorical_cols):
    """Try transform, if fails replace unseen categories by df_ref[col].unique()[0] and retry."""
    try:
        return encoder.transform(X)
    except Exception:
        # map unseen categories to first known category
        X2 = X.copy()
        for col in categorical_cols:
            if col in X2.columns:
                known = list(df_ref[col].dropna().unique())
                if known:
                    X2[col] = X2[col].apply(lambda v: v if v in known else known[0])
                else:
                    X2[col] = X2[col].fillna("Unknown")
        return encoder.transform(X2)

# -----------------------
# DEMOGRAPHICS
# -----------------------
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
    city_df = df[df['posted_city'] == posted_city]
    if not city_df.empty:
        pollution_index = float(city_df['pollution_index'].iloc[0])
        city_workload_index = float(city_df['city_workload_index'].iloc[0])
    else:
        pollution_index = 0.0
        city_workload_index = 0.0
    height_cm = st.number_input("Height (cm)", min_value=120, max_value=250)
    weight_kg = st.number_input("Weight (kg)", min_value=30, max_value=200)

bmi = round(weight_kg / ((height_cm/100)**2), 1)
st.text_input("BMI", value=bmi, disabled=True)

# -----------------------
# VITALS (qualitative controls)
# -----------------------
st.header("❤️ Vital Signs (select level — model uses numeric equivalents)")
col1, col2, col3 = st.columns(3)
with col1:
    bp_level = st.selectbox("Blood Pressure Level (Systolic/Diastolic)", ["Low","Normal","High"])
    systolic_bp = get_vital_value(bp_level, 95, 120, 150)
    diastolic_bp = get_vital_value(bp_level, 65, 80, 100)
with col2:
    heart_level = st.selectbox("Heart Rate Level", ["Low","Normal","High"])
    heart_rate = get_vital_value(heart_level, 55, 80, 110)
with col3:
    spo2_level = st.selectbox("SpO₂ Level", ["Low","Normal"])
    spo2 = get_vital_value(spo2_level, 92, 98, 98)

col1, col2 = st.columns(2)
with col1:
    sugar_level = st.selectbox("Fasting Blood Sugar Level", ["Low","Normal","High"])
    fasting_blood_sugar = get_vital_value(sugar_level, 70, 100, 125)
with col2:
    cholesterol_level = st.selectbox("Cholesterol Level", ["Low","Normal","High"])
    cholesterol = get_vital_value(cholesterol_level, 150, 200, 270)

chronic_disease = st.selectbox("Chronic Disease", df['chronic_disease'].unique())
if chronic_disease == "Other":
    chronic_disease_other = st.text_input("Please specify your chronic disease")
else:
    chronic_disease_other = chronic_disease

# -----------------------
# Lifestyle & Exercise
# -----------------------
st.header("🏋️ Lifestyle & Physical Health")

do_exercise = st.radio("Do you exercise?", ["Yes", "No"])
if do_exercise == "Yes":
    exercise_mins_per_week = st.number_input("Exercise minutes per week (enter 0 if none)", min_value=0, max_value=10000, step=5)
    # show exercise types only if > 0
    exercise_types = []
    if exercise_mins_per_week > 0:
        exercise_types = st.multiselect("Select types of exercise you do", ["Walking","Running","Jogging","Swimming","Cycling","Weight training","Aerobics","Yoga"])
else:
    exercise_mins_per_week = 0
    exercise_types = []

sleep_hours = st.number_input("Sleep hours per day", min_value=1, max_value=24)
# Diet quality existing options (kept)
st.markdown("### 🥗 Diet Quality & Nutrition")
meal = st.multiselect("Meals you take regularly", ["Breakfast","Lunch","Dinner"])
diet_protein = st.selectbox("Protein requirement met?", ["Low","Medium","High"])
diet_vitamins = st.selectbox("Vitamins requirement met?", ["Low","Medium","High"])
diet_carbs = st.selectbox("Carbohydrates requirement met?", ["Low","Medium","High"])
diet_minerals = st.selectbox("Minerals requirement met?", ["Low","Medium","High"])
smoking = st.selectbox("Do you smoke?", ["No","Occasionally","Regularly"])
alcohol = st.selectbox("Do you consume alcohol?", ["No","Occasionally","Regularly"])

# Wellness program moved below alcohol (user asked)
wellness_program = st.radio("Wellness Programs Provided by Department?", ["Yes","No","Sometimes"])
st.info("Healthcare Scheme is used for Survey & Analysis Purpose . Wellness program is just informative only.")

water_intake_liters = st.number_input("Daily Water Intake (Liters)", min_value=0.0, max_value=10.0, step=0.1)

# -----------------------
# Diet section: breakfast, lunch, dinner with Maharashtrian options
# -----------------------
st.header("🍽️ Food choices (Breakfast / Lunch / Dinner) — affects cholesterol impact")

# Food lists (Maharashtra-focused examples)
veg_breakfast = ["Poha", "Misal (veg)", "Upma", "Sabudana Khichdi", "Batata Vada", "Thalipeeth", "Puran Poli (sweet)"]
nonveg_breakfast = ["Egg Bhurji", "Egg Roll", "Chicken Sandwich (small)"]

veg_lunch = ["Chapati-Bhaji", "Zunka-Bhakar", "Pithla", "Usal", "Varan-Bhaat", "Bhaji-Roti", "Sambar-Rice (veg)"]
nonveg_lunch = ["Bombil (fish) curry", "Chicken Curry", "Mutton Curry", "Fish Fry", "Egg Curry"]
mix_lunch = veg_lunch + nonveg_lunch

veg_dinner = ["Bhakri-Bhaji", "Chapati-Veg", "Bharli Vangi (stuffed brinjal)", "Dal-Rice", "Batatyachi Bhaji"]
nonveg_dinner = ["Fish Curry", "Chicken Masala", "Mutton Sukka", "Fried Fish"]
mix_dinner = veg_dinner + nonveg_dinner

# For each meal: do you take it? then type and selection
# Breakfast
st.subheader("Breakfast")
has_breakfast = st.radio("Do you have breakfast every day?", ["Yes","No"], horizontal=True, key="breakfast_yesno")
breakfast_score = 0
breakfast_choices = []
if has_breakfast == "Yes":
    breakfast_type = st.radio("Breakfast Type", ["Veg","Non-Veg","Mix"], horizontal=True, key="breakfast_type")
    if breakfast_type == "Veg":
        breakfast_choices = st.multiselect("Select veg breakfast items you eat regularly", veg_breakfast, key="breakfast_veg")
    elif breakfast_type == "Non-Veg":
        breakfast_choices = st.multiselect("Select non-veg breakfast items you eat regularly", nonveg_breakfast, key="breakfast_nonveg")
    else:
        breakfast_choices = st.multiselect("Select breakfast items you eat regularly (mix)", veg_breakfast + nonveg_breakfast, key="breakfast_mix")
    # scoring: veg small impact, nonveg bigger
    for item in breakfast_choices:
        if item in nonveg_breakfast:
            breakfast_score += 8
        else:
            breakfast_score += 3
else:
    breakfast_choices = []
    breakfast_score = 0

# Lunch
st.subheader("Lunch")
has_lunch = st.radio("Do you have lunch every day?", ["Yes","No"], horizontal=True, key="lunch_yesno")
lunch_score = 0
lunch_choices = []
if has_lunch == "Yes":
    lunch_type = st.radio("Lunch Type", ["Veg","Non-Veg","Mix"], horizontal=True, key="lunch_type")
    if lunch_type == "Veg":
        lunch_choices = st.multiselect("Select veg lunch items you eat regularly", veg_lunch, key="lunch_veg")
    elif lunch_type == "Non-Veg":
        lunch_choices = st.multiselect("Select non-veg lunch items you eat regularly", nonveg_lunch, key="lunch_nonveg")
    else:
        lunch_choices = st.multiselect("Select lunch items you eat regularly (mix)", mix_lunch, key="lunch_mix")
    for item in lunch_choices:
        if item in nonveg_lunch:
            lunch_score += 12
        else:
            lunch_score += 5
else:
    lunch_choices = []
    lunch_score = 0

# Dinner
st.subheader("Dinner")
has_dinner = st.radio("Do you have dinner every day?", ["Yes","No"], horizontal=True, key="dinner_yesno")
dinner_score = 0
dinner_choices = []
if has_dinner == "Yes":
    dinner_type = st.radio("Dinner Type", ["Veg","Non-Veg","Mix"], horizontal=True, key="dinner_type")
    if dinner_type == "Veg":
        dinner_choices = st.multiselect("Select veg dinner items you eat regularly", veg_dinner, key="dinner_veg")
    elif dinner_type == "Non-Veg":
        dinner_choices = st.multiselect("Select non-veg dinner items you eat regularly", nonveg_dinner, key="dinner_nonveg")
    else:
        dinner_choices = st.multiselect("Select dinner items you eat regularly (mix)", mix_dinner, key="dinner_mix")
    for item in dinner_choices:
        if item in nonveg_dinner:
            dinner_score += 12
        else:
            dinner_score += 5
else:
    dinner_choices = []
    dinner_score = 0

# Compute overall diet score
diet_score = breakfast_score + lunch_score + dinner_score
# qualitative diet category
if diet_score <= 10:
    diet_category = "Low"
elif diet_score <= 30:
    diet_category = "Normal"
else:
    diet_category = "High"

st.info(f"Estimated diet cholesterol impact: **{diet_category}** (internal score: {diet_score})")

# -----------------------
# Occupational & mental
# -----------------------
st.header("💼 Occupational Health")
col1, col2 = st.columns(2)
with col1:
    shift_pattern = st.selectbox("Shift Pattern", ["Day","Night","Rotational"])
with col2:
    working_hours_per_week = st.number_input("Working hours per week", min_value=1, max_value=120)

# Mental health / stress calculation (kept)
st.header("🧠 Mental Health & Wellbeing")
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
mood = st.selectbox("How do you feel today?", ["😊 Happy","😐 Neutral","😔 Sad","😟 Stressed","😡 Angry"])
mindfulness = st.slider("Minutes of Mindfulness / Meditation Everyday", 0, 60, 0)

# -----------------------
# Prediction input preparation
# -----------------------
st.markdown("---")
st.header("🩺 Prediction & Report")

if st.button("Predict My Risk & Download PDF"):
    # Build input dataframe (include numeric versions for model and diet/exercise flags)
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
        # numeric vitals (for model)
        'systolic_bp':[systolic_bp],
        'diastolic_bp':[diastolic_bp],
        'heart_rate':[heart_rate],
        'spo2':[spo2],
        'fasting_blood_sugar':[fasting_blood_sugar],
        'cholesterol':[cholesterol],
        # chronic
        'chronic_disease':[chronic_disease_other if chronic_disease_other else "None"],
        'sleep_hours':[sleep_hours],
        'exercise_mins_per_week':[exercise_mins_per_week],
        'exercise_flag':[1 if do_exercise == "Yes" and exercise_mins_per_week > 0 else 0],
        'smoking':[smoking],
        'alcohol':[alcohol],
        'stress_level':[stress_level],
        'shift_pattern':[shift_pattern],
        'working_hours_per_week':[working_hours_per_week],
        # healthcare scheme fallback (take first if df has)
        'healthcare_scheme':[df['healthcare_scheme'].iloc[0] if 'healthcare_scheme' in df.columns else "Unknown"],
        'technological_support':["Low"],
        'predictive_system_usage':["Yes"],
        # diet features to include in model
        'breakfast_score':[breakfast_score],
        'lunch_score':[lunch_score],
        'dinner_score':[dinner_score],
        'diet_score':[diet_score],
        'diet_category':[diet_category],
        # include foods selected (string) for reference / pdf (encoder may not expect these)
        'breakfast_foods':[", ".join(breakfast_choices) if breakfast_choices else "None"],
        'lunch_foods':[", ".join(lunch_choices) if lunch_choices else "None"],
        'dinner_foods':[", ".join(dinner_choices) if dinner_choices else "None"],
        'has_breakfast':[has_breakfast],
        'has_lunch':[has_lunch],
        'has_dinner':[has_dinner]
    })

    # Convert certain columns to numeric safely where needed
    numeric_cols = ['personnel_id','pollution_index','city_workload_index','age','years_of_service',
                    'height_cm','weight_kg','bmi','systolic_bp','diastolic_bp','heart_rate','spo2',
                    'fasting_blood_sugar','cholesterol','sleep_hours','exercise_mins_per_week',
                    'stress_level','working_hours_per_week','breakfast_score','lunch_score','dinner_score','diet_score']
    for c in numeric_cols:
        if c in input_data.columns:
            input_data[c] = pd.to_numeric(input_data[c], errors='coerce')

    # Fill NA and cast categorical columns
    input_data.fillna("Unknown", inplace=True)
    categorical_cols = ['post','posted_city','gender','chronic_disease','smoking','alcohol',
                        'shift_pattern','healthcare_scheme','technological_support','predictive_system_usage','diet_category',
                        'has_breakfast','has_lunch','has_dinner']
    for col in categorical_cols:
        if col in input_data.columns:
            input_data[col] = input_data[col].astype(str)

    # Encode and predict safely (handle unseen categories)
    input_encoded = safe_transform(ct_encoder, input_data, df, categorical_cols)
    risk_score = float(xgb_model.predict(input_encoded)[0])

    # lifestyle adjustments
    if smoking == "Occasionally": risk_score += 5
    elif smoking == "Regularly": risk_score += 10
    if alcohol == "Occasionally": risk_score += 3
    elif alcohol == "Regularly": risk_score += 8
    # small adjustment from diet_score
    risk_score += (diet_score / 20.0)  # small contribution

    # risk category
    if risk_score < 40:
        risk_category = "✅ Normal"
    elif risk_score < 70:
        risk_category = "⚠ Borderline"
    else:
        risk_category = "❌ High Risk"

    st.markdown("### Results")
    st.write(f"**Risk Score:** {risk_score:.1f}")
    st.write(f"**Risk Category:** {risk_category}")

    # Build top-5 feature importances display if model has attribute
    try:
        importance = xgb_model.feature_importances_
        feature_names = input_data.columns
        top_indices = np.argsort(importance)[::-1][:5]
        st.subheader("Top Factors Impacting Risk")
        for i in top_indices:
            st.write(f"- {feature_names[i]} (importance: {importance[i]:.3f})")
    except Exception:
        pass

    # Personalized recommendations (basic)
    recommendations = []
    if risk_category == "✅ Normal":
        recommendations.append("Maintain your current healthy lifestyle and continue regular check-ups.")
    elif risk_category == "⚠ Borderline":
        recommendations.append("Pay attention to diet, monitor vitals and consult for lifestyle changes.")
    else:
        recommendations.append("High risk: consult a healthcare professional immediately and follow medical advice.")

    # targeted based on categories
    if bp_level != "Normal":
        recommendations.append("Blood pressure is not Normal: monitor BP and reduce salt intake.")
    if cholesterol_level != "Normal" or diet_category == "High":
        recommendations.append("High cholesterol/diet impact: reduce fatty/non-veg fried foods and consult dietitian.")
    if sleep_hours < 7:
        recommendations.append("Improve sleep to at least 7 hours for better recovery.")
    if exercise_mins_per_week < 60:
        recommendations.append("Aim for at least 60 minutes of moderate exercise weekly.")
    if smoking != "No":
        recommendations.append("Consider quitting smoking to reduce long-term health risk.")
    if alcohol != "No":
        recommendations.append("Limit alcohol consumption.")

    st.subheader("Personalized Recommendations")
    for rec in recommendations:
        st.info(rec)

    # Overall health summary counts (High/Normal/Low among vitals + diet)
    categories = [bp_level, heart_level, sugar_level, cholesterol_level, diet_category]
    summary = {"High": categories.count("High"), "Normal": categories.count("Normal"), "Low": categories.count("Low")}
    st.info(f"Overall Categories → High: {summary['High']} | Normal: {summary['Normal']} | Low: {summary['Low']}")

    # -----------------------
    # PDF generation
    # -----------------------
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=30)
    styles = getSampleStyleSheet()
    # small custom styles
    styles.add(ParagraphStyle(name='TitleCenter', parent=styles['Title'], alignment=1))
    styles.add(ParagraphStyle(name='Heading', parent=styles['Heading2'], spaceAfter=6))
    elements = []
    # logo (try)
    try:
        logo = Image("—Pngtree—gold police officer badge_7258551.png", width=60, height=60)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1,8))
    except:
        pass
    elements.append(Paragraph("Predictive Healthcare Report", styles['TitleCenter']))
    elements.append(Spacer(1,8))
    elements.append(Paragraph(f"Generated on: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}", styles['Normal']))
    elements.append(Spacer(1,12))

    # --- Personnel & demographic info (include numeric where acceptable) ---
    elements.append(Paragraph("Personnel & Demographics", styles['Heading']))
    demo_rows = [
        ["Personnel ID", str(input_data['personnel_id'].iloc[0])],
        ["Age (years)", str(input_data['age'].iloc[0])],
        ["Gender", str(input_data['gender'].iloc[0])],
        ["Post", str(input_data['post'].iloc[0])],
        ["Posted City", str(input_data['posted_city'].iloc[0])],
        ["Years of Service", str(input_data['years_of_service'].iloc[0])],
        ["Height (cm)", str(input_data['height_cm'].iloc[0])],
        ["Weight (kg)", str(input_data['weight_kg'].iloc[0])],
        ["BMI", str(input_data['bmi'].iloc[0])]
    ]
    demo_table = Table(demo_rows, colWidths=[180, 320])
    demo_table.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.3,colors.grey),('FONTSIZE',(0,0),(-1,-1),9)]))
    elements.append(demo_table)
    elements.append(Spacer(1,10))

    # --- Vital signs (show qualitative only, no numeric vitals) ---
    elements.append(Paragraph("Vital Signs (qualitative)", styles['Heading']))
    vitals_rows = [
        ["Blood Pressure", bp_level],
        ["Heart Rate", heart_level],
        ["SpO₂", spo2_level],
        ["Fasting Blood Sugar", sugar_level],
        ["Cholesterol", cholesterol_level]
    ]
    vitals_table = Table(vitals_rows, colWidths=[180, 320])
    vitals_table.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.3,colors.grey),('FONTSIZE',(0,0),(-1,-1),9)]))
    elements.append(vitals_table)
    elements.append(Spacer(1,10))

    # --- Lifestyle & habits ---
    elements.append(Paragraph("Lifestyle & Habits", styles['Heading']))
    lifestyle_rows = [
        ["Exercise", "No Exercise" if input_data['exercise_mins_per_week'].iloc[0] == 0 else f"Yes — {int(input_data['exercise_mins_per_week'].iloc[0])} mins/week"],
        ["Exercise Types", ", ".join(exercise_types) if exercise_types else "None"],
        ["Sleep Hours", str(input_data['sleep_hours'].iloc[0])],
        ["Smoking", str(input_data['smoking'].iloc[0])],
        ["Alcohol", str(input_data['alcohol'].iloc[0])],
        ["Wellness Program Provided", str(wellness_program)],
        ["Water Intake (L/day)", str(input_data['water_intake_liters'].iloc[0]) if 'water_intake_liters' in locals() else "N/A"]
    ]
    life_table = Table(lifestyle_rows, colWidths=[180, 320])
    life_table.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.3,colors.grey),('FONTSIZE',(0,0),(-1,-1),9)]))
    elements.append(life_table)
    elements.append(Spacer(1,10))

    # --- Diet details (show qualitative and items selected) ---
    elements.append(Paragraph("Diet & Meal Details (qualitative)", styles['Heading']))
    diet_rows = [
        ["Breakfast (Yes/No)", has_breakfast],
        ["Breakfast Foods", ", ".join(breakfast_choices) if breakfast_choices else "None"],
        ["Lunch (Yes/No)", has_lunch],
        ["Lunch Foods", ", ".join(lunch_choices) if lunch_choices else "None"],
        ["Dinner (Yes/No)", has_dinner],
        ["Dinner Foods", ", ".join(dinner_choices) if dinner_choices else "None"],
        ["Diet Impact Category", diet_category]
    ]
    diet_table = Table(diet_rows, colWidths=[180, 320])
    diet_table.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.3,colors.grey),('FONTSIZE',(0,0),(-1,-1),9)]))
    elements.append(diet_table)
    elements.append(Spacer(1,10))

    # --- Occupational & mental ---
    elements.append(Paragraph("Occupational & Mental Health", styles['Heading']))
    occ_rows = [
        ["Shift Pattern", shift_pattern],
        ["Working Hours / week", str(working_hours_per_week)],
        ["Stress Level (1-10)", str(stress_level)],
        ["Mood", mood],
        ["Mindfulness mins/day", str(mindfulness)]
    ]
    occ_table = Table(occ_rows, colWidths=[180, 320])
    occ_table.setStyle(TableStyle([('GRID',(0,0),(-1,-1),0.3,colors.grey),('FONTSIZE',(0,0),(-1,-1),9)]))
    elements.append(occ_table)
    elements.append(Spacer(1,12))

    # --- Risk summary & recommendations ---
    elements.append(Paragraph("Risk Assessment", styles['Heading']))
    # Color the category text by using simple paragraph color styling
    if risk_category == "✅ Normal":
        rc_style = ParagraphStyle('rc', textColor=colors.green, fontSize=11)
    elif risk_category == "⚠ Borderline":
        rc_style = ParagraphStyle('rc', textColor=colors.orange, fontSize=11)
    else:
        rc_style = ParagraphStyle('rc', textColor=colors.red, fontSize=11)
    elements.append(Paragraph(f"Risk Category: {risk_category}", rc_style))
    elements.append(Paragraph(f"Risk Score (internal): {risk_score:.1f}", styles['Normal']))  # user requested not to show vitals numeric, but score is okay
    elements.append(Spacer(1,8))
    elements.append(Paragraph("Recommendations", styles['Heading']))
    for rec in recommendations:
        elements.append(Paragraph(f"• {rec}", styles['Normal']))
    elements.append(Spacer(1,12))

    # --- Overall health counts (qualitative) ---
    elements.append(Paragraph("Overall Health Summary (qualitative)", styles['Heading']))
    elements.append(Paragraph(f"High: {summary['High']}  |  Normal: {summary['Normal']}  |  Low: {summary['Low']}", styles['Normal']))
    elements.append(Spacer(1,16))

    # Footer
    footer_text = f"Generated from Police Personnel Healthcare | Report Date: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
    elements.append(Paragraph(footer_text, ParagraphStyle('Footer', fontSize=8, alignment=1, textColor=colors.grey)))

    pdf.build(elements)
    buffer.seek(0)

    # Download PDF
    st.download_button(
        label="📥 Download Full PDF Report",
        data=buffer,
        file_name=f"police_health_report_{personnel_id}.pdf",
        mime="application/pdf"
    )

# -----------------------
# Footer
# -----------------------
st.markdown("---")
st.caption("© 2025 Police Health Analytics | Developed for Research and Awareness")
