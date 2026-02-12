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
# LIGHT HEALTH THEME
# ==============================
st.markdown("""
<style>

/* พื้นหลังหลัก */
.main {
    background-color: #ffffff;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background-color: #F2FBFA;
}

/* หัวข้อ */
h1, h2, h3 {
    color: #2E7D6B;
    font-weight: 600;
}

/* KPI Card */
.metric-card {
    background-color: #FFFFFF;
    padding: 25px;
    border-radius: 14px;
    border: 1px solid #E0F2F1;
    box-shadow: 0px 3px 8px rgba(0,0,0,0.05);
    text-align: center;
}

/* ปุ่ม */
.stButton>button {
    background-color: #4DB6AC;
    color: white;
    border-radius: 10px;
    border: none;
    padding: 0.5rem 1rem;
}

.stButton>button:hover {
    background-color: #26A69A;
}

/* Divider */
hr {
    border: 1px solid #E0F2F1;
}

</style>
""", unsafe_allow_html=True)

st.title("🏥 NHIP Dashboard")
st.caption("ระบบรายงานข้อมูลด้านสาธารณสุข")

# ==============================
# CONNECT GOOGLE SHEET
# ==============================
SPREADSHEET_ID = "1Y4FANer87OduQcK7XctCjJ0FBEKTHlXJ4aMZklcqzFU"
GID = "0"

url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"

try:
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    st.success("เชื่อม Google Sheet สำเร็จ")
except:
    st.error("ไม่สามารถเชื่อม Google Sheet ได้ กรุณาตรวจสอบการแชร์ไฟล์")
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
st.sidebar.header("🔎 ตัวกรอง")

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
# KPI SECTION
# ==============================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <h3>จำนวนรายการทั้งหมด</h3>
        <h2 style="color:#26A69A;">{len(filtered_df):,}</h2>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown(f"""
    <div class="metric-card">
        <h3>จำนวนจังหวัด</h3>
        <h2 style="color:#26A69A;">{filtered_df[province_col].nunique():,}</h2>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <h3>จำนวนประเภท</h3>
        <h2 style="color:#26A69A;">{filtered_df[category_col].nunique():,}</h2>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# ==============================
# TABLE
# ==============================
st.subheader("📋 ตารางข้อมูล")
st.dataframe(filtered_df, use_container_width=True)

st.divider()

# ==============================
# TREND GRAPH
# ==============================
st.subheader("📈 แนวโน้มข้อมูลรายวัน")

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
        color_discrete_sequence=["#4DB6AC"]
    )
    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF"
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("ไม่มีข้อมูลสำหรับแสดงกราฟ")
