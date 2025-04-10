import pandas as pd
import streamlit as st
import sqlite3
from fpdf import FPDF

# Connect to the SQLite database
def load_data_from_db():
    conn = sqlite3.connect("stickiness_data.db")
    data = pd.read_sql("SELECT * FROM technical_stickiness", conn)
    conn.close()
    return data

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

# Function to rank features based on adoption rate
def rank_features(data, feature_columns):
    feature_counts = data[feature_columns].apply(lambda col: (col == "Yes").sum())
    sorted_features = feature_counts.sort_values(ascending=False)
    high_threshold = sorted_features.quantile(0.75)
    medium_threshold = sorted_features.quantile(0.50)

    ranked_features = {
        "High": sorted_features[sorted_features >= high_threshold].index.tolist(),
        "Medium": sorted_features[(sorted_features < high_threshold) & (sorted_features >= medium_threshold)].index.tolist(),
        "Low": sorted_features[sorted_features < medium_threshold].index.tolist()
    }
    return ranked_features

# Function to generate detailed recommendations based on missing features, API, and webhook usage
def generate_recommendations(row, ranked_features, data):
    recommendations = {"High": [], "Medium": [], "Low": []}
    vertical = row.get("vertical", "Unknown")

    for rank, features in ranked_features.items():
        for feature in features:
            if row.get(feature, "No") == "No":
                enabled_sellers = data[data[feature] == "Yes"]["Company ID"].dropna().unique()
                enabled_sellers_vertical = data[(data[feature] == "Yes") & (data["vertical"] == vertical)]["Company ID"].dropna().unique()

                recommendation_text = f"- {feature.replace('_', ' ').title()}"
                if len(enabled_sellers) > 0:
                    recommendation_text += f" (Enabled by: {', '.join(map(str, enabled_sellers[:2]))})"
                if len(enabled_sellers_vertical) > 0:
                    recommendation_text += f" | Vertical: {', '.join(map(str, enabled_sellers_vertical[:2]))}"

                recommendations[rank].append(recommendation_text)

    # API & Webhook Recommendations
    api_stickiness = pd.to_numeric(row.get("api stickiness v2", "0"), errors="coerce")
    webhook_score = pd.to_numeric(row.get("webhook score (total 86)", "0"), errors="coerce")

    if webhook_score < 50:
        recommendations["High"].append("- Improve Webhook integration: Increase adoption for real-time order updates.")
    if api_stickiness < 50:
        recommendations["High"].append("- Enhance API adoption: Implement additional API endpoints to improve automation.")

    return recommendations

# ✅ UPDATED Function to generate PDF report with aligned bullet points
def generate_pdf(company_id, overall_score, product_value, recommendations):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, txt=f"Stickiness Report for Company ID: {company_id}", ln=True, align='C')
    pdf.ln(10)
    pdf.set_font("Arial", size=10)
    pdf.cell(0, 10, txt=f"Overall Score: {overall_score}%", ln=True)
    pdf.ln(5)
    pdf.cell(0, 10, txt=f"Product: {product_value}", ln=True)
    pdf.ln(10)

    pdf.set_font("Arial", 'B', size=10)
    pdf.cell(0, 10, txt="Recommendations:", ln=True)
    pdf.ln(5)

    pdf.set_font("Arial", size=10)

    for rank, features in recommendations.items():
        if features:
            pdf.set_font("Arial", 'B', size=10)
            pdf.cell(0, 10, txt=f"{rank} Stickiness Features:", ln=True)
            pdf.ln(2)
            pdf.set_font("Arial", size=10)
            for feature in features:
                pdf.set_x(10)  # Consistent indentation
                pdf.multi_cell(0, 8, txt=feature, border=0, align='L')
            pdf.ln(3)

    file_name = f"{company_id}_Stickiness_Report.pdf"
    pdf.output(file_name)
    return file_name

# Reports Page Function
def reports_page():
    st.title("📑 Reports and Recommendations")

    data = load_data_from_db()

    # Standardize column names
    data.columns = data.columns.str.strip().str.lower()
    data.rename(columns={"company_id": "Company ID"}, inplace=True)

    feature_columns = data.columns[9:36]  # Columns J to AJ (0-indexed: J=9, AJ=35)
    ranked_features = rank_features(data, feature_columns)

    possible_product_columns = [col for col in data.columns if "products" in col]
    product_column = possible_product_columns[0] if possible_product_columns else None

    if "overall_score" in data.columns:
        if data["overall_score"].max() <= 1:
            data["overall_score"] *= 100
        data["overall_score"] = data["overall_score"].round(2)

    if "Stickiness Category" not in data.columns:
        data["Stickiness Category"] = data["overall_score"].apply(categorise_stickiness)

    # 📌 Display Recommendations Table
    st.subheader("📌 Seller Recommendations")
    data["Recommendations"] = data.apply(lambda row: generate_recommendations(row, ranked_features, data), axis=1)

    display_columns = ["Company ID", "overall_score", "Stickiness Category", "Recommendations"]
    if product_column:
        display_columns.append(product_column)

    st.dataframe(data[display_columns])

    # 🔻 Dropdown to Select a Company for Report
    if "Company ID" in data.columns:
        selected_company = st.selectbox("📌 Select a Company:", data["Company ID"].unique())

        if st.button("📄 Generate & Download Report", key="download_button", help="Click to generate and download the PDF"):
            company_data = data[data["Company ID"] == selected_company].iloc[0]
            recommendations = generate_recommendations(company_data, ranked_features, data)
            product_value = company_data.get(product_column, "N/A") if product_column else "N/A"
            pdf_path = generate_pdf(
                company_id=selected_company,
                overall_score=company_data.get("overall_score", "N/A"),
                product_value=product_value,
                recommendations=recommendations
            )

            with open(pdf_path, "rb") as pdf_file:
                st.download_button(
                    label="📥 Download Report",
                    data=pdf_file,
                    file_name=pdf_path,
                    mime="application/pdf",
                    help="Click to download the PDF report",
                    key="final_download_button"
                )
