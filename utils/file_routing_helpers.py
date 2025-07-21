import pandas as pd

def detect_file_columns(file) -> dict:
    df = pd.read_csv(file)

    if 'Product Title' in df.columns and not df['Product Title'].dropna().empty:
        return {"agent": "shopping_agent", "queries": df['Product Title'].dropna().tolist()}

    elif 'ASIN' in df.columns and not df['ASIN'].dropna().empty:
        return {"agent": "web_shopping_agent", "queries": df['ASIN'].dropna().tolist()}

    elif 'EAN' in df.columns and not df['EAN'].dropna().empty:
        return {"agent": "web_shopping_agent", "queries": df['EAN'].dropna().tolist()}

    else:
        return {"agent": None, "queries": []}
