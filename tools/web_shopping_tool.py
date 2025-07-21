from langchain.tools import tool
import requests
from typing import List, Dict
import json
from dotenv import load_dotenv
import os
from tools.web_ean_asin_tool import search_web_ean_asin
from tools.shopping_tool import search_shopping
# Load environment variables
load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")   # You may want to move this to .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")



@tool
def search_product_combined(code_or_name: str) -> List[Dict]:
    """Combine web and shopping search to return enriched product information."""
    web_results = search_web_ean_asin(code_or_name)

    if "error" in web_results[0]:
        return web_results

    product_title = web_results[0].get("Product Title", "")
    product_link = web_results[0].get("Link", "")

    if not product_title or len(product_title) < 3:
        return [{
            "Product Title": product_title or code_or_name,
            "Description": web_results[0].get("Description", ""),
            "Price": "Not available",
            "Link": product_link,
            "Note": "No valid product title found for shopping search. Showing web search result only."
        }]

    shopping_results = search_shopping(product_title)

    if isinstance(shopping_results, list) and shopping_results and "error" in shopping_results[0]:
        return [{
            "Product Title": product_title,
            "Description": web_results[0].get("Description", ""),
            "Price": "Not available",
            "Link": product_link,
            "Note": shopping_results[0]["error"]
        }]

    enriched_results = []
    for item in shopping_results:
        item["Product Page Link"] = product_link
        enriched_results.append(item)

    return enriched_results
