"""
GUI implementation for the Audi R8 price analysis application
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import threading
from typing import List, Tuple
from data_processor import ListingData
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

class AnalysisGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Audi R8 Market Analysis")
        self.root.geometry("1200x800")
        
        # Create main container with tabs
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=5)
        
        # Create tabs
        self.summary_tab = ttk.Frame(self.notebook)
        self.details_tab = ttk.Frame(self.notebook)
        self.graphs_tab = ttk.Frame(self.notebook)
        
        self.notebook.add(self.summary_tab, text='Summary')
        self.notebook.add(self.details_tab, text='Detailed Listings')
        self.notebook.add(self.graphs_tab, text='Graphs')
        
        # Initialize tabs
        self.setup_summary_tab()
        self.setup_details_tab()
        self.setup_graphs_tab()
        
        # Progress bar and status
        self.status_frame = ttk.Frame(root)
        self.status_frame.pack(fill='x', padx=10, pady=5)
        
        self.progress = ttk.Progressbar(self.status_frame, mode='indeterminate')
        self.progress.pack(fill='x', side='left', expand=True)
        
        self.status_label = ttk.Label(self.status_frame, text="Ready")
        self.status_label.pack(side='left', padx=5)

    def add_forecast_to_graph(self):
        # Call API for predictions
        api_url = "https://your-api-gateway-url/predict"
        params = {
            'transmission': 'manual',
            'engine': 'v10'
        }
        
        response = requests.get(api_url, params=params)
        forecast_data = response.json()
        
        # Add forecast line to price trend graph
        dates = [datetime.strptime(d, '%Y-%m-%d') for d in forecast_data['dates']]
        predictions = forecast_data['predictions']
        
        self.price_trend_ax.plot(dates, predictions, 
                                linestyle='--', 
                                color='green', 
                                label=f'Forecast (Accuracy: {forecast_data["accuracy"]:.1%})')
        self.price_trend_ax.legend()

    def setup_summary_tab(self):
        # Create frames for different sections
        self.create_summary_section(self.summary_tab, "Manual vs Automatic Analysis", 0)
        self.create_summary_section(self.summary_tab, "V10 Analysis", 1)
        self.create_summary_section(self.summary_tab, "V8 Analysis", 2)

    def create_summary_section(self, parent, title, row):
        frame = ttk.LabelFrame(parent, text=title)
        frame.grid(row=row, column=0, padx=10, pady=5, sticky='ew')
        parent.grid_columnconfigure(0, weight=1)
        
        # Create labels for statistics
        self.create_stat_labels(frame)
        return frame

    def create_stat_labels(self, frame):
        labels = ['Total Manual:', 'Total Auto:', 'Avg Manual Price:', 'Avg Auto Price:',
                 'Manual Price Range:', 'Auto Price Range:']
        
        for i, label in enumerate(labels):
            ttk.Label(frame, text=label).grid(row=i//2, column=i%2*2, padx=5, pady=2, sticky='e')
            ttk.Label(frame, text="---").grid(row=i//2, column=i%2*2+1, padx=5, pady=2, sticky='w')

    def setup_details_tab(self):
        # Create text widget for detailed listings
        self.details_text = scrolledtext.ScrolledText(self.details_tab, wrap=tk.WORD, height=40)
        self.details_text.pack(expand=True, fill='both', padx=10, pady=5)

    def setup_graphs_tab(self):
        # Create matplotlib figure
        self.figure = Figure(figsize=(10, 8))
        self.canvas = FigureCanvasTkAgg(self.figure, self.graphs_tab)
        self.canvas.get_tk_widget().pack(expand=True, fill='both')

    def update_summary_stats(self, analyzer):
        # Update Manual vs Automatic section
        self.update_section_stats(
            self.summary_tab.winfo_children()[0],  # First LabelFrame
            analyzer.with_manual,
            analyzer.without_manual
        )
        
        # Update V10 section
        self.update_section_stats(
            self.summary_tab.winfo_children()[1],  # Second LabelFrame
            analyzer.v10_with_manual,
            analyzer.v10_without_manual
        )
        
        # Update V8 section
        self.update_section_stats(
            self.summary_tab.winfo_children()[2],  # Third LabelFrame
            analyzer.v8_with_manual,
            analyzer.v8_without_manual
        )

    def update_section_stats(self, frame, manual_data: List[Tuple[ListingData, float]], 
                           auto_data: List[Tuple[ListingData, float]]):
        labels = frame.winfo_children()
        
        # Update statistics
        stats = [
            str(len(manual_data)),
            str(len(auto_data)),
            f"${self.calculate_average(manual_data):,.2f}",
            f"${self.calculate_average(auto_data):,.2f}",
            f"${self.get_price_range(manual_data)}",
            f"${self.get_price_range(auto_data)}"
        ]
        
        # Update labels with new values
        value_labels = [label for i, label in enumerate(labels) if i % 2 == 1]
        for label, stat in zip(value_labels, stats):
            label.configure(text=stat)

    def update_details(self, analyzer):
        self.details_text.delete(1.0, tk.END)
        
        categories = [
            ("Manual Transmission Listings", analyzer.with_manual),
            ("Automatic Transmission Listings", analyzer.without_manual),
            ("V10 Manual Transmission Listings", analyzer.v10_with_manual),
            ("V10 Automatic Transmission Listings", analyzer.v10_without_manual),
            ("V8 Manual Transmission Listings", analyzer.v8_with_manual),
            ("V8 Automatic Transmission Listings", analyzer.v8_without_manual)
        ]
        
        for title, listings in categories:
            self.details_text.insert(tk.END, f"\n{title}\n")
            self.details_text.insert(tk.END, "="*50 + "\n")
            for listing, price in listings:
                self.details_text.insert(tk.END, f"{listing.name}\n")
                self.details_text.insert(tk.END, f"Price: ${price:,.2f}\n")
                self.details_text.insert(tk.END, f"{listing.details}\n\n")

    def update_graphs(self, analyzer):
        self.figure.clear()
        
        # Create subplots
        ax1 = self.figure.add_subplot(211)
        ax2 = self.figure.add_subplot(212)
        
        # Price comparison bar chart
        categories = ['All', 'V10', 'V8']
        manual_avgs = [
            self.calculate_average(analyzer.with_manual),
            self.calculate_average(analyzer.v10_with_manual),
            self.calculate_average(analyzer.v8_with_manual)
        ]
        auto_avgs = [
            self.calculate_average(analyzer.without_manual),
            self.calculate_average(analyzer.v10_without_manual),
            self.calculate_average(analyzer.v8_without_manual)
        ]
        
        x = range(len(categories))
        width = 0.35
        
        ax1.bar([i - width/2 for i in x], manual_avgs, width, label='Manual')
        ax1.bar([i + width/2 for i in x], auto_avgs, width, label='Automatic')
        
        ax1.set_ylabel('Average Price ($)')
        ax1.set_title('Average Prices by Category')
        ax1.set_xticks(x)
        ax1.set_xticklabels(categories)
        ax1.legend()
        
        # Distribution plot
        all_manual_prices = [price for _, price in analyzer.with_manual]
        all_auto_prices = [price for _, price in analyzer.without_manual]
        
        ax2.hist(all_manual_prices, bins=20, alpha=0.5, label='Manual')
        ax2.hist(all_auto_prices, bins=20, alpha=0.5, label='Automatic')
        ax2.set_xlabel('Price ($)')
        ax2.set_ylabel('Number of Listings')
        ax2.set_title('Price Distribution')
        ax2.legend()
        
        self.figure.tight_layout()
        self.canvas.draw()

    @staticmethod
    def calculate_average(listings: List[Tuple[ListingData, float]]) -> float:
        if not listings:
            return 0
        return sum(price for _, price in listings) / len(listings)

    @staticmethod
    def get_price_range(listings: List[Tuple[ListingData, float]]) -> str:
        if not listings:
            return "No data"
        prices = [price for _, price in listings]
        return f"{min(prices):,.2f} - ${max(prices):,.2f}"
