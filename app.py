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

# ===============================
# โหลดชื่อ Sheet
# ===============================
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

selected_sheets = st.sidebar.multiselect(
    "📄 เลือก Sheet",
    sheet_list,
    default=sheet_list[:1]
)

# ===============================
# โหลดข้อมูล
# ===============================
@st.cache_data(ttl=300)
def load_sheet(sheet):
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={sheet}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df["Sheet"] = sheet
    return df

dfs = [load_sheet(s) for s in selected_sheets]

if not dfs:
    st.stop()

df = pd.concat(dfs, ignore_index=True)

# ตรวจจับคอลัมน์
zone_col = next((c for c in df.columns if "เขต" in c), None)
province_col = next((c for c in df.columns if "จังหวัด" in c), None)
date_col = next((c for c in df.columns if "วัน" in c or "date" in c.lower()), None)

if date_col:
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

# ===============================
# 🔎 ตัวกรอง
# ===============================
filtered_df = df.copy()

if zone_col:
    selected_zone = st.sidebar.multiselect(
        "เลือกเขต",
        df[zone_col].dropna().unique(),
        default=df[zone_col].dropna().unique()
    )
    filtered_df = filtered_df[filtered_df[zone_col].isin(selected_zone)]

if province_col:
    selected_province = st.sidebar.multiselect(
        "เลือกจังหวัด",
        filtered_df[province_col].dropna().unique(),
        default=filtered_df[province_col].dropna().unique()
    )
    filtered_df = filtered_df[filtered_df[province_col].isin(selected_province)]

# =====================================================
# 📊 EXECUTIVE SUMMARY
# =====================================================

st.header("📊 Executive Summary")

col1, col2, col3, col4 = st.columns(4)

total_records = len(filtered_df)
sheet_summary = filtered_df.groupby("Sheet").size().reset_index(name="จำนวน")
top_sheet = sheet_summary.sort_values("จำนวน", ascending=False).iloc[0]["Sheet"]

col1.metric("จำนวนรวมทั้งหมด", total_records)
col2.metric("Sheet สูงสุด", top_sheet)
col3.metric("จำนวน Sheet ที่เลือก", len(selected_sheets))

if province_col:
    col4.metric("จังหวัดทั้งหมด", filtered_df[province_col].nunique())

st.divider()

# =====================================================
# 🧠 วิเคราะห์แนวโน้มอัตโนมัติ
# =====================================================

st.header("🧠 Automatic Trend Analysis")

if date_col:

    trend_df = (
        filtered_df
        .groupby(["Sheet", filtered_df[date_col].dt.date])
        .size()
        .reset_index(name="จำนวน")
    )

    insights = []

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

            insights.append(f"• **{sheet}** : {status} {change:+} ({percent:.1f}%)")

    for i in insights:
        st.markdown(i)

    st.divider()

    # กราฟแนวโน้ม
    fig_trend = px.line(
        trend_df,
        x=date_col,
        y="จำนวน",
        color="Sheet",
        markers=True,
        color_discrete_sequence=px.colors.sequential.Teal
    )

    st.plotly_chart(fig_trend, use_container_width=True)

# =====================================================
# 📊 เปรียบเทียบจังหวัด
# =====================================================

if province_col:
    compare_df = (
        filtered_df
        .groupby(["Sheet", province_col])
        .size()
        .reset_index(name="จำนวน")
    )

    fig_compare = px.bar(
        compare_df,
        x=province_col,
        y="จำนวน",
        color="Sheet",
        barmode="group",
        color_discrete_sequence=px.colors.sequential.Mint
    )

    st.header("📊 เปรียบเทียบตามจังหวัด")
    st.plotly_chart(fig_compare, use_container_width=True)

st.divider()

st.dataframe(filtered_df, use_container_width=True)
