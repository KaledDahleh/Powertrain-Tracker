# config.py
"""
Configuration settings for the web scraping application
"""
from selenium.webdriver.chrome.options import Options

def get_chrome_options():
    options = Options()
    options.add_experimental_option("detach", True)
    return options

BASE_URL = "https://bringatrailer.com/audi/r8/"
MAX_YEAR = "2015"