# test_amazon_integration.py

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'mcp_server'))

from amazon_tools import search_amazon_products


def test_amazon_search():
    """
    Test Amazon product search functionality
    """
    print("\n" + "=" * 70)
    print("PHASE 4 TEST: Amazon Product Integration")
    print("=" * 70)
    
    # Test searches for common agricultural products
    test_queries = [
        "Bt insecticide organic",
        "neem oil spray concentrate",
        "spinosad spray caterpillars"
    ]
    
    for query in test_queries:
        print(f"\n{'─' * 70}")
        print(f"🔍 Searching: {query}")
        print("─" * 70)
        
        products = search_amazon_products(query, max_results=3)
        
        if products and "error" not in products[0]:
            print(f"✓ Found {len(products)} products:\n")
            for i, product in enumerate(products, 1):
                print(f"{i}. {product['name']}")
                print(f"   💰 {product['price']}")
                print(f"   ⭐ {product['rating']}")
                print(f"   🔗 {product['url'][:80]}...\n")
        else:
            print(f"✗ No products found or error occurred")
            if products:
                print(f"   Error: {products[0].get('error', 'Unknown')}")
    
    print("\n" + "=" * 70)
    print("PHASE 4 TEST COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    test_amazon_search()
