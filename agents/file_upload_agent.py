import pandas as pd
from typing import Dict, Any

class FileUploadAgent:
    def __init__(self, master_router_agent):
        self.master_router_agent = master_router_agent

    async def process_uploaded_file(self, uploaded_file) -> Dict[str, Any]:
        # Load the file into a DataFrame
        try:
            if uploaded_file.type == "application/json":
                df = pd.read_json(uploaded_file)
            elif uploaded_file.type in [
                "application/vnd.ms-excel",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ]:
                df = pd.read_excel(uploaded_file)
            else:
                df = pd.read_csv(uploaded_file)
        except Exception as e:
            return {"responses": [{"agent": "FileUploadAgent", "content": f"⚠️ Failed to read file: {e}"}]}

        columns = [col.lower() for col in df.columns]
        has_title = any("product title" in col for col in columns)
        has_asin = any("asin" in col for col in columns)
        has_ean = any("ean" in col for col in columns)

        queries = []
        for _, row in df.iterrows():
            if has_asin and pd.notna(row.get("ASIN", None)) and row["ASIN"] != "":
                queries.append(f"Find product info for identifier: {row['ASIN'].strip()}")
            elif has_ean and pd.notna(row.get("EAN", None)) and row["EAN"] != "":
                queries.append(f"Find product info for identifier: {row['EAN'].strip()}")
            elif has_title and pd.notna(row.get("Product Title", None)) and row["Product Title"] != "":
                queries.append(f"Find product info for product title: {row['Product Title'].strip()}")

        if not queries:
            return {"responses": [{"agent": "FileUploadAgent", "content": "⚠️ Uploaded file must contain at least one valid 'Product Title', 'ASIN', or 'EAN'."}]}

        # Run master router agent for each query to respect intent detection
        results = []
        for q in queries:
            response = await self.master_router_agent.run(q)
            results.append(response)

        # Aggregate all responses in one dictionary
        return {"responses": results}
