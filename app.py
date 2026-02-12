import streamlit as st
import pandas as pd

st.set_page_config(page_title="Google Sheets Multi-Sheet Dashboard", layout="wide")
st.title("📊 Dashboard จาก Google Sheets")

# ----------------------------
# Google Sheet Link Setup
# ----------------------------
sheet_url = "https://docs.google.com/spreadsheets/d/1Y4FANer87OduQcK7XctCjJ0FBEKTHlXJ4aMZklcqzFU/edit?usp=sharing"
spreadsheet_id = sheet_url.split("/d/")[1].split("/")[0]

# ----------------------------
# รับชื่อ sheet จาก user
# ----------------------------
st.sidebar.header("เลือก sheet")
user_sheet = st.sidebar.text_input("พิมพ์ชื่อ sheet ที่ต้องการดู (ตรงกับชื่อ tab)")

if user_sheet:
    try:
        # แปลง link เป็น CSV URL
        csv_url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet={user_sheet}"

        # อ่าน sheet
        df = pd.read_csv(csv_url)
        df.columns = df.columns.str.strip()
        st.success(f"โหลด sheet '{user_sheet}' สำเร็จ ✅")

        # ------------------------
        # แสดงข้อมูล + ตัวกรอง
        # ------------------------
        st.subheader("📋 ตารางข้อมูล")
        st.dataframe(df, use_container_width=True)

        # ------------------------
        # เลือกคอลัมน์กรอง
        # ------------------------
        st.sidebar.header("กรองข้อมูล")
        filter_col = st.sidebar.selectbox("เลือกคอลัมน์สำหรับกรอง", df.columns)

        if df[filter_col].dtype == "object":
            options = st.sidebar.multiselect(
                f"เลือกค่าจาก {filter_col}", df[filter_col].dropna().unique()
            )
            if options:
                df = df[df[filter_col].isin(options)]
        else:
            st.sidebar.write("ช่วงตัวเลข")
            min_val, max_val = float(df[filter_col].min()), float(df[filter_col].max())
            range_val = st.sidebar.slider("ช่วงตัวเลข", min_val, max_val, (min_val, max_val))
            df = df[(df[filter_col] >= range_val[0]) & (df[filter_col] <= range_val[1])]

        # ------------------------
        # แสดงตารางที่กรองแล้ว
        # ------------------------
        st.subheader("📈 ตารางข้อมูลกรองแล้ว")
        st.dataframe(df, use_container_width=True)

    except Exception as e:
        st.error("❌ ไม่สามารถโหลด sheet นี้ได้ - ตรวจสอบชื่อ sheet อีกครั้ง")
        st.write(e)
else:
    st.info("➡️ โปรดพิมพ์ชื่อ sheet ที่ต้องการแสดง")
