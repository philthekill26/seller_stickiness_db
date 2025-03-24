
import pandas as pd
import streamlit as st
import plotly.express as px
import sqlite3

# Function to categorize stickiness score
def categorise_stickiness(score):
    if score >= 75:
        return "High"
    elif 50 <= score < 75:
        return "Moderate"
    elif 25 <= score < 50:
        return "Low"
    else:
        return "Critical"

# Function to load seller data from database
@st.cache_data
def load_data_from_db(sheet_name):
    conn = sqlite3.connect("stickiness_data.db")
    data = pd.read_sql(f"SELECT * FROM {sheet_name}", conn)
    conn.close()

    # Normalize column names
    data.columns = data.columns.str.strip().str.lower()
    data.rename(columns={"company_id": "Company ID", "csm": "CSM"}, inplace=True)

    if "overall_score" in data.columns:
        if data["overall_score"].max() <= 1:
            data["overall_score"] *= 100
        data["overall_score"] = data["overall_score"].round(2)
        data["Stickiness Category"] = data["overall_score"].apply(categorise_stickiness)

    return data

# Main Dashboard Function
def main_dashboard():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Luckiest+Guy&display=swap');

            body { font-family: 'Arial', sans-serif; }
            .stApp { color: black; background-color: #FFFFFF; }
            .stTitle { color: #1F1F1F; font-weight: bold; font-size: 28px; }
            .stDataFrame { background-color: #FFA500; color: black; }
            div.stButton > button:first-child {
                background-color: #FFA500;
                color: black;
                border-radius: 10px;
                transition: 0.3s;
            }
            div.stButton > button:hover {
                background-color: #FF7400;
                color: white;
            }
        </style>
    """, unsafe_allow_html=True)

    st.title("📊 Seller Stickiness Dashboard")

    # Sheet selection dropdown
    sheet_options = {
        "Technical Stickiness": "technical_stickiness",
        "Seller Tech Stacks": "seller_tech_stacks",
        "Webhooks": "webhooks",
        "API Stickiness Matrix": "api_stickiness"
    }
    selected_sheet = st.selectbox("Select Data Sheet:", list(sheet_options.keys()))
    sheet_name = sheet_options[selected_sheet]

    # Load data from selected sheet
    data = load_data_from_db(sheet_name)

    if not data.empty:
        st.subheader(f"🔍 Data from {selected_sheet}")
        with st.expander("🔍 View Full Data Table"):
            st.dataframe(data)

        if "Stickiness Category" in data.columns:
            st.subheader("📌 Summary Metrics")
            categories = ["Critical", "Low", "Moderate", "High"]
            category_counts = [len(data[data["Stickiness Category"] == cat]) for cat in categories]

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Critical Companies", category_counts[0])
            col2.metric("Low Companies", category_counts[1])
            col3.metric("Moderate Companies", category_counts[2])
            col4.metric("High Companies", category_counts[3])

            fig = px.bar(
                x=categories,
                y=category_counts,
                labels={"x": "Stickiness Category", "y": "Number of Sellers"},
                title="Stickiness Distribution",
            )
            fig.update_traces(marker_color="#FF7400", hoverinfo="x+y")
            st.plotly_chart(fig)

        # Search Bar
        search_col1, search_col2 = st.columns(2)
        with search_col1:
            search_query = st.text_input("🔍 Search by Company ID:")
        with search_col2:
            search_csm = st.text_input("🔍 Search by CSM:")

        # Apply search filters
        filtered_data = data.copy()
        if search_query:
            filtered_data = filtered_data[
                filtered_data["Company ID"].astype(str).str.contains(search_query, case=False, na=False)
            ]

        if search_csm:
            filtered_data = filtered_data[
                filtered_data["CSM"].astype(str).str.contains(search_csm, case=False, na=False)
            ]

        st.dataframe(filtered_data)

        # Filters (only if columns exist in the selected sheet)
        selected_vertical = "All"
        if "vertical" in data.columns:
            st.subheader("📂 Filter by Vertical")
            verticals = data["vertical"].dropna().unique()
            selected_vertical = st.selectbox("Select a Vertical:", ["All"] + list(verticals))

        selected_stickiness = "All"
        if "Stickiness Category" in data.columns:
            st.subheader("📂 Filter by Stickiness Category")
            selected_stickiness = st.selectbox("Select a Stickiness Category:", ["All"] + categories)

        # Apply Filters
        if selected_vertical != "All" and "vertical" in filtered_data.columns:
            filtered_data = filtered_data[filtered_data["vertical"] == selected_vertical]

        if selected_stickiness != "All" and "Stickiness Category" in filtered_data.columns:
            filtered_data = filtered_data[filtered_data["Stickiness Category"] == selected_stickiness]

        # Display Filtered Data
        if not filtered_data.empty:
            display_columns = []
            if selected_sheet != "Webhooks":
                display_columns.append("Company ID")
            if "Stickiness Category" in filtered_data.columns:
                display_columns.append("Stickiness Category")
            if "vertical" in filtered_data.columns:
                display_columns.append("vertical")

            st.write("### Filtered for Company IDs")
            st.dataframe(filtered_data[display_columns])
        else:
            st.warning("⚠️ No matching results found based on selected filters.")
