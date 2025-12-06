import streamlit as st
import numpy as np
import pandas as pd
import joblib
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
import io

# ---------------------------
#      PAGE SETTINGS
# ---------------------------
st.set_page_config(page_title="Predictive Healthcare for Police Personnel", layout="wide")

st.markdown("<h1 style='text-align:center;color:#0047AB;'>Predictive Healthcare System for Police Personnel</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align:center;'>Advanced Health Risk Prediction & Personalized Wellness Recommendations</h3>", unsafe_allow_html=True)
st.write("")

# ---------------------------
#    LOAD TRAINED MODEL
# ---------------------------
model = joblib.load("trainedHealthModel.pkl")
scaler = joblib.load("scaler.pkl")
encoder = joblib.load("encoder.pkl")

# COLUMNS USED BY YOUR MODEL
model_feature_order = [
    "Gender", "Age", "BMI", "Physical_Activity", "Smoking", "Alcohol_Consumption",
    "Cholesterol", "Blood_Pressure", "Diabetes", "Sleep_Hours", "Stress_Level",
    "Diet_Type", "Predictive_System_Usage", "Has_Chronic_Disease"
]

# ---------------------------
# SAFE TRANSFORM FUNCTION
# ---------------------------
def safe_transform(df):
    for col in encoder.feature_names_in_:
        df[col] = df[col].astype(str)
    return encoder.transform(df)

# ---------------------------
# SIDEBAR FOR BASIC DETAILS
# ---------------------------
with st.sidebar:
    st.header("Personnel Information")
    personnel_id = st.text_input("Personnel ID")
    name = st.text_input("Name")
    gender = st.selectbox("Gender", ["Male", "Female"])
    age = st.slider("Age", 18, 65, 30)
    height = st.number_input("Height (cm)", 100, 220, 170)
    weight = st.number_input("Weight (kg)", 30, 150, 70)

# ---------------------------
#      HEALTH PARAMETERS
# ---------------------------
st.subheader("Medical Parameters")
col1, col2, col3 = st.columns(3)

with col1:
    physical_activity = st.selectbox("Physical Activity Level", ["Low", "Medium", "High"])
    sleep_hours = st.slider("Sleep Hours", 3, 12, 7)

with col2:
    smoking = st.selectbox("Smoking", ["No", "Yes"])
    alcohol = st.selectbox("Alcohol Consumption", ["No", "Yes"])
    bp = st.selectbox("Blood Pressure", ["Normal", "High"])

with col3:
    cholesterol = st.selectbox("Cholesterol Level", ["Normal", "Borderline", "High"])
    diabetes = st.selectbox("Diabetes", ["No", "Yes"])
    stress = st.slider("Stress Level (1–10)", 1, 10, 5)

# ---------------------------
#         DIET LOGIC
# ---------------------------
st.subheader("Diet Information")

diet_type = st.selectbox("Diet Type", ["Vegetarian", "Non-Vegetarian", "Mixed"])

have_breakfast = st.radio("Do you have Breakfast?", ["Yes", "No"])
have_lunch = st.radio("Do you have Lunch?", ["Yes", "No"])
have_dinner = st.radio("Do you have Dinner?", ["Yes", "No"])

veg_items = ["Roti", "Rice", "Dal", "Green Salad", "Poha", "Dosa", "Upma", "Khichdi"]
nonveg_items = ["Eggs", "Chicken", "Fish"]

# BREAKFAST
if have_breakfast == "Yes":
    if diet_type == "Vegetarian":
        breakfast_items = st.multiselect("Breakfast Items", veg_items)
    elif diet_type == "Non-Vegetarian":
        breakfast_items = st.multiselect("Breakfast Items", nonveg_items)
    else:
        breakfast_items = st.multiselect("Breakfast Items", veg_items + nonveg_items)
else:
    breakfast_items = []

# LUNCH
if have_lunch == "Yes":
    if diet_type == "Vegetarian":
        lunch_items = st.multiselect("Lunch Items", veg_items)
    elif diet_type == "Non-Vegetarian":
        lunch_items = st.multiselect("Lunch Items", nonveg_items)
    else:
        lunch_items = st.multiselect("Lunch Items", veg_items + nonveg_items)
else:
    lunch_items = []

# DINNER
if have_dinner == "Yes":
    if diet_type == "Vegetarian":
        dinner_items = st.multiselect("Dinner Items", veg_items)
    elif diet_type == "Non-Vegetarian":
        dinner_items = st.multiselect("Dinner Items", nonveg_items)
    else:
        dinner_items = st.multiselect("Dinner Items", veg_items + nonveg_items)
else:
    dinner_items = []

# ---------------------------
# USE OF PREDICTIVE SYSTEM
# ---------------------------
predictive_usage = st.selectbox("Do you regularly use this predictive system?", ["No", "Yes"])

# ---------------------------
# CHRONIC DISEASE
# ---------------------------
chronic_disease = st.selectbox("Any Chronic Disease?", ["No", "Diabetes", "Hypertension", "Asthma", "Other"])

# ---------------------------
#       COMPUTE BMI
# ---------------------------
bmi = round(weight / ((height/100) ** 2), 2)

# ---------------------------
#       PREDICT BUTTON
# ---------------------------
if st.button("Predict Health Risk"):

    input_df = pd.DataFrame([[
        gender, age, bmi, physical_activity, smoking, alcohol,
        cholesterol, bp, diabetes, sleep_hours, stress, diet_type,
        predictive_usage, chronic_disease
    ]], columns=model_feature_order)

    encoded = safe_transform(input_df)
    scaled = scaler.transform(encoded)
    prediction = model.predict(scaled)[0]

    risk = ["Low Risk", "Medium Risk", "High Risk"][prediction]

    st.success(f"Predicted Risk Level: **{risk}**")

    # ---------------------------
    #      PDF GENERATION
    # ---------------------------
    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>Predictive Healthcare Report</b>", styles["Title"]))
    elements.append(Spacer(1, 12))

    # USER INFO TABLE
    user_info = [
        ["Field", "Value"],
        ["Personnel ID", personnel_id],
        ["Name", name],
        ["Gender", gender],
        ["Age", str(age)],
        ["BMI", str(bmi)]
    ]
    t1 = Table(user_info)
    t1.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.lightgrey), ("GRID", (0,0), (-1,-1), 1, colors.black)]))
    elements.append(t1)
    elements.append(Spacer(1, 12))

    # MEDICAL TABLE
    med_table = [
        ["Parameter", "Value"],
        ["Physical Activity", physical_activity],
        ["Smoking", smoking],
        ["Alcohol", alcohol],
        ["Blood Pressure", bp],
        ["Cholesterol", cholesterol],
        ["Diabetes", diabetes],
        ["Stress Level", str(stress)],
        ["Sleep Hours", str(sleep_hours)]
    ]
    t2 = Table(med_table)
    t2.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.lightgrey), ("GRID", (0,0), (-1,-1), 1, colors.black)]))
    elements.append(t2)
    elements.append(Spacer(1, 12))

    # DIET TABLE
    diet_table = [
        ["Meal", "Items"],
        ["Breakfast", ", ".join(breakfast_items)],
        ["Lunch", ", ".join(lunch_items)],
        ["Dinner", ", ".join(dinner_items)]
    ]
    t3 = Table(diet_table)
    t3.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,0), colors.lightgrey), ("GRID", (0,0), (-1,-1), 1, colors.black)]))
    elements.append(t3)
    elements.append(Spacer(1, 12))

    # RISK
    elements.append(Paragraph(f"<b>Predicted Health Risk:</b> {risk}", styles["Heading2"]))
    elements.append(Spacer(1, 12))

    # SUGGESTIONS
    elements.append(Paragraph("<b>Personalized Suggestions:</b>", styles["Heading2"]))
    suggestions = [
        "• Maintain a balanced home-cooked diet.",
        "• Avoid processed and fried food.",
        "• Follow daily walking or jogging routines.",
        "• Drink 3–4 liters of water daily.",
        "• Prefer low-salt and low-oil meals.",
        "• Practice meditation or breathing exercises.",
        "• Take sufficient sleep and maintain a consistent schedule."
    ]
    for s in suggestions:
        elements.append(Paragraph(s, styles["Normal"]))

    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M')}", styles["Normal"]))

    pdf.build(elements)
    buffer.seek(0)

    st.download_button(
        label="Download Full PDF Report",
        data=buffer,
        file_name="Health_Report.pdf",
        mime="application/pdf"
    )

