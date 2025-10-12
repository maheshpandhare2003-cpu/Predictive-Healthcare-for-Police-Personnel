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

# --- Background with Black-Blue Gradient Overlay ---
import base64

# Option 1: Use Online Background Image
bg_image_url = "https://images.unsplash.com/photo-1526256262350-7da7584cf5eb"  # You can replace this link

page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] {{
    background: 
        linear-gradient(rgba(0, 0, 0, 0.7), rgba(10, 25, 47, 0.9)),
        url("{bg_image_url}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

[data-testid="stHeader"], [data-testid="stSidebar"] {{
    background: rgba(0,0,0,0);
}}

h1, h2, h3, h4, h5, h6, p, label, span {{
    color: #E0F7FA !important;
}}

.stButton > button {{
    background: linear-gradient(90deg, #0F2027, #203A43, #2C5364);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.6em 1.2em;
    font-weight: bold;
    transition: 0.3s;
}}

.stButton > button:hover {{
    background: linear-gradient(90deg, #2C5364, #203A43, #0F2027);
    transform: scale(1.03);
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)


# --- HEADER SECTION ---
with open("—Pngtree—gold police officer badge_7258551.png", "rb") as img_file:
    encoded_logo = base64.b64encode(img_file.read()).decode()

st.markdown(f"""
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
""", unsafe_allow_html=True)

# --- LOAD DATASET & MODEL ---
df = pd.read_csv("police_health_dataset.csv")
ct_encoder = joblib.load("ct_encoder.pkl")
xgb_model = joblib.load("xgb_model.pkl")

# --- DEMOGRAPHICS SECTION ---
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
    city_data = df[df['posted_city']==posted_city].iloc[0]
    pollution_index = st.text_input("City Pollution Index", value=city_data['pollution_index'], disabled=True)
    city_workload_index = st.text_input("City Workload Index", value=city_data['city_workload_index'], disabled=True)
    height_cm = st.number_input("Height (cm)", min_value=120, max_value=250)
    weight_kg = st.number_input("Weight (kg)", min_value=30, max_value=200)
bmi = round(weight_kg / ((height_cm/100)**2),1)
st.text_input("BMI", value=bmi, disabled=True)

# --- HEALTHCARE SCHEME SECTION ---
st.subheader("🏥 Healthcare Scheme & Awareness Programs")
col1, col2 = st.columns(2)
with col1:
    healthcare_scheme = st.selectbox("Select Your Healthcare Scheme", df['healthcare_scheme'].unique())
    if healthcare_scheme=="Other":
        healthcare_scheme_other = st.text_input("Specify Healthcare Scheme")
with col2:
    wellness_program = st.radio("Wellness Programs Provided by Department?", ["Yes","No","Sometimes"])
st.info("Healthcare Scheme is used for Survey & Analysis Purpose . Wellness program is just informative only.")

# --- VITAL SIGNS SECTION ---
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
    if chronic_disease=="Other":
        chronic_disease_other = st.text_input("Please specify your chronic disease")

# --- Physical Health ---
st.markdown("### 🏋️ Physical Health")
col1, col2 = st.columns(2)
with col1:
    exercise_mins_per_week = st.number_input("Exercise minutes per week (0 if none)", min_value=0, max_value=1000)
with col2:
    sleep_hours = st.number_input("Sleep hours per day", min_value=1, max_value=24)
# Dynamic Exercise Types
exercise_types = []
if exercise_mins_per_week>0:
    exercise_types = st.multiselect(
        "Select types of exercise you do",
        ["Swimming","Running","Jogging","Walking","Weight training","Cycling","Aerobics"]
    )

# --- Diet Quality ---
# --- Diet Quality Section ---
st.markdown("### 🥗 Diet Quality & Nutrition")

# Meals taken
meal = st.multiselect("Meals you take regularly", ["Breakfast", "Lunch", "Dinner"])

# Macro/Micronutrients completion
diet_protein = st.selectbox("Protein requirement met?", ["Not Completed", "Partially Completed", "Completed"])
diet_vitamins = st.selectbox("Vitamins requirement met?", ["Not Completed", "Partially Completed", "Completed"])
diet_carbs = st.selectbox("Carbohydrates requirement met?", ["Not Completed", "Partially Completed", "Completed"])
diet_minerals = st.selectbox("Minerals requirement met?", ["Not Completed", "Partially Completed", "Completed"])

# Water Intake
water_intake_liters = st.number_input("Daily Water Intake (Liters)", min_value=0.0, max_value=10.0, step=0.1)

# Optional info tooltip
st.info("Provide accurate values to get better personalized recommendations.")

# --- Occupational Health ---
st.markdown("### 💼 Occupational Health")
col1, col2 = st.columns(2)
with col1:
    shift_pattern = st.selectbox("Shift Pattern", ["Day","Night","Rotational"])
    working_hours_per_week = st.number_input("Working hours per week", min_value=1, max_value=120)

# --- MENTAL HEALTH SECTION ---
st.markdown("### 🧠 Mental Health & Wellbeing")
# --- Auto-calculate Stress Level ---
stress_calc = 5  # base
# Sleep factor
if sleep_hours < 6:
    stress_calc += 3
elif sleep_hours < 7:
    stress_calc += 2
elif sleep_hours < 8:
    stress_calc += 1

# Working hours factor
if working_hours_per_week > 60:
    stress_calc += 3
elif working_hours_per_week > 50:
    stress_calc += 2
elif working_hours_per_week > 40:
    stress_calc += 1

# Exercise factor
if exercise_mins_per_week == 0:
    stress_calc += 2
elif exercise_mins_per_week < 60:
    stress_calc += 1

# Shift pattern factor
if shift_pattern.lower() in ["night", "rotational"]:
    stress_calc += 2

# Clip to 1-10
stress_level = int(np.clip(stress_calc, 1, 10))


# --- Mood Selector ---
mood = st.selectbox(
    "How do you feel today?",
    ["😊 Happy", "😐 Neutral", "😔 Sad", "😟 Stressed", "😡 Angry"]
)

# --- Mindfulness / Meditation ---
mindfulness = st.slider("Minutes of Mindfulness / Meditation Everyday", 0, 60, 0)

# --- Stress Visualization ---
stress_percentage = int((stress_level / 10) * 100)
color = "#00C853" if stress_level <= 4 else "#FFA000" if stress_level <= 7 else "#D32F2F"
st.progress(stress_percentage, text=f"Stress Level: {stress_level}/10")
st.markdown(f"<span style='color:{color}; font-weight:bold'>Stress Score Visual</span>", unsafe_allow_html=True)

# --- Tips / Suggestions ---
if stress_level >= 7:
    st.warning("⚠ High stress detected! Consider taking a short walk, meditation, or talking to a colleague.")
elif stress_level >= 4:
    st.info("ℹ Moderate stress: Keep up regular exercise, adequate sleep, and hydration.")
else:
    st.success("✅ Low stress! Keep maintaining your healthy routine.")

# --- Daily Journaling ---
mental_notes = st.text_area(
    "Write a note about your mental wellbeing Issues if you have in Your Services (optional):",
    placeholder="Reflect on your workload, stress,duties and work activities..."
)

st.markdown("</div>", unsafe_allow_html=True)

# --- Technology & System Usage ---
st.markdown("### 💻 Technology & System Usage")
tech_usage_yesno = st.radio("Do you use technology Apps or Devices for health tracking?", ["Yes","No"])
tech_level = None
if tech_usage_yesno=="Yes":
    tech_level = st.radio("Level of usage", ["High","Medium","Low"])

# --- ATTRACTIVE DYNAMIC BUTTON ---
import base64

# Encode logo
with open("—Pngtree—gold police officer badge_7258551.png", "rb") as img_file:
    encoded_logo = base64.b64encode(img_file.read()).decode()

# --- DYNAMIC BUTTON WITH LOGO (CSS fixed) ---
st.markdown(f"""
<style>
div.stButton > button:first-child {{
    font-size: 18px;
    font-weight: 700;
    padding: 15px 40px 15px 60px;
    border-radius: 15px;
    border: none;
    color: white;
    cursor: pointer;
    background: linear-gradient(135deg, #0F2027, #203A43, #2C5364);
    background-size: 300% 300%;
    animation: gradientShiftBtn 5s ease infinite;
    box-shadow: 0 4px 20px rgba(0,0,0,0.6);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
    position: relative;
}}

div.stButton > button:first-child::before {{
    content: "";
    position: absolute;
    left: 15px;
    top: 50%;
    transform: translateY(-50%);
    width: 30px;
    height: 30px;
    background-image: url("data:image/png;base64,{encoded_logo}");
    background-size: cover;
    background-repeat: no-repeat;
}}

div.stButton > button:first-child:hover {{
    transform: scale(1.05);
    box-shadow: 0 0 25px rgba(0,191,255,0.9);
}}

div.stButton > button:first-child:active {{
    transform: scale(0.98);
    box-shadow: 0 0 15px rgba(0,191,255,0.7);
}}

@keyframes gradientShiftBtn {{
    0% {{ background-position: 0% 50%; }}
    50% {{ background-position: 100% 50%; }}
    100% {{ background-position: 0% 50%; }}
}}
</style>
""", unsafe_allow_html=True)

# --- REAL STREAMLIT BUTTON ---
if st.button("Predict My Risk & Recommendations"):
    # --- Your existing prediction logic ---
    with st.spinner("Calculating your risk score..."):
        # Prepare input data dictionary
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
            'chronic_disease':[chronic_disease if chronic_disease!="Other" else chronic_disease_other],
            'sleep_hours':[sleep_hours],
            'exercise_mins_per_week':[exercise_mins_per_week],
            'smoking':["No"],  # placeholder if needed
            'alcohol':["No"],  # placeholder if needed
            'stress_level':[stress_level],
            'shift_pattern':[shift_pattern],
            'working_hours_per_week':[working_hours_per_week],
            'healthcare_scheme':[healthcare_scheme if healthcare_scheme!="Other" else healthcare_scheme_other],
            'technological_support':[tech_level if tech_level else "Low"],
            'predictive_system_usage':["Yes"]
        })

        # Convert numeric columns to float
     numeric_cols = ['personnel_id','pollution_index','city_workload_index','age','years_of_service',
                        'height_cm','weight_kg','bmi','systolic_bp','diastolic_bp','heart_rate','spo2',
                        'fasting_blood_sugar','cholesterol','sleep_hours','exercise_mins_per_week',
                        'stress_level','working_hours_per_week']
     for col in numeric_cols:
            input_data[col] = pd.to_numeric(input_data[col], errors='coerce')
     if input_data[numeric_cols].isnull().any().any():
            st.error("Invalid numeric inputs detected!")
            st.stop()
        # Encode categorical
     categorical_cols = ['post','posted_city','gender','chronic_disease','smoking','alcohol',
                            'shift_pattern','healthcare_scheme','technological_support','predictive_system_usage']
     for col in categorical_cols:
            input_data[col] = input_data[col].astype(str).fillna("Unknown")
     input_encoded = ct_encoder.transform(input_data)
        # Predict
     risk_score = xgb_model.predict(input_encoded)[0]
     if risk_score<40: risk_category="✅ Normal"
     elif risk_score<70: risk_category="⚠ Borderline"
     else: risk_category="❌ High Risk"
    # --- STYLISH RISK SCORE & CATEGORY WITH BLACK GRADIENT ---
    # --- RISK SCORE & CATEGORY STYLISH AND DYNAMIC ---
     color = "#EBEBEB" if risk_category=="✅ Normal" else "#FFA000" if risk_category=="⚠ Borderline" else "#D32F2F"
     
     st.markdown(f"""
     <style>
     @keyframes gradientText {{
         0% {{ background-position: 0% 50%; }}
         50% {{ background-position: 100% 50%; }}
         100% {{ background-position: 0% 50%; }}
     }}
     
     .risk-box {{
         text-align: center;
         padding: 25px;
         border-radius: 20px;
         background: linear-gradient(135deg, #0F2027, #203A43, #2C5364);
         background-size: 300% 300%;
         animation: gradientShift 10s ease infinite;
         box-shadow: 0 6px 25px rgba(0,0,0,0.6);
         margin-top: 20px;
     }}
     
     .risk-score {{
         font-size: 3em;
         font-weight: 800;
         background: linear-gradient(90deg, #00ffea, #00C853, #00ffea);
         background-size: 200% 200%;
         -webkit-background-clip: text;
         -webkit-text-fill-color: transparent;
         animation: gradientText 4s ease infinite;
         text-shadow: 0 0 15px rgba(0,255,234,0.6);
     }}
     
     .risk-category {{
         font-size: 2em;
         font-weight: 700;
         background: linear-gradient(90deg, #FFEA00, #FFA000, #FFEA00);
         background-size: 200% 200%;
         -webkit-background-clip: text;
         -webkit-text-fill-color: transparent;
         animation: gradientText 4s ease infinite;
         text-shadow: 0 0 12px rgba(255,235,0,0.6);
     }}
     </style>
     
     <div class="risk-box">
         <div class="risk-score">Risk Score: {risk_score:.1f}</div>
         <div class="risk-category">Risk Category: {risk_category}</div>
     </div>
     """, unsafe_allow_html=True)

     
    # --- FEATURE IMPORTANCE ---
     st.subheader("📊 Top Factors Impacting Risk")
     importance = xgb_model.feature_importances_
     feature_names = input_data.columns
     top_indices = np.argsort(importance)[::-1][:5]
     for i in top_indices:
      st.progress(min(int(importance[i]*100), 100), text=f"{feature_names[i]}")
    # --- PERSONALIZED RECOMMENDATIONS ---
     st.subheader("💡 Personalized Recommendations")
     recommendations = []
    # Risk-category-based recommendations
     if risk_category == "✅ Normal":
      recommendations.append("Maintain your current healthy lifestyle and continue regular check-ups.")
     elif risk_category == "⚠ Borderline":
      recommendations.append("Pay attention to your diet, exercise regularly, and monitor vital signs closely.")
     else:  # High Risk
      recommendations.append("Consult a healthcare professional immediately and follow preventive measures strictly.")
   # Targeted advice based on top features
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
       recommendations.append("Practice stress management techniques like meditation, yoga, or mindfulness.")
      elif feature == "smoking":
       recommendations.append("Consider quitting smoking to reduce health risks.")
      elif feature == "alcohol":
       recommendations.append("Limit alcohol consumption to improve health.")
      elif feature == "water_intake_liters":
       recommendations.append("Maintain proper hydration by drinking sufficient water daily.")
      elif feature in ["diet_protein", "diet_vitamins", "diet_carbs", "diet_minerals"]:
       recommendations.append(f"Ensure your {feature.split('_')[1]} intake meets daily requirements.")
# Dsplay all recommendations
     for rec in recommendations:
      st.success(rec)
    
     import numpy as np
     from reportlab.lib.pagesizes import A4
     from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
     from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
     from reportlab.lib import colors
     import io
     import datetime
    
     st.subheader("📄 Download PDF Report")
    
     buffer = io.BytesIO()
     pdf = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=30, leftMargin=30,
        topMargin=30, bottomMargin=30
     )
     elements = []
     styles = getSampleStyleSheet()
     styles.add(ParagraphStyle(name='HeadingLarge', fontSize=16, leading=20, spaceAfter=10, alignment=1, fontName='Helvetica-Bold'))
     styles.add(ParagraphStyle(name='SubHeading', fontSize=14, leading=18, spaceAfter=8, fontName='Helvetica-Bold'))
     styles.add(ParagraphStyle(name='NormalText', fontSize=12, leading=16, fontName='Helvetica'))
     styles.add(ParagraphStyle(name='FooterText', fontSize=10, leading=12, alignment=1, textColor=colors.grey))
    
    # Logo
     try:
        logo = Image("—Pngtree—gold police officer badge_7258551.png", width=60, height=60)
        logo.hAlign = 'CENTER'
        elements.append(logo)
        elements.append(Spacer(1,8))
     except:
        pass
    
    # Title
     elements.append(Paragraph("Predictive Healthcare Report", styles['HeadingLarge']))
     elements.append(Spacer(1,12))
    
    # Personnel Info
     elements.append(Paragraph("Personnel Information", styles['SubHeading']))
     data = [[col, str(input_data[col].iloc[0])] for col in input_data.columns]
     table = Table(data, colWidths=[150, 350])
     table.setStyle(TableStyle([
        ('BACKGROUND',(0,0),(-1,0),colors.lightgrey),
        ('GRID',(0,0),(-1,-1),0.5,colors.black),
        ('FONTNAME',(0,0),(-1,-1),'Helvetica'),
        ('FONTSIZE',(0,0),(-1,-1),10),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
     ]))
     elements.append(table)
     elements.append(Spacer(1,12))
    
    # Risk Assessment
     elements.append(Paragraph("Risk Assessment", styles['SubHeading']))
     risk_color = colors.green if risk_category=="✅ Normal" else colors.orange if risk_category=="⚠ Borderline" else colors.red
     elements.append(Paragraph(f"Risk Score: {risk_score:.1f}", ParagraphStyle('RiskScore', textColor=risk_color, fontSize=12, leading=16)))
     elements.append(Paragraph(f"Risk Category: {risk_category}", ParagraphStyle('RiskCat', textColor=risk_color, fontSize=12, leading=16)))
     elements.append(Spacer(1,12))
    
    # Top Features
     elements.append(Paragraph("Top Factors Impacting Risk", styles['SubHeading']))
     for i in top_indices[:5]:
        elements.append(Paragraph(f"{feature_names[i]} (Importance: {xgb_model.feature_importances_[i]:.2f})", styles['NormalText']))
     elements.append(Spacer(1,12))
    
    # Recommendations
     elements.append(Paragraph("Personalized Recommendations", styles['SubHeading']))
     for rec in recommendations:
        elements.append(Paragraph(f"• {rec}", styles['NormalText']))
     elements.append(Spacer(1,12))
    
    # Footer
     footer_text = f"Generated from Police Personnel Healthcare | Developed by Your Name | Report Date: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
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
    
    
    
    
    






