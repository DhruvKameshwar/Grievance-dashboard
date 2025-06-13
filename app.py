import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime

st.set_page_config(page_title="Grievance Dashboard", layout="wide")

DATA_DIR = "dashboard_data"
os.makedirs(DATA_DIR, exist_ok=True)

st.sidebar.title("📁 Upload Data File")
uploaded_file = st.sidebar.file_uploader("Upload an Excel file", type=["xlsx", "xls"])

# Save new upload
if uploaded_file:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"{timestamp}_{uploaded_file.name}"
    save_path = os.path.join(DATA_DIR, file_name)
    with open(save_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    st.success(f"✅ Uploaded: {uploaded_file.name}")

# History dropdown
st.sidebar.title("📂 Dashboard History")
file_list = sorted(os.listdir(DATA_DIR), reverse=True)
selected_history_file = st.sidebar.selectbox("Select a past dashboard", file_list)

# Load and process the selected file
if selected_history_file:
    try:
        df = pd.read_excel(os.path.join(DATA_DIR, selected_history_file))

        # Clean column names
        df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_')
        print(df.columns)

        # --- FIX START ---

        # 1. Make the 'pending_days' column robustly numeric.
        #    'errors='coerce'' will turn any non-numeric values into Not a Number (NaN).
        if 'Pending_Days' in df.columns:
            df['Pending_Days'] = pd.to_numeric(df['Pending_Days'], errors='coerce')

        # 2. Convert all remaining object columns to strings to prevent serialization errors.
        #    This is the primary fix for the ArrowTypeError.
        for col in df.select_dtypes(include=['object']).columns:
            df[col] = df[col].astype(str)

        # --- FIX END ---


        st.title("📊 Samadhaan Grievance Dashboard")
        st.caption(f"Data Source: `{selected_history_file}`")

        # KPIs (now more robust)
        st.subheader("📌 Key Metrics")
        col1, col2, col3 = st.columns(3)

        col1.metric("Total Grievances", len(df))

        if 'Pending_Days' in df.columns:
            # Drop rows where 'pending_days' could not be converted to a number
            df.dropna(subset=['Pending_Days'], inplace=True)
            df['Pending_Days'] = df['Pending_Days'].astype(int)

            pending_over_10 = df[df['pending_days'] > 10].shape[0]
            max_pending = df['Pending_Days'].max()
            
            col2.metric("Pending > 10 days", pending_over_10)
            col3.metric("Max Pending Days", max_pending)
        else:
            col2.metric("Pending > 10 days", "N/A")
            col3.metric("Max Pending Days", "N/A")
            st.warning("⚠️ Column 'pending_days' not found. Cannot calculate pending metrics.")


        # Filters
        st.sidebar.title("🔍 Filters")
        if 'pending_with_section' in df.columns:
            # Ensure filter column is available after data cleaning
            departments = df['pending_with_section'].dropna().unique()
            print(departments)
            selected_dept = st.sidebar.selectbox("Select Department", options=["All"] + list(departments))
            print(selected_dept)
            if selected_dept != "All":
                df = df[df['pending_with_section'] == selected_dept]

        # Charts
        st.subheader("📈 Grievances by Department")
        if 'pending_with_section' in df.columns and not df.empty:
            dept_counts = df['pending_with_section'].value_counts().reset_index()
            print(dept_counts)
            dept_counts.columns = ['Department', 'Grievances'] # Rename for clarity
            print(dept_counts)
            fig_bar = px.bar(dept_counts, x='Department', y='Grievances',
                             labels={'Department': 'Department', 'Grievances': 'Number of Grievances'})
            st.plotly_chart(fig_bar, use_container_width=True)

        st.subheader("🗂️ Grievance Table")
        st.dataframe(df)

    except Exception as e:
        st.error(f"An error occurred while processing the file: {e}")

else:
    st.info("👆 Upload a file or select one from history to view the dashboard.")
