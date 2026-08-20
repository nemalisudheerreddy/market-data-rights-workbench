import pandas as pd
import streamlit as st

from api_client import WorkbenchAPIError, get_documents


st.title("Document Inventory")

try:
    documents = get_documents()
except WorkbenchAPIError as error:
    st.error(str(error))
    st.stop()

if not documents:
    st.info("The document inventory is empty.")
    st.stop()

dataframe = pd.DataFrame(documents)

search_term = st.text_input(
    "Search by filename",
    placeholder="Enter contract, vendor or feed name",
)

file_types = sorted(
    dataframe["file_type"].dropna().unique().tolist()
)

selected_types = st.multiselect(
    "Filter by file type",
    options=file_types,
    default=file_types,
)

filtered = dataframe.copy()

if search_term:
    filtered = filtered[
        filtered["filename"]
        .str.contains(search_term, case=False, na=False)
    ]

if selected_types:
    filtered = filtered[
        filtered["file_type"].isin(selected_types)
    ]

column1, column2 = st.columns(2)
column1.metric("Displayed Documents", len(filtered))
column2.metric("Total Documents", len(dataframe))

display_columns = [
    column for column in [
        "id",
        "filename",
        "file_type",
        "parser_name",
        "processing_status",
        "created_at",
        "sha256",
    ]
    if column in filtered.columns
]

st.dataframe(
    filtered[display_columns],
    use_container_width=True,
    hide_index=True,
)

csv_data = filtered[display_columns].to_csv(index=False)

st.download_button(
    "Download inventory as CSV",
    data=csv_data,
    file_name="market_data_document_inventory.csv",
    mime="text/csv",
)