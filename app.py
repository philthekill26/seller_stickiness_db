import streamlit as st
from pages.dashboard import main_dashboard
from pages.reports import reports_page

# Set page config
st.set_page_config(page_title="Seller Stickiness Dashboard", page_icon="logo.png", layout="wide")

# Custom CSS for FastSpring Theme
st.markdown(
    """
    <style>
        /* Sidebar Styling */
        [data-testid="stSidebar"] {
            background-color: #FFA500 !important; /* FastSpring Orange */
            color: white !important;
            padding: 20px;
        }
        [data-testid="stSidebarNav"] a {
            color: black !important;
            font-weight: bold;
            font-size: 16px;
            text-decoration: none;
            padding: 12px;
            display: block;
            border-radius: 8px;
            transition: background 0.3s ease-in-out;
        }
        [data-testid="stSidebarNav"] a:hover {
            background-color: #E69500 !important; /* Darker Orange */
        }

        /* Main content background */
        .stApp {
            background-color: #FFFFFF !important; /* White */
        }

        /* Header Styling */
        .stTitle {
            color: #1F1F1F !important; /* Dark Text */
            font-weight: bold;
            font-size: 30px !important;
            text-align: center;
        }

        /* Metric Cards */
        .stMetric {
            background: #FFA500;
            color: white;
            padding: 15px;
            border-radius: 8px;
            box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.1);
            font-size: 18px;
            font-weight: bold;
            text-align: center;
        }

        /* Data Table Styling */
        .stDataFrame {
            border-radius: 8px;
            border: 1px solid #E69500;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Sidebar navigation
st.sidebar.title("📌 Navigation")
page = st.sidebar.radio("Go to:", ["📊 Main Dashboard", "📑 Reports & Recommendations"])

# Load the selected page
if page == "📊 Main Dashboard":
    main_dashboard()
elif page == "📑 Reports & Recommendations":
    reports_page()
