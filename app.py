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

# Load selected file
if selected_history_file:
    df = pd.read_excel(os.path.join(DATA_DIR, selected_history_file))

    st.title("📊 Samadhaan Grievance Dashboard")
    st.caption(f"Data Source: `{selected_history_file}`")

    # KPIs
    st.subheader("📌 Key Metrics")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Grievances", len(df))
    with col2:
        st.metric("Pending > 10 days", df[df['Pending Days'] > 10].shape[0])
    with col3:
        st.metric("Max Pending Days", df['Pending Days'].max())

    # Filters
    st.sidebar.title("🔍 Filters")
    if 'Pending with' in df.columns:
        departments = df['Pending with'].dropna().unique()
        selected_dept = st.sidebar.selectbox("Select Department", options=["All"] + list(departments))
        if selected_dept != "All":
            df = df[df['Pending with'] == selected_dept]

    # Charts
    st.subheader("📈 Grievances by Department")
    if 'Pending with' in df.columns:
        dept_counts = df['Pending with'].value_counts().reset_index()
        fig_bar = px.bar(dept_counts, x='index', y='Pending with',
                         labels={'index': 'Department', 'Pending with': 'Grievances'})
        st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("🗂️ Grievance Table")
    st.dataframe(df)

else:
    st.info("👆 Upload a file or select one from history to view the dashboard.")