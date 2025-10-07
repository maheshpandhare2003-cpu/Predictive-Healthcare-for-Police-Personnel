import streamlit as st

# App Title and Header
st.set_page_config(page_title="Predictive Healthcare for Police Personnel", layout="wide")

# Header Section
st.markdown(
    """
    <div style='text-align: center; padding: 10px; background-color: #1E3A8A; color: white; border-radius: 10px;'>
        <h1>Predictive Healthcare for Police Personnel</h1>
        <p>Get your personalized risk assessment and preventive suggestions</p>
        <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/3/37/Police_Icon.svg/1024px-Police_Icon.svg.png" 
             width="80" alt="Police Logo">
    </div>
    """,
    unsafe_allow_html=True
)
