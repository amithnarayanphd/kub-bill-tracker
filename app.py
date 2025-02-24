from flask import Flask, render_template
import sqlite3

app = Flask(__name__)

def get_billing_data():
    conn = sqlite3.connect("kub_bills.db")
    cursor = conn.cursor()
    cursor.execute("SELECT month_year, amount FROM bills ORDER BY month_year DESC")
    bills = [{"month_year": row[0], "amount": row[1]} for row in cursor.fetchall()]
    conn.close()
    return bills

@app.route('/')
def index():
    bills = get_billing_data()
    return render_template('index.html', bills=bills)

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 10000))  # Render assigns a dynamic port
    app.run(host="0.0.0.0", port=port)
