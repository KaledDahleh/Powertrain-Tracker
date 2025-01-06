import tkinter as tk
from tkinter import ttk
import threading
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
import re

class AudiAnalysisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("First-Gen Audi R8 Market Analysis (2008-2015)")
        self.root.geometry("1200x800")
        
        # Create notebook (tabbed interface)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Create tabs
        self.data_tab = ttk.Frame(self.notebook)
        self.graphs_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.data_tab, text='Data')
        self.notebook.add(self.graphs_tab, text='Graphs')
        
        # Setup Data tab
        self.setup_data_tab()
        
        # Setup Graphs tab
        self.setup_graphs_tab()
        
        # Data storage
        self.listings_data = []

    def setup_data_tab(self):
        # Control frame
        control_frame = ttk.Frame(self.data_tab)
        control_frame.pack(fill='x', padx=10, pady=5)
        
        self.analyze_button = ttk.Button(control_frame, text="Run Analysis", command=self.start_analysis)
        self.analyze_button.pack(side='left', padx=5)
        
        self.status_label = ttk.Label(control_frame, text="Ready")
        self.status_label.pack(side='left', padx=5)
        
        self.progress = ttk.Progressbar(control_frame, mode='indeterminate')
        self.progress.pack(side='left', fill='x', expand=True, padx=5)
        
        # Results text
        self.results_text = tk.Text(self.data_tab, height=20, width=60)
        self.results_text.pack(padx=10, pady=5, expand=True, fill='both')

    def setup_graphs_tab(self):
        self.figure = plt.Figure(figsize=(12, 8), dpi=100)
        self.canvas = FigureCanvasTkAgg(self.figure, self.graphs_tab)
        self.canvas.get_tk_widget().pack(expand=True, fill='both')

    def start_analysis(self):
        self.analyze_button.config(state='disabled')
        self.status_label.config(text="Starting analysis...")
        self.progress.start()
        self.results_text.delete(1.0, tk.END)
        thread = threading.Thread(target=self.run_analysis)
        thread.daemon = True
        thread.start()

    def extract_year(self, name):
        year_match = re.search(r'\b(20\d{2})\b', name)
        return int(year_match.group(1)) if year_match else None

    def parse_listing_data(self, name, details):
        # First check the year to ensure it's first gen
        year = self.extract_year(name)
        if not year or year < 2008 or year > 2015:
            return None
            
        # Extract price
        price_match = re.search(r"\$([0-9,]+)", details)
        if not price_match:
            return None
        price = float(price_match.group(1).replace(',', ''))
        
        # Extract date
        date_match = re.search(r"on (\d{1,2}/\d{1,2}/\d{2})", details)
        if not date_match:
            return None
        date_str = date_match.group(1)
        try:
            date = datetime.strptime(date_str, "%m/%d/%y")
        except ValueError:
            return None
        
        # Determine transmission and engine
        is_manual = '6-Speed' in name
        is_v10 = 'V10' in name
        
        return {
            'name': name,
            'year': year,
            'price': price,
            'date': date,
            'is_manual': is_manual,
            'is_v10': is_v10
        }

    def update_graphs(self):
        self.figure.clear()
        
        # Create subplots
        price_trend_ax = self.figure.add_subplot(221)
        transmission_compare_ax = self.figure.add_subplot(222)
        engine_compare_ax = self.figure.add_subplot(223)
        price_dist_ax = self.figure.add_subplot(224)
        
        # Filter valid listings and sort by date
        valid_listings = sorted([l for l in self.listings_data if l['date']], key=lambda x: x['date'])
        
        # 1. Price Trend Over Time with different colors for each variant
        categories = {
            'V10 Manual': [(l['date'], l['price']) for l in valid_listings if l['is_v10'] and l['is_manual']],
            'V10 Auto': [(l['date'], l['price']) for l in valid_listings if l['is_v10'] and not l['is_manual']],
            'V8 Manual': [(l['date'], l['price']) for l in valid_listings if not l['is_v10'] and l['is_manual']],
            'V8 Auto': [(l['date'], l['price']) for l in valid_listings if not l['is_v10'] and not l['is_manual']]
        }
        
        colors = {'V10 Manual': 'darkred', 'V10 Auto': 'red', 
                 'V8 Manual': 'darkblue', 'V8 Auto': 'blue'}
        markers = {'V10 Manual': 'o', 'V10 Auto': '^', 
                  'V8 Manual': 'o', 'V8 Auto': '^'}
        
        for category, data in categories.items():
            if data:
                dates, prices = zip(*data)
                price_trend_ax.scatter(dates, prices, 
                                     label=category,
                                     color=colors[category],
                                     marker=markers[category],
                                     alpha=0.6)
        
        price_trend_ax.set_title('First-Gen R8 Price Trends by Variant')
        price_trend_ax.set_xlabel('Sale Date')
        price_trend_ax.set_ylabel('Price ($)')
        price_trend_ax.legend()
        price_trend_ax.tick_params(axis='x', rotation=45)
        price_trend_ax.grid(True, linestyle='--', alpha=0.7)
        
        # 2. Box plots for price distributions
        manual_prices = [l['price'] for l in valid_listings if l['is_manual']]
        auto_prices = [l['price'] for l in valid_listings if not l['is_manual']]
        v10_manual = [l['price'] for l in valid_listings if l['is_v10'] and l['is_manual']]
        v10_auto = [l['price'] for l in valid_listings if l['is_v10'] and not l['is_manual']]
        v8_manual = [l['price'] for l in valid_listings if not l['is_v10'] and l['is_manual']]
        v8_auto = [l['price'] for l in valid_listings if not l['is_v10'] and not l['is_manual']]
        
        # Create box plots
        bp1 = transmission_compare_ax.boxplot([manual_prices, auto_prices],
                                            labels=['Manual', 'Auto'],
                                            patch_artist=True)
        transmission_compare_ax.set_title('Price Distribution by Transmission')
        transmission_compare_ax.set_ylabel('Price ($)')
        
        bp2 = engine_compare_ax.boxplot([v10_manual, v10_auto, v8_manual, v8_auto],
                                      labels=['V10 Manual', 'V10 Auto', 'V8 Manual', 'V8 Auto'],
                                      patch_artist=True)
        engine_compare_ax.set_title('Price Distribution by Engine & Transmission')
        engine_compare_ax.set_ylabel('Price ($)')
        engine_compare_ax.tick_params(axis='x', rotation=45)
        
        # Color the box plots
        colors = ['lightblue', 'lightgreen']
        for patch, color in zip(bp1['boxes'], colors):
            patch.set_facecolor(color)
        
        colors = ['darkred', 'red', 'darkblue', 'blue']
        for patch, color in zip(bp2['boxes'], colors):
            patch.set_facecolor(color)
            
        # Add grid to box plots
        transmission_compare_ax.grid(True, linestyle='--', alpha=0.7)
        engine_compare_ax.grid(True, linestyle='--', alpha=0.7)
        
        # 4. Price distribution histogram
        all_prices = [l['price'] for l in valid_listings]
        price_dist_ax.hist(all_prices, bins=30, color='skyblue', edgecolor='black')
        mean_price = sum(all_prices) / len(all_prices)
        median_price = sorted(all_prices)[len(all_prices)//2]
        
        price_dist_ax.axvline(mean_price, color='red', linestyle='--', 
                            label=f'Mean: ${mean_price:,.0f}')
        price_dist_ax.axvline(median_price, color='green', linestyle='--', 
                            label=f'Median: ${median_price:,.0f}')
        
        price_dist_ax.set_title('Price Distribution')
        price_dist_ax.set_xlabel('Price ($)')
        price_dist_ax.set_ylabel('Number of Sales')
        price_dist_ax.grid(True, linestyle='--', alpha=0.7)
        price_dist_ax.legend()
        
        self.figure.tight_layout()
        self.canvas.draw()

    def run_analysis(self):
        try:
            self.update_status("Initializing browser...")
            
            options = Options()
            options.add_experimental_option("detach", True)
            driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), 
                                   options=options)
            
            self.update_status("Navigating to website...")
            driver.get("https://bringatrailer.com/audi/r8/")
            driver.maximize_window()
            
            self.update_status("Setting year filter...")
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
            
            self.update_status("Loading listings...")
            self.update_results("Beginning data collection for First-Gen R8 (2008-2015)...\n")
            
            # Load all listings
            while True:
                try:
                    show_more_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "/html/body/main/div[2]/div/div[2]/div/div/div[2]/div[2]/button"))
                    )
                    show_more_button.click()
                    time.sleep(1/3)
                except Exception:
                    break
            
            self.update_status("Processing listings...")
            listings = driver.find_elements(By.CSS_SELECTOR, 
                ".listings-container.auctions-grid .listing-card.bg-white-transparent")
            
            # Process listings
            self.listings_data = []
            for listing in listings:
                try:
                    name = listing.find_element(By.CSS_SELECTOR, ".content-main h3").text
                    details = listing.find_element(By.CSS_SELECTOR, ".content-main .item-results").text
                    
                    if "bid to" not in details.lower():  # Only include completed sales
                        listing_data = self.parse_listing_data(name, details)
                        if listing_data:  # Only add if it's a valid first-gen listing
                            self.listings_data.append(listing_data)
                            self.update_results(f"Processed: {name} - ${listing_data['price']:,.2f}\n")
                except Exception as e:
                    print(f"Error processing listing: {str(e)}")
                    continue
            
            # Print summary statistics
            self.update_results("\nSummary Statistics:\n")
            self.update_results(f"Total listings processed: {len(self.listings_data)}\n")
            
            # Find highest sales
            top_sales = sorted(self.listings_data, key=lambda x: x['price'], reverse=True)[:5]
            self.update_results("\nTop 5 Highest Sales:\n")
            for i, sale in enumerate(top_sales, 1):
                self.update_results(f"{i}. {sale['name']} - ${sale['price']:,.2f}\n")
            
            self.update_status("Generating graphs...")
            self.root.after(0, self.update_graphs)
            self.update_status("Analysis complete!")
            
        except Exception as e:
            self.update_status(f"Error: {str(e)}")
        finally:
            driver.quit()
            self.analyze_button.config(state='normal')
            self.progress.stop()

    def update_status(self, message):
        self.root.after(0, lambda: self.status_label.config(text=message))

    def update_results(self, message):
        self.root.after(0, lambda: self.results_text.insert(tk.END, message))

def main():
    root = tk.Tk()
    app = AudiAnalysisGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()