'''

This program is designed to understand the effects 
of different powertrain options on the 
price of the first generation Audi R8... 
the    greatest     car      ever

'''

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager 
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import re

options = Options()
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

driver.get("https://bringatrailer.com/audi/r8/")
driver.maximize_window()
#-------------------------------------------filter up to 2015 to only search for first gen audi r8 --- (2006-2015) -------------------------------------------------------
year_range_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "//*[text()='Year Range']")))
year_range_button.click()

input_field = WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/main/div[2]/div/div[2]/div/div/div[1]/div/div[2]/div[3]/div[4]/div[2]/div/input[2]")))
input_field.send_keys("2015")
#----------------------------------------------------------------------------------------------------------------------------------------------------------

#-------------------------------------------make all of the listings load------------------------------------------------------------------
while True:
    try:
        show_more_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, "/html/body/main/div[2]/div/div[2]/div/div/div[2]/div[2]/button")))
        show_more_button.click()
        driver.implicitly_wait(1)
        time.sleep(1/3)
    except Exception as e:
        print(f"No more 'Show More' button found: {e}")
        break
#----------------------------------------------------------------------------------------------------------------------------------------------------------

# Find all elements containing the name and price information
listings = driver.find_elements(By.CSS_SELECTOR, ".listings-container.auctions-grid .listing-card.bg-white-transparent")

#----------------------------------empty lists of the different powertrain options---------------------------------------------------------------------------------------------
#prices
with_manual_prices = []
without_manual_prices = []
v8_with_manual_prices = []
v8_without_manual_prices = []
v10_with_manual_prices = []
v10_without_manual_prices = []

#quantity - aka sample size
with_manual_list = []
without_manual_list = []
v8_with_manual_list = []
v8_without_manual_list = []
v10_with_manual_list = []
v10_without_manual_list = []
#----------------------------------------------------------------------------------------------------------------------------------------------------------


#--------------------------------------------Use regex to understand whether it was sold or not (disregards a listing if it wasn't sold), price, transmission type, and engine type--------------------------------------------
for listing in listings:
    name = listing.find_element(By.CSS_SELECTOR, ".content-main h3").text
    details = listing.find_element(By.CSS_SELECTOR, ".content-main .item-results").text
    
    # Check if the listing was sold (exclude "bid to")
    if "bid to" not in details.lower():
        price_text = re.search(r"\$\d+(?:,\d+)?", details)  # Using regex to extract the price
        v10_present = 'V10' in name
        if price_text:
            price = price_text.group(0)
            if '6-Speed' in name:
                with_manual_prices.append(float(price.replace(',', '').replace('$', '')))
                with_manual_list.append(f"Listing Name: {name}\nDetails: {details}\n")
                if v10_present:
                    v10_with_manual_prices.append(float(price.replace(',', '').replace('$', '')))
                    v10_with_manual_list.append(f"Listing Name: {name}\nDetails: {details}\n")
                else:
                    v8_with_manual_prices.append(float(price.replace(',', '').replace('$', '')))
                    v8_with_manual_list.append(f"Listing Name: {name}\nDetails: {details}\n")
            else:
                without_manual_prices.append(float(price.replace(',', '').replace('$', '')))
                without_manual_list.append(f"Listing Name: {name}\nDetails: {details}\n")
                if v10_present:
                    v10_without_manual_prices.append(float(price.replace(',', '').replace('$', '')))
                    v10_without_manual_list.append(f"Listing Name: {name}\nDetails: {details}\n")
                else:
                    v8_without_manual_prices.append(float(price.replace(',', '').replace('$', '')))
                    v8_without_manual_list.append(f"Listing Name: {name}\nDetails: {details}\n")

#----------------------------------------------------------------------------------------------------------------------------------------------------------

#----------------------------------------simple arithmetic to calculate average prices------------------------------------------------------------------------------------------------------
avg_price_with_manual = sum(with_manual_prices) / len(with_manual_prices) if with_manual_prices else 0
avg_price_without_manual = sum(without_manual_prices) / len(without_manual_prices) if without_manual_prices else 0
avg_price_v8_with_manual = sum(v8_with_manual_prices) / len(v8_with_manual_prices) if v8_with_manual_prices else 0
avg_price_v8_without_manual = sum(v8_without_manual_prices) / len(v8_without_manual_prices) if v8_without_manual_prices else 0
avg_price_v10_with_manual = sum(v10_with_manual_prices) / len(v10_with_manual_prices) if v10_with_manual_prices else 0
avg_price_v10_without_manual = sum(v10_without_manual_prices) / len(v10_without_manual_prices) if v10_without_manual_prices else 0
#----------------------------------------------------------------------------------------------------------------------------------------------------------

print("Listings with 6-speed manual:")
for with_manual in with_manual_list:
    print(with_manual)

print("Listings without 6-speed manual:")
for without_manual in without_manual_list:
    print(without_manual)

print("Listings with V8 and 6-speed manual:")
for v8_with_manual in v8_with_manual_list:
    print(v8_with_manual)

print("Listings with V8 but without 6-speed manual:")
for v8_without_manual in v8_without_manual_list:
    print(v8_without_manual)

print("Listings with V10 and 6-speed manual:")
for v10_with_manual in v10_with_manual_list:
    print(v10_with_manual)

print("Listings with V10 but without 6-speed manual:")
for v10_without_manual in v10_without_manual_list:
    print(v10_without_manual)

#----------------------------------------------------------------------------------------------------------------------------------------------------------
print("-------------------------------------------------------------")
print("HERES SOME SALES HISTORY TO HELP YOU UNDERSTAND THE MARKET OF AUDI R8'S...")
print("-------------------------------------------------------------")

print("MANUAL VS AUTOMATIC")
print("-------------------------------------------------------------")
print(f"Total number of listings with 6-speed manual transmission: {len(with_manual_list)}")
print(f"Total number of listings with automatic transmission: {len(without_manual_list)} ")
print(f"Average price of listings with 6-speed manual transmission: ${avg_price_with_manual:.2f}")
print(f"Average price of listings without 6-speed manual: ${avg_price_without_manual:.2f}")
print("-------------------------------------------------------------")


print("V10 MANUAL VS V10 AUTOMATIC")
print("-------------------------------------------------------------")
print(f"Total number of listings with V10 and 6-speed manual transmission: {len(v10_with_manual_list)}")
print(f"Total number of listings with V10 and automatic transmission: {len(v10_without_manual_list)}")
print(f"Average price of listings with V10 and 6-speed manual transmission: ${avg_price_v10_with_manual:.2f}")
print(f"Average price of listings with V10 and automatic transmission: ${avg_price_v10_without_manual:.2f}")
print("-------------------------------------------------------------")

print("V8 MANUAL VS V8 AUTOMATIC")
print("-------------------------------------------------------------")
print(f"Total number of listings with V8 and 6-speed manual transmission: {len(v8_with_manual_list)}")
print(f"Total number of listings with V8 and automatic transmission: {len(v8_without_manual_list)}")
print(f"Average price of listings with V8 and 6-speed manual transmission: ${avg_price_v8_with_manual:.2f}")
print(f"Average price of listings with V8 and automatic transmission: ${avg_price_v8_without_manual:.2f}")
print("-------------------------------------------------------------\n")

#----------------------------------------------------------------------------------------------------------------------------------------------------------

driver.quit()
