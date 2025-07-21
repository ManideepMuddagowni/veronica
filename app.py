import streamlit as st
import asyncio
import nest_asyncio

from agents.shopping_agent import create_agent as create_shopping_agent
from agents.web_shopping_agent import create_agent as create_web_agent
from agents.intent_understanding_agent import IntentUnderstandingAgent
from agents.master_route_agent import MasterRouterAgent, AgentWrapper

from utils.product_utils import extract_all_products, save_products_to_files
from utils.streamlit_utils import show_download_buttons
import pandas as pd

# Patch asyncio for Streamlit
nest_asyncio.apply()

st.set_page_config(page_title="🛒 Veronica")
st.title("🧠 Veronica")

if "master_agent" not in st.session_state:
    shopping_agent = create_shopping_agent()
    web_agent = create_web_agent()

    intent_agent = IntentUnderstandingAgent()

    agents_dict = {
        "shopping_agent": AgentWrapper("ShoppingAgent", shopping_agent),
        "web_shopping_agent": AgentWrapper("WebShoppingAgent", web_agent),
    }

    st.session_state.master_agent = MasterRouterAgent(intent_agent, agents_dict)

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Display chat history
for msg in st.session_state.chat_history:
    role = msg["role"]
    content = msg["content"]

    if isinstance(content, dict) and "responses" in content:
        for item in content["responses"]:
            agent_name = item.get("agent", "Unknown Agent")
            response = item.get("content", "")

            with st.chat_message(role):
                st.markdown(f"#### 🤖 Agent: `{agent_name}`")

                if isinstance(response, list):
                    for product in response:
                        st.markdown(f"**🛒 Product Title:** {product.get('Product Title', '')}")
                        st.markdown(f"- **Category:** {product.get('Category', '')}")
                        st.markdown(f"- **Price:** {product.get('Price', '')}")
                        st.markdown(f"- **Rating:** {product.get('Rating', '')}")
                        st.markdown(f"- **Description:** {product.get('Description', '')}")
                        st.markdown(f"- **Source:** {product.get('Source', '')}")
                        if url := product.get("url", "") or product.get("Link", ""):
                            st.markdown(f"[🔗 View Product]({url})")
                        st.markdown("---")
                elif isinstance(response, str):
                    st.markdown(response)
                else:
                    st.warning("⚠️ Unexpected response format.")
    else:
        st.chat_message(role).markdown(content)

# Chat input
user_input = st.chat_input("Ask me about any product with (title, ASIN, EAN, etc.)")

if user_input:
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    st.chat_message("user").markdown(user_input)

    with st.spinner("🤖 Routing your query to the right agent..."):
        loop = asyncio.get_event_loop()
        response = loop.run_until_complete(st.session_state.master_agent.run(user_input))

    st.session_state.chat_history.append({"role": "assistant", "content": response})

    with st.chat_message("assistant"):
        if isinstance(response, dict) and "responses" in response:
            for item in response["responses"]:
                agent_name = item.get("agent", "Unknown Agent")
                response_content = item.get("content", "")

                st.markdown(f"#### 🤖 Agent: `{agent_name}`")

                if isinstance(response_content, list):
                    for product in response_content:
                        st.markdown(f"**🛒 Product Title:** {product.get('Product Title', '')}")
                        st.markdown(f"- **Category:** {product.get('Category', '')}")
                        st.markdown(f"- **Price:** {product.get('Price', '')}")
                        st.markdown(f"- **Rating:** {product.get('Rating', '')}")
                        st.markdown(f"- **Description:** {product.get('Description', '')}")
                        st.markdown(f"- **Source:** {product.get('Source', '')}")
                        if url := product.get("url", "") or product.get("Link", ""):
                            st.markdown(f"[🔗 View Product]({url})")
                        st.markdown("---")
                elif isinstance(response_content, str):
                    st.markdown(response_content)
                else:
                    st.warning("⚠️ Unexpected response format.")
        else:
            st.markdown(response)

    # Save and show download buttons
    products = extract_all_products(response)
    if products:
        files = save_products_to_files(products)
        st.markdown("---") 
        show_download_buttons(files)
# ---- FILE UPLOAD ----
st.markdown("---")
st.header("📁 Batch Product Lookup")

show_upload = st.checkbox("Enable batch upload via CSV/Excel")

if show_upload:
    uploaded_file = st.file_uploader("Upload product file (CSV or Excel)", type=["csv", "xlsx"])

    if uploaded_file is not None:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)

        st.write("### 📊 Uploaded File Preview:")
        st.dataframe(df.head())

        has_title = "Product Title" in df.columns
        has_asin = "ASIN" in df.columns
        has_ean = "EAN" in df.columns

        if not (has_title or has_asin or has_ean):
            st.error("File must contain at least one of: 'Product Title', 'ASIN', or 'EAN'")
        else:
            if st.button("🔍 Search products via agents"):

                async def process_rows():
                    all_products = []
                    progress = st.progress(0, text="🔄 Processing rows...")
                    total_rows = len(df)
                    success_count = 0

                    for idx, row in df.iterrows():
                        query = None

                        if has_title and pd.notna(row.get("Product Title")):
                            query = f"Find product info for product title: {row['Product Title']}"
                        elif has_asin and pd.notna(row.get("ASIN")):
                            query = f"Find product info for identifier: {row['ASIN']}"
                        elif has_ean and pd.notna(row.get("EAN")):
                            query = f"Find product info for identifier: {row['EAN']}"
                        else:
                            continue

                        response = await st.session_state.master_agent.run(query)
                        products = extract_all_products(response)

                        if products:
                            success_count += 1
                            all_products.extend(products)

                            st.markdown(f"### ✅ Row {idx + 1}")
                            for p in products:
                                st.markdown(f"**🛒 Product Title:** {p.get('Product Title', '')}")
                                st.markdown(f"- **Category:** {p.get('Category', '')}")
                                st.markdown(f"- **Price:** {p.get('Price', '')}")
                                st.markdown(f"- **Rating:** {p.get('Rating', '')}")
                                st.markdown(f"- **Description:** {p.get('Description', '')}")
                                st.markdown(f"- **Source:** {p.get('Source', '')}")
                                if url := p.get("url") or p.get("Link"):
                                    st.markdown(f"[🔗 View Product]({url})")
                                st.markdown("---")
                        else:
                            st.warning(f"⚠️ No products found for row {idx + 1}")

                        progress.progress((idx + 1) / total_rows, text=f"🔄 Row {idx + 1}/{total_rows}")

                    st.session_state.batch_products = all_products
                    st.session_state.batch_processing_done = True
                    st.session_state.success_count = success_count
                    st.session_state.total_rows = total_rows
                    st.rerun()

                asyncio.run(process_rows())
                
                
                
st.markdown("---")
st.header("📈 Bulk SEO Metadata Generation")

show_seo_upload = st.checkbox("Enable SEO generation via CSV")

if show_seo_upload:
    seo_file = st.file_uploader("Upload CSV with product names for SEO", type=["csv"])

    if seo_file:
        df_seo = pd.read_csv(seo_file)

        if "Product Title" not in df_seo.columns:
            st.error("CSV must contain a 'Product Title' column.")
        else:
            st.write("### Preview of Uploaded Products for SEO:")
            st.dataframe(df_seo.head())

            if st.button("⚙️ Generate SEO Metadata"):
                async def process_seo_rows():
                    seo_results = []
                    progress = st.progress(0, text="🚀 Generating SEO metadata...")
                    total = len(df_seo)

                    for i, row in df_seo.iterrows():
                        product_name = row["Product Title"]

                        query = (
                            f"Generate SEO content for the following product:\n"
                            f"{product_name}\n"
                            f"Return JSON with keys: meta_title, description, keywords, category."
                        )

                        response = await st.session_state.master_agent.run(query)

                        # This assumes the SEO agent responds with a JSON string
                        seo_entry = {
                            "Product Title": product_name,
                            "Meta Title": "",
                            "Description": "",
                            "Keywords": "",
                            "Category": "",
                        }

                        if isinstance(response, dict) and "responses" in response:
                            for item in response["responses"]:
                                if isinstance(item["content"], str):
                                    import json
                                    try:
                                        content = json.loads(item["content"])
                                        seo_entry.update({
                                            "Meta Title": content.get("meta_title", ""),
                                            "Description": content.get("description", ""),
                                            "Keywords": content.get("keywords", ""),
                                            "Category": content.get("category", ""),
                                        })
                                    except json.JSONDecodeError:
                                        pass

                        seo_results.append(seo_entry)
                        progress.progress((i + 1) / total, text=f"Processed {i+1}/{total}")

                    result_df = pd.DataFrame(seo_results)
                    st.session_state.seo_result_df = result_df
                    st.session_state.seo_generation_done = True
                    st.rerun()

                asyncio.run(process_seo_rows())
                
if st.session_state.get("seo_generation_done", False):
    st.markdown("### ✅ SEO Metadata Generated:")
    st.dataframe(st.session_state.seo_result_df)

    csv = st.session_state.seo_result_df.to_csv(index=False).encode("utf-8")
    st.download_button("📥 Download SEO Metadata CSV", data=csv, file_name="seo_metadata_output.csv", mime="text/csv")
