import pandas as pd
import sqlite3

# Define the Excel file and SQLite database
excel_file = "Seller_Stickiness_Sheet.xlsx"  # Ensure this file is in the same directory
db_file = "stickiness_data.db"

# Read Excel sheets
xls = pd.ExcelFile(excel_file)
sheets = {
    "technical_stickiness": xls.parse("Technical Stickiness"),
    "webhooks": xls.parse("Webhooks"),
    "api_stickiness": xls.parse("API Stickiness matrix"),
    "seller_tech_stacks": xls.parse("Seller Tech stacks"),
}

# Convert column names to lowercase and replace spaces with underscores
for sheet_name, df in sheets.items():
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

# Connect to SQLite and store sheets as tables
conn = sqlite3.connect(db_file)
for sheet_name, df in sheets.items():
    df.to_sql(sheet_name, conn, if_exists="replace", index=False)

conn.close()
print(f"✅ Successfully converted '{excel_file}' to '{db_file}'!")
