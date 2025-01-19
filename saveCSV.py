import os
import csv
import re
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def extract_year(name):
    """Extract the year (20XX) from the listing name."""
    match = re.search(r'\b(20\d{2})\b', name)
    return int(match.group(1)) if match else None

def parse_listing_data(name, details):
    """Return a dict with listing data if valid first-gen R8, else None."""
    # Year check
    year = extract_year(name)
    if not year or year < 2008 or year > 2015:
        return None
    
    # Price
    price_match = re.search(r"\$([0-9,]+)", details)
    if not price_match:
        return None
    price = float(price_match.group(1).replace(',', ''))
    
    # Sale date
    date_match = re.search(r"on (\d{1,2}/\d{1,2}/\d{2})", details)
    if not date_match:
        return None
    
    date_str = date_match.group(1)
    try:
        date = datetime.strptime(date_str, "%m/%d/%y")
    except ValueError:
        return None
    
    # Transmission & engine
    is_manual = '6-Speed' in name
    is_v10 = 'V10' in name
    
    return {
        'name': name,
        'year': year,
        'price': price,
        'date': date.strftime("%Y-%m-%d"),  # Format date as YYYY-MM-DD for CSV
        'is_manual': is_manual,
        'is_v10': is_v10
    }

def scrape_audi_r8_data():
    """Scrape first-gen Audi R8 data from Bring a Trailer and save to CSV."""
    # Create folders if they don't exist
    base_folder = "carData"
    car_folder = os.path.join(base_folder, "AudiR8")
    os.makedirs(car_folder, exist_ok=True)
    csv_path = os.path.join(car_folder, "audi_r8_data.csv")
    
    # Setup WebDriver
    options = Options()

    # ---- the following 3 lines makes selenium headless
    options.add_argument("--headless")          # No UI
    options.add_argument("--no-sandbox")        # (Recommended for some Linux servers)
    options.add_argument("--disable-dev-shm-usage")

    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )
    
    try:
        # Navigate
        driver.get("https://bringatrailer.com/audi/r8/")
        driver.maximize_window()
        
        # Set year range
        year_range_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//*[text()='Year Range']"))
        )
        year_range_button.click()
        
        min_year_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/main/div[2]/div/div[2]/div/div/div[1]/div/div[2]/div[3]/div[4]/div[2]/div/input[1]"))
        )
        min_year_field.send_keys("2008")
        
        max_year_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/main/div[2]/div/div[2]/div/div/div[1]/div/div[2]/div[3]/div[4]/div[2]/div/input[2]"))
        )
        max_year_field.send_keys("2015")
        
        # Load all listings by clicking "Show More" until it fails
        while True:
            try:
                show_more_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/main/div[2]/div/div[2]/div/div/div[2]/div[2]/button"))
                )
                show_more_button.click()
                time.sleep(0.33)
            except:
                break
        
        # Scrape listings
        listings = driver.find_elements(By.CSS_SELECTOR,
            ".listings-container.auctions-grid .listing-card.bg-white-transparent")
        
        scraped_data = []
        for listing in listings:
            try:
                name = listing.find_element(By.CSS_SELECTOR, ".content-main h3").text
                details = listing.find_element(By.CSS_SELECTOR, ".content-main .item-results").text
                
                # Filter out "bid to" (which indicates incomplete sale/no final price)
                if "bid to" not in details.lower():
                    row = parse_listing_data(name, details)
                    if row:
                        scraped_data.append(row)
            except Exception:
                continue
        
        # Write to CSV
        with open(csv_path, "w", newline="", encoding="utf-8") as csvfile:
            fieldnames = ["name", "year", "price", "date", "is_manual", "is_v10"]
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in scraped_data:
                writer.writerow(row)
        
        print(f"Scraped {len(scraped_data)} listings. Data saved to {csv_path}")
    
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    scrape_audi_r8_data()

