from langchain.tools import tool
import requests
from typing import List, Dict
import json
from dotenv import load_dotenv
import os
# Load environment variables
load_dotenv()
SERPER_API_KEY = os.getenv("SERPER_API_KEY")   # You may want to move this to .env
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

@tool
def search_web_ean_asin(code: str) -> List[Dict]:
    """Search product info from web by EAN or ASIN code."""
    url = "https://google.serper.dev/search"
    headers = {"X-API-KEY": SERPER_API_KEY, "Content-Type": "application/json"}
    payload = {"q": code, "gl": "us", "location": "United States", "num": 10}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(payload))
        response.raise_for_status()
        results = response.json().get("organic", [])

        if not results:
            return [{"error": "No results found for the code."}]

        top_result = results[0]
        return [{
            "Product Title": top_result.get("title", ""),
            "EAN": code,
            "Product Code": str(abs(hash(top_result.get("title", ""))))[:20],
            "Category": "Unknown",
            "Price": "Not available",
            "Description": top_result.get("snippet", ""),
            "Image url1": "",
            "Image url2": "",
            "Image url3": "",
            "Image url4": "",
            "technical specs": "Not available in web search.",
            "Link": top_result.get("link", ""),
            "Input Type": "EAN" if len(code) in [8, 13] else "ASIN",
            "Country": "US"
        }]
    except requests.RequestException as e:
        return [{"error": f"Serper web search failed: {str(e)}"}]

