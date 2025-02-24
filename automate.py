import os

print("🚀 Running automated KUB bill extraction & update process...")

# Run the scraper to fetch new bills
print("📥 Extracting bills from KUB website...")
os.system("python3 kub_scraper.py")

# Store extracted data into SQLite
print("💾 Storing new data in the database...")
os.system("python3 store_data.py")

print("✅ Monthly KUB bill update completed successfully!")

