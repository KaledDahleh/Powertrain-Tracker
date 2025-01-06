"""
Functions for web scraping operations
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

def set_year_filter(driver, year):
    year_range_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[text()='Year Range']"))
    )
    year_range_button.click()

    input_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "/html/body/main/div[2]/div/div[2]/div/div/div[1]/div/div[2]/div[3]/div[4]/div[2]/div/input[2]"))
    )
    input_field.send_keys(year)

def load_all_listings(driver):
    while True:
        try:
            show_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "/html/body/main/div[2]/div/div[2]/div/div/div[2]/div[2]/button"))
            )
            show_more_button.click()
            driver.implicitly_wait(1)
            time.sleep(1/3)
        except Exception as e:
            print(f"No more 'Show More' button found: {e}")
            break

def get_listings(driver):
    return driver.find_elements(
        By.CSS_SELECTOR,
        ".listings-container.auctions-grid .listing-card.bg-white-transparent"
    )
