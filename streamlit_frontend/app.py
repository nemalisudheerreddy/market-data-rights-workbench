import streamlit as st


st.set_page_config(
    page_title="Market Data Rights Workbench",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        .main .block-container {
            padding-top: 1.5rem;
            padding-bottom: 3rem;
            max-width: 1450px;
        }

        [data-testid="stSidebar"] {
            background-color: #071C33;
        }

        [data-testid="stSidebar"] * {
            color: #FFFFFF;
        }

        div[data-testid="stMetric"] {
            background: #FFFFFF;
            border: 1px solid #E2E8F0;
            border-radius: 12px;
            padding: 16px;
        }

        .workbench-banner {
            background: linear-gradient(110deg, #071C33, #0070AD);
            color: white;
            padding: 24px 28px;
            border-radius: 14px;
            margin-bottom: 24px;
        }

        .workbench-banner h1 {
            margin: 0;
            color: white;
            font-size: 2rem;
        }

        .workbench-banner p {
            margin: 8px 0 0 0;
            color: #DDEEFF;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.sidebar.markdown("## Market Data Rights")
st.sidebar.caption("Contract and entitlement intelligence")

pages = {
    "Workbench": [
        st.Page(
            "pages/dashboard.py",
            title="Dashboard",
            icon=":material/dashboard:",
            default=True,
        ),
        st.Page(
            "pages/corpus.py",
            title="Corpus Ingestion",
            icon=":material/upload_file:",
        ),
        st.Page(
            "pages/documents.py",
            title="Document Inventory",
            icon=":material/description:",
        ),
    ],
    "Analysis": [
        st.Page(
            "pages/assistant.py",
            title="Rights Assistant",
            icon=":material/gavel:",
        ),
    ],
    "Information": [
        st.Page(
            "pages/about.py",
            title="About",
            icon=":material/info:",
        ),
    ],
}

navigation = st.navigation(pages)
navigation.run()