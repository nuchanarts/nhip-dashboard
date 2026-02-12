import streamlit as st
import pandas as pd
import plotly.express as px
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import TableStyle
from io import BytesIO

st.set_page_config(page_title="NHIP Smart Dashboard", layout="wide")

st.title("📊 NHIP Smart Auto Dashboard")

# ==============================
# 🔗 Google Sheet Config
# ==============================

SPREADSHEET_ID = "1Y4FANer87OduQcK7XctCjJ0FBEKTHlXJ4aMZklcqzFU"
GID = "0"

# ==============================
# 🔄 Load Data (Auto refresh ทุก 5 นาที)
# ==============================

@st.cache_data(ttl=300)
def load_data():
    url = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid={GID}"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
    st.success("เชื่อม Google Drive สำเร็จ ✅ (Auto refresh ทุก 5 นาที)")
except Exception as e:
    st.error("❌ เชื่อมไม่ได้ กรุณาตรวจสอบว่าแชร์แบบ Anyone with the link → Viewer")
    st.stop()

# ==============================
# 🧠 Auto Detect Columns
# ==============================

date_col = None
province_col = None
category_col = None
numeric_col = None

for col in df.columns:
    if "วัน" in col or "date" in col.lower():
        date_col = col
    elif "จังหวัด" in col or "province" in col.lower():
        province_col = col
    elif pd.api.types.is_numeric_dtype(df[col]) and not numeric_col:
        numeric_col = col
    elif df[col].dtype == "object" and not category_col:
        category_col = col

if date_col:
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")

# ==============================
# 🎛 Filters
# ==============================

st.sidebar.header("🔎 ตัวกรองข้อมูล")

filtered_df = df.copy()

if province_col:
    provinces = df[province_col].dropna().unique()
    province_filter = st.sidebar.multiselect(
        "เลือกจังหวัด", provinces, default=provinces
    )
    filtered_df = filtered_df[filtered_df[province_col].isin(province_filter)]

if category_col:
    categories = filtered_df[category_col].dropna().unique()
    category_filter = st.sidebar.multiselect(
        f"เลือก {category_col}", categories, default=categories
    )
    filtered_df = filtered_df[filtered_df[category_col].isin(category_filter)]

# ==============================
# 📊 KPI Section
# ==============================

st.divider()

col1, col2, col3 = st.columns(3)

col1.metric("จำนวนรายการทั้งหมด", len(filtered_df))

if province_col:
    col2.metric("จำนวนจังหวัด", filtered_df[province_col].nunique())
else:
    col2.metric("จำนวนคอลัมน์", len(filtered_df.columns))

if numeric_col:
    col3.metric("ผลรวมตัวเลข", round(filtered_df[numeric_col].sum(), 2))
else:
    col3.metric("จำนวนประเภท", filtered_df[category_col].nunique() if category_col else "-")

st.divider()

# ==============================
# 📈 Charts
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
        fig1 = px.line(
            trend_df,
            x=date_col,
            y="จำนวน",
            markers=True,
            template="plotly_white"
        )
        col_left.plotly_chart(fig1, use_container_width=True)

if province_col:
    bar_df = (
        filtered_df
        .groupby(province_col)
        .size()
        .reset_index(name="จำนวน")
        .sort_values("จำนวน", ascending=False)
    )

    fig2 = px.bar(
        bar_df,
        x=province_col,
        y="จำนวน",
        template="plotly_white"
    )
    col_right.plotly_chart(fig2, use_container_width=True)

st.divider()

# ==============================
# 📋 Data Table
# ==============================

with st.expander("📋 ดูข้อมูลทั้งหมด"):
    st.dataframe(filtered_df, use_container_width=True)

# ==============================
# 📄 Export PDF
# ==============================

def generate_pdf(dataframe):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer)
    elements = []

    styles = getSampleStyleSheet()
    elements.append(Paragraph("NHIP Dashboard Report", styles["Title"]))
    elements.append(Spacer(1, 0.5 * inch))

    table_data = [dataframe.columns.tolist()] + dataframe.head(20).values.tolist()

    table = Table(table_data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR',(0,0),(-1,0),colors.whitesmoke),
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
        ('FONTSIZE', (0,0), (-1,-1), 8),
    ]))

    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer

pdf_file = generate_pdf(filtered_df)

st.download_button(
    label="📄 ดาวน์โหลดรายงาน PDF",
    data=pdf_file,
    file_name="NHIP_Report.pdf",
    mime="application/pdf"
)
