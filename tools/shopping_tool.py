from langchain.tools import tool
import requests
from typing import List, Dict
import json
from dotenv import load_dotenv
import os

load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")  # replace or keep here
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@tool("search_shopping", return_direct=True)
def search_shopping(product_name: str) -> List[Dict]:
    """
    Search shopping results for a product name using Serper API.
    Returns a list of dictionaries with product info.
    """    
    if not product_name or len(product_name) < 3:
        return [{"error": "Product title not valid for shopping search."}]

    url = "https://google.serper.dev/shopping"
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": product_name, "gl": "us", "hl": "en", "num": 10}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        results = response.json().get("shopping", [])

        if not results:
            return [{"error": "No shopping results found."}]

        return [{
            "Product Title": item.get("title", ""),
            "Source": item.get("source", ""),
            "Link": item.get("link", ""),
            "Price": item.get("price", "N/A"),
            "Image URL": item.get("imageUrl") or item.get("thumbnail", ""),
            "Product ID": item.get("productId", ""),
            "Position": item.get("position", ""),
            "Category": item.get("category", "General"),
            "Description": item.get("description", item.get("title", "")),
            "Rating": item.get("rating", "N/A"),
            "Rating Count": item.get("ratingCount", "N/A"),
            "EAN": "",  # Serper API doesn’t provide this field
            "Product Code": str(abs(hash(item.get("title", ""))))[:20],
            "technical specs": "Specs not available in Serper shopping API.",
            "Input Type": "Product Name",
            "Country": "US"
        } for item in results]

    except requests.RequestException as e:
        return [{"error": f"Serper shopping search failed: {str(e)}"}]

