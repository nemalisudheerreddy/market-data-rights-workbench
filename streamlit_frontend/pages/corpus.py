import streamlit as st

from api_client import WorkbenchAPIError, upload_document


st.title("Corpus Ingestion")

st.write(
    """
    Upload contracts, schedules, amendments, addenda, feed specifications,
    field dictionaries, entitlement exports and pricing information.
    """
)

uploaded_files = st.file_uploader(
    "Select corpus files",
    type=["pdf", "docx", "csv", "xlsx", "json", "txt", "md"],
    accept_multiple_files=True,
    help="Maximum upload size is configured as 200 MB per file.",
)

if uploaded_files:
    st.write(f"Selected files: **{len(uploaded_files)}**")

    for uploaded_file in uploaded_files:
        st.caption(
            f"{uploaded_file.name} — "
            f"{uploaded_file.size / 1024:.1f} KB"
        )

    if st.button(
        "Process selected files",
        type="primary",
        use_container_width=True,
    ):
        progress = st.progress(0)
        status = st.empty()
        results = []

        for index, uploaded_file in enumerate(uploaded_files, start=1):
            status.write(f"Processing {uploaded_file.name}...")

            try:
                result = upload_document(uploaded_file)
                results.append(
                    {
                        "filename": uploaded_file.name,
                        "status": (
                            "Duplicate"
                            if result.get("duplicate")
                            else "Processed"
                        ),
                        "document_id": result.get("document_id"),
                        "characters": result.get(
                            "characters_extracted",
                            0,
                        ),
                    }
                )
            except WorkbenchAPIError as error:
                results.append(
                    {
                        "filename": uploaded_file.name,
                        "status": "Failed",
                        "document_id": None,
                        "characters": 0,
                        "error": str(error),
                    }
                )

            progress.progress(index / len(uploaded_files))

        status.success("Corpus processing completed")

        for result in results:
            if result["status"] == "Processed":
                st.success(
                    f"{result['filename']} processed successfully. "
                    f"Document ID: {result['document_id']}"
                )
            elif result["status"] == "Duplicate":
                st.warning(
                    f"{result['filename']} is an exact duplicate. "
                    f"Existing document ID: {result['document_id']}"
                )
            else:
                st.error(
                    f"{result['filename']} failed: "
                    f"{result.get('error')}"
                )
else:
    st.info("Select one or more files to begin processing.")

with st.expander("Supported corpus types"):
    st.markdown(
        """
        **Unstructured**

        - PDF contracts
        - DOCX agreements
        - TXT and Markdown documents

        **Structured**

        - CSV feed catalogs
        - XLSX field dictionaries
        - JSON entitlement and usage files
        """
    )