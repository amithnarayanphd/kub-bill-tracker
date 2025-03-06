from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)  # Enables cross-origin requests

# Function to get data from SQLite
def get_billing_data():
    conn = sqlite3.connect("kub_bills.db")
    cursor = conn.cursor()
    cursor.execute("SELECT month_year, amount FROM bills ORDER BY month_year DESC")
    bills = [{"month_year": row[0], "amount": row[1]} for row in cursor.fetchall()]
    conn.close()
    return bills

# Fix Route Name to Match Flutter Expectation
@app.route("/get_bills", methods=["GET"])  # Fixed from /index to /get_bills
def get_bills():
    bills = get_billing_data()
    return jsonify(bills)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))  # Use Render's assigned port
    app.run(host="0.0.0.0", port=port)
