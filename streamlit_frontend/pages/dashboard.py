import streamlit as st

from api_client import WorkbenchAPIError, get_documents, get_health


st.markdown(
    """
    <div class="workbench-banner">
        <h1>Market Data Rights Workbench</h1>
        <p>
            Analyze market-data contracts, feeds, entitlements,
            licensing restrictions and duplicate products.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    health = get_health()
    backend_available = health.get("status") == "healthy"
except WorkbenchAPIError:
    backend_available = False

status_column, environment_column = st.columns(2)

with status_column:
    if backend_available:
        st.success("FastAPI backend is connected")
    else:
        st.error("FastAPI backend is unavailable")

with environment_column:
    st.info("Database: SQLite | LLM: OpenAI")

try:
    documents = get_documents() if backend_available else []
except WorkbenchAPIError as error:
    documents = []
    st.error(str(error))

total_documents = len(documents)
pdf_documents = sum(
    1 for document in documents
    if document.get("file_type", "").lower() == "pdf"
)
structured_documents = sum(
    1 for document in documents
    if document.get("file_type", "").lower()
    in {"csv", "xlsx", "json"}
)
processed_documents = sum(
    1 for document in documents
    if document.get("processing_status") == "processed"
)

column1, column2, column3, column4 = st.columns(4)

column1.metric("Corpus Documents", total_documents)
column2.metric("Contracts and PDFs", pdf_documents)
column3.metric("Structured Feeds", structured_documents)
column4.metric("Processed", processed_documents)

st.subheader("Processing workflow")

st.markdown(
    """
    1. Upload contracts and feed specifications.
    2. Parse structured and unstructured content.
    3. Detect exact duplicate documents.
    4. Retrieve relevant evidence using BM25.
    5. Use the LLM to interpret retrieved clauses.
    6. Return an evidence-based answer with citations.
    """
)

if documents:
    st.subheader("Recently processed documents")

    recent_documents = documents[:5]

    for document in recent_documents:
        with st.container(border=True):
            column1, column2, column3 = st.columns([3, 1, 1])

            column1.write(f"**{document.get('filename')}**")
            column2.write(document.get("file_type", "").upper())
            column3.write(document.get("processing_status", "Unknown"))
else:
    st.warning(
        "No documents have been processed. "
        "Open Corpus Ingestion to upload your corpus."
    )