from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
import time
import os
import requests
import pdfplumber
import pandas as pd

# KUB credentials (REPLACE with your actual credentials)
KUB_USERNAME = "amith.narayan@yahoo.com"
KUB_PASSWORD = "Mouna2404671410!@#"

# Set up Selenium WebDriver
options = webdriver.ChromeOptions()
options.add_argument("--headless")  # Run without opening a browser window
prefs = {"download.default_directory": os.path.abspath("kub_bills")}  # Set download folder
options.add_experimental_option("prefs", prefs)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

def login_to_kub():
    driver.get("https://www.kub.org")

    try:
        # Wait for the login button to be clickable
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//div[contains(@class, 'kub-login-button')]/a"))
        )
        driver.execute_script("arguments[0].click();", login_button)  # Click via JavaScript
        time.sleep(3)

        # Enter username and password
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.NAME, "username"))
        )
        username_field.send_keys(KUB_USERNAME)
        
        password_field = driver.find_element(By.NAME, "password")
        password_field.send_keys(KUB_PASSWORD + Keys.RETURN)
        time.sleep(5)

    except Exception as e:
        print(f"Error during login: {e}")

def download_bill_pdfs():
    """Clicks 'More Bill History', paginates, scrolls down, and downloads all available PDF bills."""
    driver.get("https://www.kub.org/customer/accounts/7975935226/activity?filter=bills")
    time.sleep(5)  # Allow page to load

    # Click "More Bill History" if available
    try:
        history_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'More Bill History')]"))
        )
        history_button.click()
        time.sleep(3)  # Allow history to load
        print("✅ Clicked 'More Bill History' button!")
    except Exception:
        print("ℹ️ 'More Bill History' button not found or already loaded. Continuing...")

    # Create directory to store PDFs
    pdf_dir = "kub_bills"
    if not os.path.exists(pdf_dir):
        os.makedirs(pdf_dir)

    # Extract session cookies from Selenium
    cookies = driver.get_cookies()
    session = requests.Session()
    for cookie in cookies:
        session.cookies.set(cookie['name'], cookie['value'])

    page_number = 1

    while True:
        print(f"📄 Scraping Page {page_number}...")

        # Scroll down to load all bills on the current page
        last_height = driver.execute_script("return document.body.scrollHeight")

        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Allow time for loading
            new_height = driver.execute_script("return document.body.scrollHeight")

            if new_height == last_height:
                break  # Stop scrolling when no new content loads
            last_height = new_height

        print("✅ Scrolled down to load all bills on this page.")

        # Locate all bill PDF links on the current page
        pdf_links = driver.find_elements(By.XPATH, "//a[contains(@href, '/api/cis/v1/accounts') and contains(@href, 'bill.pdf')]")

        if not pdf_links:
            print("❌ No PDF bills found on this page.")
        else:
            for index, link in enumerate(pdf_links):
                pdf_url = link.get_attribute("href")
                bill_date = pdf_url.split("billDate=")[-1].split("&")[0]  # Extract bill date from URL
                bill_date = bill_date.replace("/", "-")  # Fix filename format
                file_name = f"KUB_Bill_{bill_date}.pdf"
                file_path = os.path.join(pdf_dir, file_name)

                # Skip if already downloaded
                if os.path.exists(file_path):
                    print(f"🔄 Skipping (already exists): {file_name}")
                    continue

                print(f"⬇️ Downloading ({index + 1}/{len(pdf_links)}): {file_name}")

                # Download the PDF
                response = session.get(pdf_url, stream=True, headers={"Referer": driver.current_url})

                if response.status_code == 200:
                    with open(file_path, "wb") as f:
                        f.write(response.content)
                    print(f"✅ Saved: {file_name}")
                else:
                    print(f"❌ Failed to download: {file_name}, Status Code: {response.status_code}")

        # Try to find and click the "Next Page" button
        try:
            next_page_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[contains(text(), 'Next')]"))
            )
            next_page_button.click()
            time.sleep(3)  # Allow the next page to load
            print("➡️ Moving to next page...")
            page_number += 1
        except Exception:
            print("🚫 No more pages available. Finished downloading all bills.")
            break  # Exit the loop when there are no more pages

    print("🎉 All PDF bills downloaded successfully!")

def extract_bill_amount_from_pdfs():
    """Extracts bill amounts from downloaded PDFs and saves them to CSV."""
    bills_data = []
    pdf_dir = "kub_bills"

    for filename in os.listdir(pdf_dir):
        if filename.endswith(".pdf"):
            filepath = os.path.join(pdf_dir, filename)
            with pdfplumber.open(filepath) as pdf:
                text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

                # Extract the amount (modify this based on actual PDF content)
                bill_amount = None
                for line in text.split("\n"):
                    if "Total Gas Charges:" in line or "Current Charges for Period:" in line:
                        try:
                            bill_amount = float(line.split("$")[-1].strip())
                        except ValueError:
                            pass  # Handle cases where extraction fails
                        break

                if bill_amount:
                    bill_date = filename.replace("KUB_Bill_", "").replace(".pdf", "")
                    bills_data.append([bill_date, bill_amount])

    # Save extracted data to CSV
    df = pd.DataFrame(bills_data, columns=["Month-Year", "Amount"])
    df.to_csv("kub_bills.csv", index=False)

    print("✅ Data extracted and saved successfully!")
    return df

if __name__ == "__main__":
    if not os.path.exists("kub_bills"):
        os.makedirs("kub_bills")

    login_to_kub()
    download_bill_pdfs()
    bill_data = extract_bill_amount_from_pdfs()
    driver.quit()
