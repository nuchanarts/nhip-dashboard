import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
from urllib.parse import quote

# =============================
# App Setup
# =============================
st.set_page_config(page_title="NHIP Executive Dashboard", layout="wide")
st.title("🏥 NHIP Executive Dashboard")

SPREADSHEET_ID = "1Y4FANer87OduQcK7XctCjJ0FBEKTHlXJ4aMZklcqzFU"

# =============================
# Load Sheet Names
# =============================
@st.cache_data(ttl=300)
def get_sheet_names():
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:json"
        res = requests.get(url)
        text = res.text
        json_str = text[text.find("{"):text.rfind("}")+1]
        data = json.loads(json_str)
        sheets = data.get("sheets", [])
        return [s["properties"]["title"] for s in sheets]
    except Exception as e:
        return []

sheet_list = get_sheet_names()

if not sheet_list:
    st.error("❌ ไม่สามารถอ่านรายชื่อ sheet ได้")
    st.stop()

# =============================
# Load All Sheets Data
# =============================
@st.cache_data(ttl=300)
def load_all_sheets():
    sheet_names = get_sheet_names()
    all_dataframes = []
    for sheet in sheet_names:
        try:
            encoded = quote(sheet)
            url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded}"
            temp_df = pd.read_csv(url)
            if temp_df.shape[0] > 0:
                temp_df.columns = temp_df.columns.str.strip()
                temp_df["Sheet"] = sheet
                all_dataframes.append(temp_df)
        except Exception as e:
            continue
    if not all_dataframes:
        return None
    return pd.concat(all_dataframes, ignore_index=True)

df = load_all_sheets()
if df is None:
    st.error("❌ ไม่พบข้อมูลจาก sheet ใด ๆ")
    st.stop()

# =============================
# Detect Columns
# =============================
zone_col    = next((c for c in df.columns if "เขต"      in c), None)
province_col= next((c for c in df.columns if "จังหวัด"  in c), None)
date_col    = next((c for c in df.columns if "วัน" in c or "date" in c.lower()), None)

if date_col:
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

# =============================
# Sidebar Filters
# =============================
st.sidebar.header("🔎 ตัวกรองข้อมูล")

filtered_df = df.copy()

# Filter by Zone
if zone_col:
    zones = sorted(df[zone_col].dropna().unique())
    selected_zones = st.sidebar.multiselect("เลือกเขต", zones, default=zones)
    filtered_df = filtered_df[filtered_df[zone_col].isin(selected_zones)]

# Filter by Province
if province_col:
    provinces = sorted(filtered_df[province_col].dropna().unique())
    selected_provinces = st.sidebar.multiselect("เลือกจังหวัด", provinces, default=provinces)
    filtered_df = filtered_df[filtered_df[province_col].isin(selected_provinces)]

# =============================
# Executive Summary
# =============================
st.header("📊 Executive Summary")

col1, col2, col3 = st.columns(3)

col1.metric("จำนวนรายการทั้งหมด", len(filtered_df))
if province_col:
    col2.metric("จำนวนจังหวัดที่มีข้อมูล", filtered_df[province_col].nunique())
col3.metric("จำนวน Sheet ที่มีข้อมูล", filtered_df["Sheet"].nunique())

st.divider()

# =============================
# Trend Analysis
# =============================
if date_col:
    st.subheader("🧠 วิเคราะห์แนวโน้มอัตโนมัติ")

    trend_df = (
        filtered_df
        .groupby(["Sheet", filtered_df[date_col].dt.date])
        .size()
        .reset_index(name="จำนวน")
    )

    for sheet in trend_df["Sheet"].unique():
        sheet_data = trend_df[trend_df["Sheet"] == sheet].sort_values(date_col)
        if len(sheet_data) >= 2:
            last  = sheet_data["จำนวน"].iloc[-1]
            prev  = sheet_data["จำนวน"].iloc[-2]
            diff  = last - prev
            pct   = (diff / prev * 100) if prev != 0 else 0

            status = "🟡 คงที่"
            if diff > 0:
                status = "🟢 เพิ่มขึ้น"
            elif diff < 0:
                status = "🔴 ลดลง"

            st.markdown(f"• **{sheet}** : {status} {diff:+} ({pct:.1f}%)")

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

# =============================
# Full Table
# =============================
st.subheader("📋 ตารางข้อมูลที่กรองแล้ว")
st.dataframe(filtered_df, use_container_width=True)

st.download_button(
    label="📥 ดาวน์โหลด CSV",
    data=filtered_df.to_csv(index=False).encode("utf-8"),
    file_name="NHIP_filtered_data.csv",
    mime="text/csv"
)
