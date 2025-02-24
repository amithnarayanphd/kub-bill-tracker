from flask import Flask, render_template, jsonify
import sqlite3
import pandas as pd

app = Flask(__name__)

def get_billing_data():
    """Fetch bills data from SQLite database."""
    conn = sqlite3.connect("kub_bills.db")
    cursor = conn.cursor()
    cursor.execute("SELECT month_year, amount FROM bills ORDER BY month_year DESC")
    bills = [{"month_year": row[0], "amount": row[1]} for row in cursor.fetchall()]
    conn.close()
    return bills

@app.route('/get_bills', methods=['GET'])
def get_bills():
    return jsonify(get_billing_data())

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Use Render's assigned port
    app.run(host="0.0.0.0", port=port)
