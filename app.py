import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# PAGE CONFIG
# ==============================
st.set_page_config(
    page_title="NHIP Dashboard",
    layout="wide"
)

# ==============================
# CUSTOM CSS (โทนสาธารณสุข)
# ==============================
st.markdown("""
<style>
body {
    background-color: #f4fbf9;
}

[data-testid="stSidebar"] {
    background-color: #e8f6f5;
}

h1, h2, h3 {
    color: #0E7C7B;
}

.metric-card {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 12px;
    box-shadow: 0px 2px 6px rgba(0,0,0,0.08);
    text-align: center;
}

.stButton>button {
    background-color: #0E7C7B;
    color: white;
    border-radius: 8px;
    border: none;
}

.stButton>button:hover {
    background-color: #0b5f5e;
}
</style>
""", unsafe_allow_html=True)

st.title("🏥 NHIP Dashboard")
st.caption("ระบบรายงานข้อมูลเพื่อการบริหารจัดการด้านสาธารณสุข")

# ==============================
# CONNECT GOOGLE SHEET
# ==============================
SPREADSHEET_ID = "1Y4FANer87OduQcK7XctCjJ0FBEKTHlXJ4aMZklcqzFU"
GID = "0"

url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"

try:
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    st.success("เชื่อม Google Sheet สำเร็จ ✅")
except Exception as e:
    st.error("❌ ไม่สามารถเชื่อมได้ กรุณาตรวจสอบการแชร์ไฟล์")
    st.stop()

# ==============================
# SIDEBAR SETTINGS
# ==============================
st.sidebar.header("⚙️ ตั้งค่าคอลัมน์")

date_col = st.sidebar.selectbox("เลือกคอลัมน์วันที่", df.columns)
province_col = st.sidebar.selectbox("เลือกคอลัมน์จังหวัด", df.columns)
category_col = st.sidebar.selectbox("เลือกคอลัมน์ประเภท", df.columns)

df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

# ==============================
# FILTER
# ==============================
st.sidebar.header("🔎 ตัวกรองข้อมูล")

province_filter = st.sidebar.multiselect(
    "เลือกจังหวัด",
    df[province_col].dropna().unique(),
    default=df[province_col].dropna().unique()
)

category_filter = st.sidebar.multiselect(
    "เลือกประเภท",
    df[category_col].dropna().un_]()
