import pandas as pd
import io
import json
from typing import List, Dict, Any

def extract_all_products(response: Dict[str, Any]) -> List[Dict[str, Any]]:
    products = []
    if isinstance(response, dict) and "responses" in response:
        for item in response["responses"]:
            content = item.get("content", [])
            if isinstance(content, list):
                # content is already a list of product dicts
                products.extend(content)
            elif isinstance(content, dict):
                # if content is a dict, try to find list(s) inside values
                for val in content.values():
                    if isinstance(val, list):
                        products.extend(val)
    return products


def save_products_to_files(products: List[Dict]) -> Dict[str, bytes]:
    df = pd.DataFrame(products)

    # CSV in memory
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    csv_data = csv_buffer.getvalue().encode('utf-8')

    # XLSX in memory
    xlsx_buffer = io.BytesIO()
    df.to_excel(xlsx_buffer, index=False, engine='openpyxl')
    xlsx_data = xlsx_buffer.getvalue()

    # JSON in memory
    json_str = json.dumps(products, ensure_ascii=False, indent=4)
    json_data = json_str.encode('utf-8')

    return {
        "csv": csv_data,
        "xlsx": xlsx_data,
        "json": json_data
    }
