import streamlit as st
import base64
# App Title and Header
st.set_page_config(
    page_title="Predictive Healthcare for Police Personnel",
    page_icon="—Pngtree—gold police officer badge_7258551.png",
    layout="wide"
)

import base64
# Convert logo image to base64
with open("—Pngtree—gold police officer badge_7258551.png", "rb") as img_file:
    encoded_logo = base64.b64encode(img_file.read()).decode()

# Header Section
st.markdown(
    f"""
    <style>
        /* compact sticky header */
        .app-header {{
            position: fixed;
            top: 3.2rem;             /* below Streamlit top bar */
            left: 0;
            width: 100%;
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 24px;
            padding: 8px 12px;      /* <<< compact height */
            color: white;
            border-radius: 0 0 10px 10px;
            background: linear-gradient(135deg, rgba(15,32,39,0.95), rgba(32,58,67,0.95));
            backdrop-filter: blur(4px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.5);
        }}

        .app-header .brand {{
            display:flex;
            align-items:center;
            gap:10px;
            margin-right: 18px;
        }}

        .app-header img {{
            width: 48px;            /* <<< small logo */
            height: 48px;
            border-radius: 8px;
            box-shadow: 0 0 8px rgba(0,0,0,0.4);
        }}

        .app-header .title {{
            font-size: 1.05rem;
            font-weight: 700;
            margin: 0;
            line-height: 1;
            color: #E0F7FA;
        }}

        .app-header .subtitle {{
            font-size: 0.75rem;
            margin: 0;
            color: #B3E5FC;
            opacity: 0.9;
        }}

        /* nav tabs */
        .app-nav {{
            display:flex;
            gap:8px;
            align-items:center;
        }}

        .app-nav a {{
            padding: 6px 12px;
            font-size: 0.9rem;
            color: #dbeefe;
            text-decoration: none;
            border-radius: 8px;
            cursor: pointer;
            transition: transform 0.12s ease, box-shadow 0.12s ease;
            border: 1px solid rgba(255,255,255,0.04);
            background: linear-gradient(180deg, rgba(255,255,255,0.02), rgba(0,0,0,0.02));
        }}

        .app-nav a:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(0,0,0,0.35);
        }}

        .app-nav a.active {{
            background: linear-gradient(90deg, rgba(0,200,255,0.12), rgba(0,120,255,0.08));
            color: #E8FFFF;
            border: 1px solid rgba(0,200,255,0.18);
        }}

        /* ensure content not hidden under header */
        .block-container {{
            padding-top: 160px !important;  /* reduce so page below remains as-is */
        }}

        /* small screens - responsive */
        @media (max-width: 700px) {{
            .app-header {{
                padding: 8px 8px;
                gap: 10px;
            }}
            .app-nav a {{ padding: 6px 8px; font-size:0.8rem; }}
            .app-header img {{ width:40px; height:40px; }}
            .block-container {{ padding-top: 200px !important; }}
        }}
    </style>

    <div class="app-header" role="navigation" aria-label="App header and navigation">
        <div class="brand" aria-hidden="false">
            <img src="data:image/png;base64,{encoded_logo}" alt="Police Logo">
            <div style="display:flex;flex-direction:column;justify-content:center;">
                <div class="title">Predictive Healthcare</div>
                <div class="subtitle">for Police Personnel</div>
            </div>
        </div>

        <nav class="app-nav" id="appNav">
            <a class="nav-item active" data-target="top">Home</a>
            <a class="nav-item" data-target="Demographics">Demographics</a>
            <a class="nav-item" data-target="Vital Signs">Vital Signs</a>
            <a class="nav-item" data-target="Lifestyle">Lifestyle</a>
            <a class="nav-item" data-target="Recommendations">Recommendations</a>
            <a class="nav-item" data-target="Download">Download</a>
        </nav>
    </div>

    <script>
    (() => {{
        // Helper: smooth scroll to element by matching visible heading text (best-effort)
        function scrollToSectionByText(text) {{
            if (text === 'top') {{
                window.scrollTo({{top: 0, behavior: 'smooth'}});
                return;
            }}
            // Search for headers (h1..h4) and elements with class that contain the text
            const candidates = Array.from(document.querySelectorAll('h1, h2, h3, h4, .stMarkdown, .streamlit-expanderHeader'));
            const match = candidates.find(el => el.innerText && el.innerText.toLowerCase().includes(text.toLowerCase()));
            if (match) {{
                // compute top offset to account for fixed header height
                const header = document.querySelector('.app-header');
                const offset = header ? header.getBoundingClientRect().height + 24 : 120;
                const topPos = match.getBoundingClientRect().top + window.scrollY - offset;
                window.scrollTo({{top: topPos, behavior: 'smooth'}});
                return true;
            }} else {{
                // fallback: try to scroll to approximate positions by known keywords
                const keyword = text.toLowerCase();
                const mapping = {{
                    'demographics': document.querySelector('.stNumberInput') || null,
                }};
                const el = mapping[keyword];
                if (el) {{
                    const header = document.querySelector('.app-header');
                    const offset = header ? header.getBoundingClientRect().height + 24 : 120;
                    const topPos = el.getBoundingClientRect().top + window.scrollY - offset;
                    window.scrollTo({{top: topPos, behavior: 'smooth'}});
                    return true;
                }}
            }}
            return false;
        }}

        // attach click handlers to nav items
        const navItems = document.querySelectorAll('.app-nav .nav-item');
        navItems.forEach(item => {{
            item.addEventListener('click', (e) => {{
                e.preventDefault();
                // set active class
                navItems.forEach(n=>n.classList.remove('active'));
                item.classList.add('active');
                const target = item.getAttribute('data-target');
                // try multiple matching variants
                const variants = [target, '👤 ' + target, target + ' (years)', target + ' hours', target.toLowerCase()];
                let scrolled = false;
                for (const v of variants) {{
                    if (scrollToSectionByText(v)) {{
                        scrolled = true;
                        break;
                    }}
                }}
                if (!scrolled) {{
                    // last resort: scroll slowly down page to help user
                    if (target.toLowerCase() === 'download') {{
                        window.scrollTo({{top: document.body.scrollHeight, behavior: 'smooth'}});
                    }}
                }}
            }});
        }});

        // observe DOM changes to ensure nav remains visible (optional resilience)
        const observer = new MutationObserver(() => {{
            const header = document.querySelector('.app-header');
            if (header) header.style.display = 'flex';
        }});
        observer.observe(document.body, {{childList:true, subtree:true}});
    }})();
    </script>
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
    pollution_index = st.text_input("City Pollution Index", value=city_data['pollution_index'], disabled=True)
    city_workload_index = st.text_input("City Workload Index", value=city_data['city_workload_index'], disabled=True)
    height_cm = st.number_input("Height (cm)", min_value=120, max_value=250)
    weight_kg = st.number_input("Weight (kg)", min_value=30, max_value=200)

# Auto-calculate BMI
bmi = round(weight_kg / ((height_cm/100)**2), 1)
st.text_input("BMI", value=bmi, disabled=True)


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
    if chronic_disease == "Other":
        chronic_disease_other = st.text_input("Please specify your chronic disease")

st.subheader("🏃 Lifestyle / Habits")

col1, col2, col3 = st.columns(3)

with col1:
    exercise_mins_per_week = st.number_input("Exercise minutes per week (0 if none)", min_value=0, max_value=1000)
    sleep_hours = st.number_input("Sleep hours per day", min_value=1, max_value=24)
    diet_quality = st.text_input("Diet Quality (Enter your description)")

with col2:
    stress_level = st.slider("Stress Level (1-10)", min_value=1, max_value=10)
    smoking = st.radio("Smoking", ["Yes", "No"])
    alcohol = st.radio("Alcohol Consumption", ["Yes", "No"])

with col3:
    shift_pattern = st.selectbox("Shift Pattern", ["Day", "Night", "Rotational"])
    working_hours_per_week = st.number_input("Working hours per week", min_value=1, max_value=120)
    healthcare_scheme = st.selectbox("Healthcare Scheme", df['healthcare_scheme'].unique())
    if healthcare_scheme == "Other":
        healthcare_scheme_other = st.text_input("Specify Healthcare Scheme")

# Technology & predictive system usage
st.subheader("💻 Technology & System Usage")
col1, col2 = st.columns(2)
with col1:
    technological_support = st.radio("Technology Support Level Usage of Health Apps or Smart-Watches", ["High", "Medium", "Low"])
with col2:
    predictive_system_usage = st.radio("Use of Predictive System? (This Application) ", ["Yes", "No"])

st.subheader("📝 Awareness Section")

awareness_questions = [
    "I am fully aware of the healthcare policies designed for police personnel in my department.",
    "I regularly participate in healthcare or wellness programs provided by the department.",
    "The process for accessing departmental healthcare services is straightforward.",
    "I am satisfied with the healthcare benefits offered to me as a police officer.",
    "The healthcare policies are well communicated to all personnel.",
    "Department policies have improved my health and wellbeing.",
    "I feel confident that the healthcare policies will support me during a health crisis.",
    "These healthcare policies have contributed to reducing absenteeism due to health problems.",
    "Irregular shifts and night duties negatively impact my health.",
    "My job makes it difficult to maintain a healthy routine.",
    "I experience significant stress due to my daily work.",
    "My eating habits are affected by my work schedule.",
    "I frequently suffer from fatigue or sleep disturbances.",
    "It is challenging to find time for regular physical activity.",
    "My family or social life is affected by my professional commitments.",
    "My health issues are strongly linked to my daily job responsibilities.",
    "I have access to department-approved health monitoring technology (wearables/apps).",
    "I use technological tools to track my health metrics (e.g., steps, heart rate).",
    "The technology provided is user-friendly and easy to integrate into my routine.",
    "I find digital health tracking motivates me to maintain healthier habits.",
    "Tech support from the department helps me manage my health more effectively.",
    "I trust that my health data is secure and used responsibly.",
    "I am satisfied with the guidance or recommendations provided by health technologies.",
    "I believe technological interventions reduce the risk of health issues for police personnel.",
    "I receive regular health alerts or reminders (e.g., for checkups, risk warnings).",
    "The alerts I receive are relevant to my health risks.",
    "I act on health recommendations provided through prediction systems.",
    "Following these alerts has led to positive changes in my lifestyle.",
    "The prediction system motivates me to attend regular health screenings.",
    "I find the guidance from prediction systems understandable and actionable.",
    "Health alerts make me more aware of potential health risks I might ignore.",
    "I would recommend the implementation of health prediction systems department-wide."
]

# Store responses
awareness_responses = {}

for q in awareness_questions:
    awareness_responses[q] = st.radio(
        q,
        ["Strongly Agree", "Agree", "Neutral", "Disagree", "Strongly Disagree"],
        index=2  # Default to 'Neutral'
    )

import joblib
import numpy as np

# Load Encoder and Model
ct_encoder = joblib.load("ct_encoder.pkl")
xgb_model = joblib.load("xgb_model.pkl")

# Action Button
if st.button("Predict My Risk & Recommendations"):

    # Show spinner while computing
    with st.spinner("Calculating your risk score..."):

        # Prepare input data
        input_data = pd.DataFrame({
            'personnel_id': [personnel_id],
            'post': [post],
            'posted_city': [posted_city],
            'pollution_index': [pollution_index],
            'city_workload_index': [city_workload_index],
            'age': [age],
            'gender': [gender],
            'years_of_service': [years_of_service],
            'height_cm': [height_cm],
            'weight_kg': [weight_kg],
            'bmi': [bmi],
            'systolic_bp': [systolic_bp],
            'diastolic_bp': [diastolic_bp],
            'heart_rate': [heart_rate],
            'spo2': [spo2],
            'fasting_blood_sugar': [fasting_blood_sugar],
            'cholesterol': [cholesterol],
            'chronic_disease': [chronic_disease if chronic_disease != "Other" else chronic_disease_other],
            'sleep_hours': [sleep_hours],
            'exercise_mins_per_week': [exercise_mins_per_week],
            'smoking': [smoking],
            'alcohol': [alcohol],
            'stress_level': [stress_level],
            'shift_pattern': [shift_pattern],
            'working_hours_per_week': [working_hours_per_week],
            'healthcare_scheme': [healthcare_scheme if healthcare_scheme != "Other" else healthcare_scheme_other],
            'technological_support': [technological_support],
            'predictive_system_usage': [predictive_system_usage]
        })

        # --- Convert numeric columns to float ---
        numeric_cols = [
            'personnel_id','pollution_index','city_workload_index','age','years_of_service',
            'height_cm','weight_kg','bmi','systolic_bp','diastolic_bp','heart_rate','spo2',
            'fasting_blood_sugar','cholesterol','sleep_hours','exercise_mins_per_week',
            'stress_level','working_hours_per_week'
        ]

        for col in numeric_cols:
            input_data[col] = pd.to_numeric(input_data[col], errors='coerce')  # converts invalid values to NaN

        # Check for invalid numeric input
        if input_data[numeric_cols].isnull().any().any():
            st.error("Some numeric inputs are invalid. Please check your entries.")
            st.stop()  # stop execution if invalid

        # --- Ensure categorical columns are strings ---
        categorical_cols = [
            'post','posted_city','gender','chronic_disease','smoking','alcohol',
            'shift_pattern','healthcare_scheme','technological_support','predictive_system_usage'
        ]
        for col in categorical_cols:
            input_data[col] = input_data[col].astype(str).fillna("Unknown")

        # Encode categorical features
        input_encoded = ct_encoder.transform(input_data)

        # Predict Risk Score
        risk_score = xgb_model.predict(input_encoded)[0]

        # Map risk score to category
        if risk_score < 40:
            risk_category = "✅ Normal"
            # color = "green"
        elif risk_score < 70:
            risk_category = "⚠ Borderline"
            # color = "yellow"
        else:
            risk_category = "❌ High Risk"
            # color = "red"

        # Define color dynamically based on risk category
        if risk_category == "✅ Normal":
            color = "#00C853"      # green
            glow = "0 0 10px rgba(0, 200, 83, 0.8)"
        elif risk_category == "⚠ Borderline":
            color = "#FFA000"      # amber
            glow = "0 0 10px rgba(255, 160, 0, 0.8)"
        else:
            color = "#D32F2F"      # red
            glow = "0 0 10px rgba(211, 47, 47, 0.8)"
        
        # Stylish section for Risk Score & Category
        st.markdown(
            f"""
            <style>
                @keyframes pulseGlow {{
                    0% {{ box-shadow: {glow}; }}
                    50% {{ box-shadow: 0 0 25px rgba(255, 255, 255, 0.6); }}
                    100% {{ box-shadow: {glow}; }}
                }}
        
                .risk-box {{
                    margin-top: 30px;
                    text-align: center;
                    padding: 20px;
                    border-radius: 15px;
                    background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
                    color: white;
                    box-shadow: {glow};
                    animation: pulseGlow 4s infinite ease-in-out;
                    transition: transform 0.3s ease;
                }}
        
                .risk-box:hover {{
                    transform: scale(1.03);
                }}
        
                .risk-score {{
                    font-size: 2.2em;
                    color: {color};
                    text-shadow: 0 0 10px {color};
                    font-weight: 700;
                }}
        
                .risk-category {{
                    font-size: 1.5em;
                    color: {color};
                    text-shadow: 0 0 10px {color};
                    font-weight: 600;
                }}
            </style>
        
            <div class="risk-box">
                <h2 class="risk-score">Risk Score: {risk_score:.1f}</h2>
                <h3 class="risk-category">Risk Category: {risk_category}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Feature Importance (Top 5)
        importance = xgb_model.feature_importances_
        feature_names = input_data.columns
        top_indices = np.argsort(importance)[::-1][:5]

        st.subheader("📊 Top Factors Impacting Risk")
        for i in top_indices:
            st.progress(min(int(importance[i]*100), 100), text=f"{feature_names[i]}")

        # Placeholder for Recommendations
        

# Personalized Recommendations (Safe Version)
if 'risk_category' in locals():  # Check if risk_category exists
    st.subheader("💡 Personalized Recommendations")
    st.info("Based on your risk profile, recommended preventive measures will be displayed here.")

    recommendations = []

    # General advice based on risk category
    if risk_category == "✅ Normal":
        recommendations.append("Maintain your current healthy lifestyle and continue regular check-ups.")
    elif risk_category == "⚠ Borderline":
        recommendations.append("Pay attention to your diet, exercise regularly, and monitor vital signs closely with Healthcare Proffessional.")
    else:  # High Risk
        recommendations.append("Consult a healthcare professional immediately and follow preventive measures strictly.")

    # Targeted advice based on top 3 features
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
            recommendations.append("Practice stress management techniques like meditation or yoga.")
        elif feature == "smoking":
            recommendations.append("Consider quitting smoking to reduce health risks.")
        elif feature == "alcohol":
            recommendations.append("Limit alcohol consumption to improve health.")

    # Display recommendations
    for rec in recommendations:
        st.success(rec)


st.subheader("💬 Suggestions / Comments")
user_comments = st.text_area("Enter your comments or feedback here (optional):")

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
import io
import datetime
import streamlit as st

if 'risk_score' in locals():
    st.subheader("📄 Download PDF Report")

    buffer = io.BytesIO()
    pdf = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        rightMargin=30, 
        leftMargin=30,
        topMargin=30, 
        bottomMargin=30
    )

    elements = []
    styles = getSampleStyleSheet()

    # Custom styles (renamed to avoid KeyError)
    styles.add(ParagraphStyle(name='HeadingLarge', fontSize=16, leading=20, spaceAfter=10, alignment=1, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='SubHeading', fontSize=14, leading=18, spaceAfter=8, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='NormalText', fontSize=12, leading=16, fontName='Helvetica'))
    styles.add(ParagraphStyle(name='BoldText', fontSize=12, leading=16, fontName='Helvetica-Bold'))
    styles.add(ParagraphStyle(name='FooterText', fontSize=10, leading=12, alignment=1, textColor=colors.grey))
    from reportlab.platypus import Image ,Spacer

    # Add logo at top
    try:
     logo = Image("—Pngtree—gold police officer badge_7258551.png", width=60, height=60)
     logo.hAlign = 'CENTER'
     elements.append(logo)
     elements.append(Spacer(1, 8))
    except Exception as e:
     st.warning(f"Logo not loaded: {e}")

    # Title
    elements.append(Paragraph("Predictive Healthcare Report", styles['HeadingLarge']))
    elements.append(Spacer(1, 12))

    # Personnel Info Table
    elements.append(Paragraph("Personnel Information", styles['SubHeading']))
    data = [[col, str(input_data[col].iloc[0])] for col in input_data.columns]
    table = Table(data, colWidths=[150, 350])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 12))

    # Risk Assessment
    elements.append(Paragraph("Risk Assessment", styles['SubHeading']))

    if risk_category == "✅ Normal":
        color = colors.green
    elif risk_category == "⚠ Borderline":
        color = colors.orange
    else:
        color = colors.red

    elements.append(Paragraph(f"Risk Score: {risk_score:.1f}", ParagraphStyle('RiskScore', textColor=color, fontSize=12, leading=16)))
    elements.append(Paragraph(f"Risk Category: {risk_category}", ParagraphStyle('RiskCat', textColor=color, fontSize=12, leading=16)))
    elements.append(Spacer(1, 12))

    # Top Features
    elements.append(Paragraph("Top Factors Impacting Risk", styles['SubHeading']))
    for i in top_indices[:5]:
        elements.append(Paragraph(f"{feature_names[i]} (Importance: {xgb_model.feature_importances_[i]:.2f})", styles['NormalText']))
    elements.append(Spacer(1, 12))

    # Recommendations
    elements.append(Paragraph("Personalized Recommendations", styles['SubHeading']))
    for rec in recommendations:
        elements.append(Paragraph(f"• {rec}", styles['NormalText']))
    elements.append(Spacer(1, 12))

    # Footer / Timestamp
    footer_text = f"Generated from Police Personnel Healthcare | Developed by Pranita Marodkar | Report Date: {datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
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
























