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

