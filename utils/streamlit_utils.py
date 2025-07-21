import streamlit as st
from typing import Dict

def show_download_buttons(files: Dict[str, bytes]):
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            st.download_button(
                label="Download CSV",
                data=files["csv"],
                file_name="products.csv",
                mime="text/csv"
            )
        with col2:
            st.download_button(
                label="Download XLSX",
                data=files["xlsx"],
                file_name="products.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        with col3:
            st.download_button(
                label="Download JSON",
                data=files["json"],
                file_name="products.json",
                mime="application/json"
            )
