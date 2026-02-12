import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json

st.set_page_config(page_title="NHIP Executive Dashboard", layout="wide")

# ===============================
# 🎨 โทนสาธารณสุขสว่าง
# ===============================
st.markdown("""
<style>
.main { background-color: #F3FBF8; }
h1, h2, h3 { color: #127C5C; }
div[data-testid="metric-container"] {
    background: white;
    padding: 15px;
    border-radius: 12px;
    border-left: 6px solid #1FBF8F;
}
</style>
""", unsafe_allow_html=True)

st.title("🏥 NHIP Executive Dashboard")

SPREADSHEET_ID = "1Y4FANer87OduQcK7XctCjJ0FBEKTHlXJ4aMZklcqzFU"

# =====================================================
# 📄 โหลดรายชื่อ Sheet จาก Google Drive
# =====================================================
@st.cache_data(ttl=300)
def get_sheet_names():
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:json"
    res = requests.get(url)
    text = res.text
    json_str = text[text.find("{"):text.rfind("}")+1]
    data = json.loads(json_str)
    sheets = data.get("sheets", [])
    return [s["properties"]["title"] for s in sheets]

sheet_list = get_sheet_names()

# =====================================================
# 🎛 SIDEBAR FILTERS (เรียงลำดับชัดเจน)
# =====================================================
st.sidebar.header("📊 ตัวกรองข้อมูล")

selected_sheets = st.sidebar.multiselect(
    "1️⃣ เลือก Sheet",
    sheet_list,
    default=sheet_list[:1]
)

if not selected_sheets:
    st.warning("กรุณาเลือกอย่างน้อย 1 Sheet")
    st.stop()

# =====================================================
# 📥 โหลดข้อมูลตาม Sheet ที่เลือก
# =====================================================
@st.cache_data(ttl=300)
def load_sheet(sheet):
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df["Sheet"] = sheet
    return df

dfs = [load_sheet(s) for s in selected_sheets]
df = pd.concat(dfs, ignore_index=True)

# =====================================================
# 🔍 ตรวจจับคอลัมน์อัตโนมัติ
# =====================================================
zone_col = next((c for c in df.columns if "เขต" in c), None)
province_col = next((c for c in df.columns if "จังหวัด" in c), None)
date_col = next((c for c in df.columns if "วัน" in c or "date" in c.lower()), None)

if date_col:
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

# =====================================================
# 🎛 Filter เขต
# =====================================================
filtered_df = df.copy()

if zone_col:
    zone_list = sorted(df[zone_col].dropna().unique())
    selected_zone = st.sidebar.multiselect(
        "2️⃣ เลือกเขต",
        zone_list,
        default=zone_list
    )
    filtered_df = filtered_df[filtered_df[zone_col].isin(selected_zone)]

# =====================================================
# 🎛 Filter จังหวัด
# =====================================================
if province_col:
    province_list = sorted(filtered_df[province_col].dropna().unique())
    selected_province = st.sidebar.multiselect(
        "3️⃣ เลือกจังหวัด",
        province_list,
        default=province_list
    )
    filtered_df = filtered_df[filtered_df[province_col].isin(selected_province)]

# =====================================================
# 📊 EXECUTIVE SUMMARY
# =====================================================
st.header("📊 Executive Summary")

col1, col2, col3 = st.columns(3)

col1.metric("จำนวนข้อมูลทั้งหมด", len(filtered_df))
col2.metric("จำนวน Sheet ที่เลือก", len(selected_sheets))

if province_col:
    col3.metric("จำนวนจังหวัด", filtered_df[province_col].nunique())

st.divider()

# =====================================================
# 🧠 วิเคราะห์แนวโน้ม
# =====================================================
if date_col:

    trend_df = (
        filtered_df
        .groupby(["Sheet", filtered_df[date_col].dt.date])
        .size()
        .reset_index(name="จำนวน")
    )

    st.subheader("🧠 วิเคราะห์แนวโน้มล่าสุด")

    for sheet in selected_sheets:
        sheet_data = trend_df[trend_df["Sheet"] == sheet].sort_values(date_col)

        if len(sheet_data) >= 2:
            last = sheet_data["จำนวน"].iloc[-1]
            prev = sheet_data["จำนวน"].iloc[-2]

            change = last - prev
            percent = (change / prev * 100) if prev != 0 else 0

            if change > 0:
                status = "🟢 เพิ่มขึ้น"
            elif change < 0:
                status = "🔴 ลดลง"
            else:
                status = "🟡 คงที่"

            st.markdown(f"**{sheet}** : {status} {change:+} ({percent:.1f}%)")

    fig_trend = px.line(
        trend_df,
        x=date_col,
        y="จำนวน",
        color="Sheet",
        markers=True,
        color_discrete_sequence=px.colors.sequential.Teal
    )

    st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# =====================================================
# 📊 ตารางข้อมูล
# =====================================================
st.dataframe(filtered_df, use_container_width=True)
