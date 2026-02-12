import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="Thailand Map Dashboard", layout="wide")

st.title("🇹🇭 Dashboard แผนที่ประเทศไทย")

uploaded_file = st.file_uploader("📂 อัปโหลดไฟล์ Excel หรือ CSV", type=["xlsx", "csv"])

if uploaded_file:

    # -------------------------
    # อ่านไฟล์
    # -------------------------
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df.columns = df.columns.str.strip()

    st.success("โหลดไฟล์สำเร็จ ✅")

    # -------------------------
    # เลือกคอลัมน์
    # -------------------------
    st.sidebar.header("⚙️ ตั้งค่า")

    zone_col = st.sidebar.selectbox("เลือกคอลัมน์เขต", df.columns)
    province_col = st.sidebar.selectbox("เลือกคอลัมน์จังหวัด", df.columns)

    # -------------------------
    # Filter เขต
    # -------------------------
    st.sidebar.header("🔎 กรองข้อมูล")

    zone_filter = st.sidebar.multiselect(
        "เลือกเขต",
        df[zone_col].dropna().unique(),
        default=df[zone_col].dropna().unique()
    )

    filtered_df = df[df[zone_col].isin(zone_filter)]

    # -------------------------
    # สรุปจำนวนต่อจังหวัด
    # -------------------------
    summary = (
        filtered_df
        .groupby(province_col)
        .size()
        .reset_index(name="จำนวน")
    )

    # -------------------------
    # โหลด GeoJSON แผนที่ไทย
    # -------------------------
    geojson_url = "https://raw.githubusercontent.com/apisit/thailand.json/master/thailand.json"
    geojson = requests.get(geojson_url).json()

    # -------------------------
    # สร้างแผนที่
    # -------------------------
    fig = px.choropleth(
        summary,
        geojson=geojson,
        locations=province_col,
        featureidkey="properties.name",
        color="จำนวน",
        color_continuous_scale="Reds",
    )

    fig.update_geos(fitbounds="locations", visible=False)

    fig.update_layout(
        margin={"r":0,"t":0,"l":0,"b":0}
    )

    st.plotly_chart(fig, use_container_width=True)

    # -------------------------
    # KPI
    # -------------------------
    st.divider()

    col1, col2 = st.columns(2)
    col1.metric("จำนวนทั้งหมด", len(filtered_df))
    col2.metric("จำนวนจังหวัดที่มีข้อมูล", summary[province_col].nunique())

else:
    st.info("⬆️ กรุณาอัปโหลดไฟล์ที่มีคอลัมน์ เขต และ จังหวัด")
