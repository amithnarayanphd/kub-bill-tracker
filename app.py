from flask import Flask, render_template
import sqlite3
import pandas as pd

app = Flask(__name__)

def get_billing_data():
    """Fetch bills data from SQLite database."""
    conn = sqlite3.connect("kub_bills.db")
    df = pd.read_sql_query("SELECT * FROM bills", conn)
    conn.close()
    return df.to_dict(orient="records")

@app.route("/")
def index():
    bills = get_billing_data()
    return render_template("index.html", bills=bills)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Use Render's assigned port
    app.run(host="0.0.0.0", port=port)
