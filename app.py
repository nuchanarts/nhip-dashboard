import streamlit as st
import pandas as pd
import plotly.express as px

# ==============================
# ตั้งค่า Page
# ==============================
st.set_page_config(
    page_title="NHIP Dashboard",
    layout="wide"
)

st.title("📊 NHIP Dashboard (Google Drive Connected)")

# ==============================
# เชื่อม Google Sheet โดยตรง
# ==============================
SPREADSHEET_ID = "1Y4FANer87OduQcK7XctCjJ0FBEKTHlXJ4aMZklcqzFU"
GID = "0"  # เปลี่ยนถ้าใช้ sheet อื่น

url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"

try:
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    st.success("เชื่อม Google Sheet สำเร็จ ✅")
except Exception as e:
    st.error("❌ ไม่สามารถเชื่อมได้ กรุณาตรวจสอบว่าเปิดแชร์แบบ Anyone with the link → Viewer แล้ว")
    st.write(e)
    st.stop()

# ==============================
# เลือกคอลัมน์ใช้งาน
# ==============================
st.sidebar.header("⚙️ ตั้งค่าคอลัมน์")

date_col = st.sidebar.selectbox("เลือกคอลัมน์วันที่", df.columns)
province_col = st.sidebar.selectbox("เลือกคอลัมน์จังหวัด", df.columns)
category_col = st.sidebar.selectbox("เลือกคอลัมน์ประเภท/แผนก", df.columns)

df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

# ==============================
# ตัวกรอง
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
# KPI
# ==============================
col1, col2, col3 = st.columns(3)

col1.metric("จำนวนรายการทั้งหมด", len(filtered_df))
col2.metric("จำนวนจังหวัด", filtered_df[province_col].nunique())
col3.metric("จำนวนประเภท", filtered_df[category_col].nunique())

st.divider()

# ==============================
# ตารางข้อมูล
# ==============================
st.subheader("📋 ตารางข้อมูล")
st.dataframe(filtered_df, use_container_width=True)

st.divider()

# ==============================
# กราฟแนวโน้มตามวันที่
# ==============================
st.subheader("📈 จำนวนรายการตามวันที่")

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
        markers=True
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("ไม่มีข้อมูลสำหรับแสดงกราฟ")
