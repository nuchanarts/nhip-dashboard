import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json

st.set_page_config(page_title="NHIP Dashboard", layout="wide")
st.title("📊 NHIP Smart Dashboard")

SPREADSHEET_ID = "1Y4FANer87OduQcK7XctCjJ0FBEKTHlXJ4aMZklcqzFU"

# ==============================
# 🔄 โหลดรายชื่อ Sheet จาก Google
# ==============================

@st.cache_data(ttl=300)
def get_sheet_names():
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:json"
    res = requests.get(url)
    text = res.text

    # Google จะส่ง JSON ครอบด้วย function call ต้องตัดออก
    json_data = text[text.find("{"):text.rfind("}")+1]
    data = json.loads(json_data)

    sheets = [sheet["properties"]["title"] for sheet in data["table"]["cols"]]
    return sheets

# วิธีที่เสถียรกว่า (ดึงจาก HTML metadata)
@st.cache_data(ttl=300)
def get_sheet_names_safe():
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
    res = requests.get(url)
    text = res.text
    titles = []
    for line in text.split('"title":"')[1:]:
        titles.append(line.split('"')[0])
    return list(set(titles))


# ใช้แบบ safe
try:
    sheet_list = get_sheet_names_safe()
except:
    st.error("❌ ไม่สามารถอ่านรายชื่อ Sheet ได้ ตรวจสอบการแชร์ไฟล์")
    st.stop()

selected_sheet = st.sidebar.selectbox("📄 เลือก Sheet", sheet_list)

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
    st.error("❌ โหลดข้อมูลไม่ได้ กรุณาตรวจสอบการแชร์ Anyone with link → Viewer")
    st.stop()

# ==============================
# 🧠 ตรวจจับคอลัมน์
# ==============================

zone_col = None
province_col = None
date_col = None

for col in df.columns:
    if "เขต" in col:
        zone_col = col
    elif "จังหวัด" in col:
        province_col = col
    elif "วัน" in col or "date" in col.lower():
        date_col = col

if date_col:
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

# ==============================
# 🎛 Filters
# ==============================

st.sidebar.header("🔎 ตัวกรองข้อมูล")

filtered_df = df.copy()

if zone_col:
    zones = df[zone_col].dropna().unique()
    selected_zone = st.sidebar.multiselect("เลือกเขต", zones, default=zones)
    filtered_df = filtered_df[filtered_df[zone_col].isin(selected_zone)]

if province_col:
    provinces = filtered_df[province_col].dropna().unique()
    selected_province = st.sidebar.multiselect("เลือกจังหวัด", provinces, default=provinces)
    filtered_df = filtered_df[filtered_df[province_col].isin(selected_province)]

# ==============================
# 📊 KPI
# ==============================

st.divider()
col1, col2, col3 = st.columns(3)

col1.metric("จำนวนรายการ", len(filtered_df))

if zone_col:
    col2.metric("จำนวนเขต", filtered_df[zone_col].nunique())

if province_col:
    col3.metric("จำนวนจังหวัด", filtered_df[province_col].nunique())

st.divider()

# ==============================
# 📈 กราฟ
# ==============================

col_left, col_right = st.columns(2)

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
# 📥 Export CSV
# ==============================

st.download_button(
    label="📥 ดาวน์โหลดข้อมูล (CSV)",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name=f"{selected_sheet}_report.csv",
    mime="text/csv"
)
