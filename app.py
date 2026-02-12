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
    df[category_col].dropna().unique(),
    default=df[category_col].dropna().unique()
)

filtered_df = df[
    (df[province_col].isin(province_filter)) &
    (df[category_col].isin(category_filter))
]

# ==============================
# KPI CARDS
# ==============================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>จำนวนรายการทั้งหมด</h3>
        <h2>{len(filtered_df):,}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h3>จำนวนจังหวัด</h3>
        <h2>{filtered_df[province_col].nunique():,}</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h3>จำนวนประเภท</h3>
        <h2>{filtered_df[category_col].nunique():,}</h2>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ==============================
# DATA TABLE
# ==============================
st.subheader("📋 ตารางข้อมูล")
st.dataframe(filtered_df, use_container_width=True)

st.divider()

# ==============================
# TREND GRAPH
# ==============================
st.subheader("📈 แนวโน้มตามวันที่")

graph_df = (
    filtered_df
    .groupby(filtered_df[date_col].dt.date)
    .size()
    .reset_index(name="จำนวนรายการ")
)

if not graph_df.empty:
    fig = px.line(
        graph_df,
        x=date_col,
        y="จำนวนรายการ",
        markers=True,
        color_discrete_sequence=["#0E7C7B"]
    )
    fig.update_layout(
        plot_bgcolor="#ffffff",
        paper_bgcolor="#f4fbf9"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("ไม่มีข้อมูลสำหรับแสดงกราฟ")
