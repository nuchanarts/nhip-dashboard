import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import json
from urllib.parse import quote

st.set_page_config(page_title="NHIP Executive Dashboard", layout="wide")

st.title("🏥 NHIP Executive Dashboard")

SPREADSHEET_ID = "1Y4FANer87OduQcK7XctCjJ0FBEKTHlXJ4aMZklcqzFU"

# ==============================
# โหลดรายชื่อ Sheet
# ==============================
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
    except:
        return []

# ==============================
# โหลดข้อมูลทุก Sheet
# ==============================
@st.cache_data(ttl=300)
def load_all_sheets():
    sheet_list = get_sheet_names()
    all_dfs = []

    if not sheet_list:
        return None

    for sheet in sheet_list:
        try:
            encoded_sheet = quote(sheet)
            url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={encoded_sheet}"
            df = pd.read_csv(url)
            if not df.empty:
                df.columns = df.columns.str.strip()
                df["Sheet"] = sheet
                all_dfs.append(df)
        except:
            continue

    if len(all_dfs) == 0:
        return None

    return pd.concat(all_dfs, ignore_index=True)

df = load_all_sheets()

# ==============================
# ถ้าโหลดไม่ได้
# ==============================
if df is None:
    st.error("❌ ไม่สามารถโหลดข้อมูลจาก Google Sheet ได้")
    st.info("กรุณาตรวจสอบว่า Google Sheet เปิดเป็น 'Anyone with the link → Viewer'")
    st.stop()

# ==============================
# ตรวจจับคอลัมน์
# ==============================
zone_col = next((c for c in df.columns if "เขต" in c), None)
province_col = next((c for c in df.columns if "จังหวัด" in c), None)
date_col = next((c for c in df.columns if "วัน" in c or "date" in c.lower()), None)

if date_col:
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

# ==============================
# Sidebar Filters
# ==============================
st.sidebar.header("📊 ตัวกรองข้อมูล")

filtered_df = df.copy()

if zone_col:
    zone_list = sorted(df[zone_col].dropna().unique())
    selected_zone = st.sidebar.multiselect(
        "เลือกเขต",
        zone_list,
        default=zone_list
    )
    filtered_df = filtered_df[filtered_df[zone_col].isin(selected_zone)]

if province_col:
    province_list = sorted(filtered_df[province_col].dropna().unique())
    selected_province = st.sidebar.multiselect(
        "เลือกจังหวัด",
        province_list,
        default=province_list
    )
    filtered_df = filtered_df[filtered_df[province_col].isin(selected_province)]

# ==============================
# Executive Summary
# ==============================
st.header("📊 Executive Summary")

col1, col2, col3 = st.columns(3)

col1.metric("จำนวนข้อมูลทั้งหมด", len(filtered_df))

if province_col:
    col2.metric("จำนวนจังหวัด", filtered_df[province_col].nunique())

col3.metric("จำนวน Sheet ทั้งหมด", filtered_df["Sheet"].nunique())

# ==============================
# แนวโน้ม
# ==============================
if date_col:

    trend_df = (
        filtered_df
        .groupby(["Sheet", filtered_df[date_col].dt.date])
        .size()
        .reset_index(name="จำนวน")
    )

    st.subheader("🧠 วิเคราะห์แนวโน้มล่าสุด")

    for sheet in trend_df["Sheet"].unique():
        sheet_data = trend_df[trend_df["Sheet"] == sheet].sort_values(date_col)

        if len(sheet_data) >= 2:
            last = sheet_data["จำนวน"].iloc[-1]
            prev = sheet_data["จำนวน"].iloc[-2]

            change = last - prev

            if change > 0:
                status = "🟢 เพิ่มขึ้น"
            elif change < 0:
                status = "🔴 ลดลง"
            else:
                status = "🟡 คงที่"

            st.markdown(f"**{sheet}** : {status} {change:+}")

    fig = px.line(
        trend_df,
        x=date_col,
        y="จำนวน",
        color="Sheet",
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)

st.divider()
st.dataframe(filtered_df, use_container_width=True)
