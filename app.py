import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import re

# -----------------------------
# CONFIG
# -----------------------------
st.set_page_config(
    page_title="NHIP Executive Dashboard",
    layout="wide"
)

SPREADSHEET_ID = "1Y4FANer87OduQcK7XctCjJ0FBEKTHlXJ4aMZklcqzFU"

# -----------------------------
# AUTO REFRESH 5 นาที
# -----------------------------
st.markdown(
    """
    <meta http-equiv="refresh" content="300">
    """,
    unsafe_allow_html=True
)

# -----------------------------
# THEME (สว่าง สาธารณสุข)
# -----------------------------
st.markdown("""
<style>
body { background-color: #f4fbf9; }
.metric-card {
    background-color: #e8f5f3;
    padding: 20px;
    border-radius: 12px;
}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# LOAD SHEET NAMES
# -----------------------------
@st.cache_data(ttl=300)
def get_sheet_names():
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}"
    res = requests.get(url)
    matches = re.findall(r'"title":"(.*?)"', res.text)
    return list(set(matches))

# -----------------------------
# LOAD ALL SHEETS
# -----------------------------
@st.cache_data(ttl=300)
def load_all_sheets():
    sheet_names = get_sheet_names()
    all_dfs = []

    for sheet in sheet_names:
        try:
            csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet}"
            df = pd.read_csv(csv_url)
            df["Sheet"] = sheet
            all_dfs.append(df)
        except:
            pass

    if not all_dfs:
        return pd.DataFrame()

    return pd.concat(all_dfs, ignore_index=True)

df = load_all_sheets()

if df.empty:
    st.error("❌ ไม่สามารถโหลดข้อมูลได้")
    st.stop()

# -----------------------------
# CLEAN COLUMN NAMES
# -----------------------------
df.columns = df.columns.str.strip()

# -----------------------------
# SIDEBAR FILTER
# -----------------------------
st.sidebar.header("🔎 ตัวกรองข้อมูล")

if "เขต" in df.columns:
    zone = st.sidebar.selectbox("เลือกเขต", ["ทั้งหมด"] + sorted(df["เขต"].dropna().unique().tolist()))
    if zone != "ทั้งหมด":
        df = df[df["เขต"] == zone]

if "จังหวัด" in df.columns:
    province = st.sidebar.selectbox("เลือกจังหวัด", ["ทั้งหมด"] + sorted(df["จังหวัด"].dropna().unique().tolist()))
    if province != "ทั้งหมด":
        df = df[df["จังหวัด"] == province]

# -----------------------------
# TITLE
# -----------------------------
st.title("📊 NHIP Executive Dashboard")

# -----------------------------
# KPI SUMMARY
# -----------------------------
st.subheader("📌 Executive Summary")

numeric_cols = df.select_dtypes(include="number").columns.tolist()

if numeric_cols:
    col1, col2, col3 = st.columns(3)

    total_value = df[numeric_cols[0]].sum()
    avg_value = df[numeric_cols[0]].mean()
    max_value = df[numeric_cols[0]].max()

    col1.metric("ยอดรวมทั้งหมด", f"{total_value:,.0f}")
    col2.metric("ค่าเฉลี่ย", f"{avg_value:,.2f}")
    col3.metric("ค่าสูงสุด", f"{max_value:,.0f}")

# -----------------------------
# TREND ANALYSIS (Sheet เพิ่ม/ลด)
# -----------------------------
st.subheader("📈 วิเคราะห์แนวโน้มแต่ละ Sheet")

trend_data = df.groupby("Sheet")[numeric_cols[0]].sum().reset_index()

fig_trend = px.bar(
    trend_data,
    x="Sheet",
    y=numeric_cols[0],
    color=numeric_cols[0],
    color_continuous_scale="Tealgrn"
)

st.plotly_chart(fig_trend, use_container_width=True)

# วิเคราะห์เพิ่ม/ลด
if len(trend_data) >= 2:
    trend_data = trend_data.sort_values("Sheet")
    diff = trend_data[numeric_cols[0]].diff().iloc[-1]

    if diff > 0:
        st.success("📈 แนวโน้มเพิ่มขึ้นจาก Sheet ก่อนหน้า")
    elif diff < 0:
        st.warning("📉 แนวโน้มลดลงจาก Sheet ก่อนหน้า")
    else:
        st.info("➖ แนวโน้มคงที่")

# -----------------------------
# DATA TABLE
# -----------------------------
st.subheader("📄 ตารางข้อมูล")
st.dataframe(df, use_container_width=True)

# -----------------------------
# EXPORT CSV
# -----------------------------
csv = df.to_csv(index=False).encode("utf-8")
st.download_button(
    "📥 ดาวน์โหลดข้อมูล (CSV)",
    csv,
    "NHIP_Report.csv",
    "text/csv"
)
