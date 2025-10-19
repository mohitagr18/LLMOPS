# mcp_server/amazon_tools.py

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from mcp.server.fastmcp import FastMCP
import requests
from bs4 import BeautifulSoup
import re
from typing import List, Dict

# Initialize FastMCP server
mcp = FastMCP("Amazon Product Search Tools")


def search_amazon_products(query: str, max_results: int = 3) -> List[Dict]:
    """
    Search Amazon for products and return basic info
    
    Args:
        query: Search query (e.g., "Bt insecticide", "neem oil spray")
        max_results: Number of results to return (default 3)
    
    Returns:
        List of products with name, price, url, rating
    """
    try:
        # Format query for Amazon search
        search_url = f"https://www.amazon.com/s?k={query.replace(' ', '+')}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
        }
        
        response = requests.get(search_url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        products = []
        product_items = soup.find_all('div', {'data-component-type': 's-search-result'})
        
        for item in product_items[:max_results]:
            try:
                # Extract product name
                title_elem = item.find('h2', class_='s-size-mini')
                if not title_elem:
                    title_elem = item.find('span', class_='a-text-normal')
                product_name = title_elem.get_text(strip=True) if title_elem else "Unknown Product"
                
                # Extract product URL
                link_elem = item.find('a', class_='a-link-normal')
                product_url = "https://www.amazon.com" + link_elem['href'] if link_elem and 'href' in link_elem.attrs else None
                
                # Extract price
                price_whole = item.find('span', class_='a-price-whole')
                price_fraction = item.find('span', class_='a-price-fraction')
                if price_whole:
                    price = f"${price_whole.get_text(strip=True)}{price_fraction.get_text(strip=True) if price_fraction else ''}"
                else:
                    price = "Price not available"
                
                # Extract rating
                rating_elem = item.find('span', class_='a-icon-alt')
                rating = rating_elem.get_text(strip=True) if rating_elem else "No rating"
                
                if product_url:
                    products.append({
                        "name": product_name[:100],  # Truncate long names
                        "price": price,
                        "url": product_url,
                        "rating": rating
                    })
            except Exception as e:
                continue
        
        return products if products else [{"error": "No products found", "query": query}]
        
    except Exception as e:
        return [{"error": f"Search failed: {str(e)}", "query": query}]


@mcp.tool()
def search_agricultural_products(product_query: str, max_results: int = 3) -> dict:
    """
    Search Amazon for agricultural products (pesticides, fungicides, tools, etc.)
    
    Args:
        product_query: Product to search for (e.g., "Bt insecticide for caterpillars")
        max_results: Number of results to return (default 3)
        
    Returns:
        Dictionary with search results
    """
    products = search_amazon_products(product_query, max_results)
    
    return {
        "query": product_query,
        "results_count": len(products),
        "products": products
    }


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
