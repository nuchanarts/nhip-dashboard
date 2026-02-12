import streamlit as st
import pandas as pd
import plotly.express as px
import requests

st.set_page_config(page_title="Thailand Map Dashboard", layout="wide")

st.title("🇹🇭 NHIP Thailand Map Dashboard")

# ==============================
# 🔗 เชื่อม Google Sheet
# ==============================

SPREADSHEET_ID = "1Y4FANer87OduQcK7XctCjJ0FBEKTHlXJ4aMZklcqzFU"
GID = "0"

csv_url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"

try:
    df = pd.read_csv(csv_url)
    df.columns = df.columns.str.strip()
    st.success("เชื่อม Google Drive สำเร็จ ✅")
except:
    st.error("❌ เชื่อม Google Sheet ไม่ได้ ตรวจสอบการแชร์เป็น Anyone with the link → Viewer")
    st.stop()

# ==============================
# 🎛 เลือกคอลัมน์
# ==============================

st.sidebar.header("⚙️ ตั้งค่า")

zone_col = st.sidebar.selectbox("เลือกคอลัมน์เขต", df.columns)
province_col = st.sidebar.selectbox("เลือกคอลัมน์จังหวัด", df.columns)

# ==============================
# 🔎 Filter เขต
# ==============================

zone_filter = st.sidebar.multiselect(
    "เลือกเขต",
    df[zone_col].dropna().unique(),
    default=df[zone_col].dropna().unique()
)

filtered_df = df[df[zone_col].isin(zone_filter)]

# ==============================
# 📊 สรุปจำนวนต่อจังหวัด
# ==============================

summary = (
    filtered_df
    .groupby(province_col)
    .size()
    .reset_index(name="จำนวน")
)

# ==============================
# 🧠 ทำความสะอาดชื่อจังหวัด (กัน error)
# ==============================

summary[province_col] = summary[province_col].str.replace("จังหวัด", "", regex=False)
summary[province_col] = summary[province_col].str.strip()

# แปลงชื่อพิเศษ
summary[province_col] = summary[province_col].replace({
    "กทม": "กรุงเทพมหานคร",
    "กรุงเทพ": "กรุงเทพมหานคร"
})

# ==============================
# 🗺 โหลด GeoJSON
# ==============================

geojson_url = "https://raw.githubusercontent.com/apisit/thailand.json/master/thailand.json"
geojson = requests.get(geojson_url).json()

# ==============================
# 🗺 สร้างแผนที่
# ==============================

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

# ==============================
# 📈 KPI
# ==============================

st.divider()

col1, col2 = st.columns(2)
col1.metric("จำนวนทั้งหมด", len(filtered_df))
col2.metric("จำนวนจังหวัดที่มีข้อมูล", summary[province_col].nunique())
