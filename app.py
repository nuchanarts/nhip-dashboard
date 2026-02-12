import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="NHIP Dashboard", layout="wide")
st.title("📊 NHIP Smart Dashboard")

# ==============================
# 🔗 Google Sheet Config
# ==============================

SPREADSHEET_ID = "1Y4FANer87OduQcK7XctCjJ0FBEKTHlXJ4aMZklcqzFU"

# ==============================
# 🔄 โหลดชื่อ Sheet ทั้งหมด
# ==============================

@st.cache_data(ttl=300)
def get_sheet_names():
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:json"
    data = pd.read_json(url)
    return data

# วิธีง่ายกว่า: กำหนดชื่อ sheet เอง (เสถียรกว่า)
SHEETS = ["Sheet1", "Sheet2", "Sheet3"]  # 🔥 แก้ตามชื่อ sheet จริงของคุณ

selected_sheet = st.sidebar.selectbox("📄 เลือก Sheet", SHEETS)

# ==============================
# 🔄 โหลดข้อมูลจาก sheet ที่เลือก
# ==============================

@st.cache_data(ttl=300)
def load_data(sheet_name):
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet_name}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data(selected_sheet)
    st.success("เชื่อม Google Drive สำเร็จ ✅ (Auto refresh 5 นาที)")
except:
    st.error("❌ กรุณาตรวจสอบว่าแชร์แบบ Anyone with link → Viewer")
    st.stop()

# ==============================
# 🧠 ตรวจจับคอลัมน์อัตโนมัติ
# ==============================

date_col = None
zone_col = None
province_col = None
numeric_col = None

for col in df.columns:
    if "วัน" in col or "date" in col.lower():
        date_col = col
    elif "เขต" in col:
        zone_col = col
    elif "จังหวัด" in col:
        province_col = col
    elif pd.api.types.is_numeric_dtype(df[col]) and not numeric_col:
        numeric_col = col

if date_col:
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

# ==============================
# 🎛 Filters
# ==============================

st.sidebar.header("🔎 ตัวกรองข้อมูล")

filtered_df = df.copy()

# เลือกเขต
if zone_col:
    zones = df[zone_col].dropna().unique()
    selected_zone = st.sidebar.multiselect(
        "เลือกเขต", zones, default=zones
    )
    filtered_df = filtered_df[filtered_df[zone_col].isin(selected_zone)]

# เลือกจังหวัด (สัมพันธ์กับเขต)
if province_col:
    provinces = filtered_df[province_col].dropna().unique()
    selected_province = st.sidebar.multiselect(
        "เลือกจังหวัด", provinces, default=provinces
    )
    filtered_df = filtered_df[filtered_df[province_col].isin(selected_province)]

# ==============================
# 📊 KPI
# ==============================

st.divider()

col1, col2, col3 = st.columns(3)

col1.metric("จำนวนรายการ", len(filtered_df))

if zone_col:
    col2.metric("จำนวนเขต", filtered_df[zone_col].nunique())
else:
    col2.metric("จำนวนคอลัมน์", len(filtered_df.columns))

if province_col:
    col3.metric("จำนวนจังหวัด", filtered_df[province_col].nunique())
else:
    col3.metric("")

st.divider()

# ==============================
# 📈 กราฟ
# ==============================

col_left, col_right = st.columns(2)

# กราฟแนวโน้ม
if date_col:
    trend_df = (
        filtered_df
        .groupby(filtered_df[date_col].dt.date)
        .size()
        .reset_index(name="จำนวน")
    )

    if not trend_df.empty:
        fig1 = px.line(trend_df, x=date_col, y="จำนวน", markers=True)
        col_left.plotly_chart(fig1, use_container_width=True)

# กราฟตามจังหวัด
if province_col:
    bar_df = (
        filtered_df
        .groupby(province_col)
        .size()
        .reset_index(name="จำนวน")
        .sort_values("จำนวน", ascending=False)
    )

    fig2 = px.bar(bar_df, x=province_col, y="จำนวน")
    col_right.plotly_chart(fig2, use_container_width=True)

st.divider()

# ==============================
# 📋 ตารางข้อมูล
# ==============================

with st.expander("📋 ดูข้อมูลทั้งหมด"):
    st.dataframe(filtered_df, use_container_width=True)

# ==============================
# 📥 Export CSV (เสถียรสุด)
# ==============================

st.download_button(
    label="📥 ดาวน์โหลดข้อมูล (CSV)",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name=f"{selected_sheet}_report.csv",
    mime="text/csv"
)
