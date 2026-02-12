import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="NHIP Dashboard",
    layout="wide"
)

# =========================
# MODERN HEALTH THEME
# =========================
st.markdown("""
<style>

/* Background */
.stApp {
    background-color: #F6FAFD;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #EAF6FB;
}

/* Headings */
h1 {
    color: #2F3E46;
    font-weight: 700;
}

h2, h3 {
    color: #3A5A66;
}

/* KPI Card */
.metric-card {
    background-color: #FFFFFF;
    padding: 25px;
    border-radius: 18px;
    box-shadow: 0 8px 20px rgba(0,0,0,0.04);
    text-align: center;
    transition: 0.3s;
}

.metric-card:hover {
    transform: translateY(-4px);
}

/* Accent Numbers */
.metric-number {
    color: #3EC7B6;
    font-size: 28px;
    font-weight: 700;
}

/* Buttons */
.stButton>button {
    background-color: #3EC7B6;
    color: white;
    border-radius: 12px;
    border: none;
    padding: 0.5rem 1.2r
