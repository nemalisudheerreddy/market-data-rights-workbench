import streamlit as st


st.title("About the Workbench")

st.markdown(
    """
    The Market Data Rights Workbench analyzes contracts and feed
    information to support:

    - Contract-rights validation
    - Feed and product comparison
    - Duplicate-document detection
    - Entitlement validation
    - Usage-rights analysis
    - Clause-supported natural-language answers
    - Vendor-rationalization analysis

    ### Current architecture

    - **Frontend:** Streamlit
    - **Backend:** FastAPI
    - **Database:** SQLite
    - **Retrieval:** BM25 lexical retrieval
    - **LLM:** OpenAI through the backend
    - **Parsing:** PyMuPDF, python-docx and pandas

    ### Important distinction

    The system must distinguish between:

    - Contractual permission
    - Technical entitlement
    - Observed usage
    - Business recommendation

    A technical entitlement does not prove that contractual use is
    permitted.
    """
)

st.info(
    "This application is a synthetic prototype and legal "
    "decision-support system. It is not a substitute for attorney review."
)