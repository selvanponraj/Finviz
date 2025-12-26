#!/usr/bin/env python3
"""
Finviz Scanner Script
Fetches and displays stock screening results from Finviz
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from tabulate import tabulate
from typing import List, Dict


class FinvizScanner:
    """Scanner for Finviz screener results"""
    
    BASE_URL = "https://finviz.com/screener.ashx"
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def build_url(self, filters: Dict[str, str], output: str = "111", order: str = "-volume") -> str:
        """
        Build Finviz screener URL
        
        Args:
            filters: Dictionary of filter codes
            output: Output format (111 for overview)
            order: Sort order
            
        Returns:
            Complete Finviz URL
        """
        filter_str = ",".join([f"{k}_{v}" for k, v in filters.items()])
        return f"{self.BASE_URL}?v={output}&f={filter_str}&ft=4&o={order}"
    
    def daily_3up_scanner(self) -> str:
        """
        Build URL for Daily 3% UP scanner
        
        Criteria:
        - Daily 3% UP
        - Price > $30
        - Above 200 SMA
        - ATR > 2
        - RVOL > 2
        """
        filters = {
            "ind": "stocksonly",
            "sh_price": "o30",           # Price over $30
            "sh_relvol": "o2",           # Relative volume over 2
            "ta_averagetruerange": "o2", # ATR over 2
            "ta_change": "u3",           # Change up 3%
            "ta_sma200": "pa"            # Price above SMA200
        }
        return self.build_url(filters)
    
    def fetch_results(self, url: str) -> List[Dict]:
        """
        Fetch and parse results from Finviz
        
        Args:
            url: Finviz screener URL
            
        Returns:
            List of stock dictionaries
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the screener table (updated class name)
            table = soup.find('table', {'class': 'screener_table'})
            if not table:
                # Fallback to other possible table classes
                table = soup.find('table', class_=lambda x: x and 'screener' in x.lower())
            
            if not table:
                return []
            
            # Get all rows directly from the table (no tbody in this version)
            # Row 0 is the header (in thead), actual data starts from row 1
            all_rows = table.find_all('tr')
            
            # Skip the first row (header row)
            data_rows = all_rows[1:]
            
            results = []
            for row in data_rows:
                cells = row.find_all('td')
                if len(cells) >= 11:
                    # Extract text from each cell, handling nested elements
                    stock = {
                        'ticker': cells[1].get_text(strip=True),
                        'company': cells[2].get_text(strip=True),
                        'sector': cells[3].get_text(strip=True),
                        'industry': cells[4].get_text(strip=True),
                        'country': cells[5].get_text(strip=True),
                        'market_cap': cells[6].get_text(strip=True),
                        'pe': cells[7].get_text(strip=True),
                        'price': cells[8].get_text(strip=True),
                        'change': cells[9].get_text(strip=True),
                        'volume': cells[10].get_text(strip=True)
                    }
                    results.append(stock)
            
            return results
            
        except Exception as e:
            print(f"Error fetching results: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def format_output(self, results: List[Dict], url: str, scanner_name: str = "daily-3up"):
        """
        Format and display results
        
        Args:
            results: List of stock dictionaries
            url: Finviz URL
            scanner_name: Name of the scanner
        """
        # Header
        today = datetime.now().strftime("%Y-%m-%d")
        print(f"Finviz Screener Results - {scanner_name} - {today}")
        print("=" * 40)
        print()
        
        # Criteria
        print("Screening Criteria:")
        print("- Daily 3% UP")
        print("- Price > $30")
        print("- Above 200 SMA")
        print("- ATR 2")
        print("- RVOL 2")
        print()
        
        # URL
        print("URL:")
        print(url)
        print("-" * 60)
        print()
        
        if not results:
            print("No results found.")
            return
        
        # Prepare table data
        table_data = []
        tickers = []
        
        for idx, stock in enumerate(results, 1):
            table_data.append([
                idx,
                stock['ticker'],
                stock['company'],
                stock['sector'],
                stock['industry'],
                stock['country'],
                stock['market_cap'],
                stock['pe'],
                stock['price'],
                stock['change'],
                stock['volume']
            ])
            tickers.append(stock['ticker'])
        
        # Headers
        headers = [
            "No", "Ticker", "Company", "Sector", "Industry", 
            "Country", "Market Cap", "P/E", "Price", "Change", "Volume"
        ]
        
        # Print table
        print(tabulate(table_data, headers=headers, tablefmt="grid"))
        print()
        
        # Ticker symbols
        print("Ticker Symbols:")
        print(", ".join(tickers))


def main():
    """Main function"""
    scanner = FinvizScanner()
    
    # Build URL for daily 3% up scanner
    url = scanner.daily_3up_scanner()
    
    # Fetch results
    results = scanner.fetch_results(url)
    
    # Format and display output
    scanner.format_output(results, url)


if __name__ == "__main__":
    main()
