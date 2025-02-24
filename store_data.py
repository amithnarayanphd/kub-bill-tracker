import sqlite3
import pandas as pd

# Load extracted CSV file
csv_file = "kub_bills.csv"

# Check if CSV exists
try:
    df = pd.read_csv(csv_file)
except FileNotFoundError:
    print(f"❌ Error: {csv_file} not found. Make sure you have extracted bills.")
    exit()

# Connect to SQLite database (or create if not exists)
conn = sqlite3.connect("kub_bills.db")
cursor = conn.cursor()

# Create a table for bills (if not exists)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS bills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        month_year TEXT UNIQUE,
        amount REAL
    )
""")

# Insert data into table, avoiding duplicates
for _, row in df.iterrows():
    try:
        cursor.execute("INSERT INTO bills (month_year, amount) VALUES (?, ?)", (row["Month-Year"], row["Amount"]))
    except sqlite3.IntegrityError:
        print(f"Skipping duplicate entry: {row['Month-Year']}")

# Commit and close
conn.commit()
conn.close()

print("✅ Data successfully stored in SQLite database!")
