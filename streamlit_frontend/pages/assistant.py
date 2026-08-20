import streamlit as st

from api_client import WorkbenchAPIError, ask_question


st.title("Natural-Language Rights Assistant")

st.warning(
    "This application provides contract decision support and does not "
    "provide final legal advice."
)

if "messages" not in st.session_state:
    st.session_state.messages = []

if st.button("Clear conversation"):
    st.session_state.messages = []
    st.rerun()

example_question = st.selectbox(
    "Example questions",
    [
        "",
        "Can the feed be used for external redistribution?",
        "Which clauses govern retention and archival rights?",
        "Are derived outputs permitted for client reporting?",
        "Can the data be used for model training or RAG?",
        "Are there technical entitlements that conflict with the contract?",
    ],
)

if example_question and st.button("Ask selected question"):
    st.session_state.pending_question = example_question

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message.get("sources"):
            with st.expander("Retrieved sources"):
                for source in message["sources"]:
                    st.write(
                        f"- {source.get('filename')} "
                        f"(score: {source.get('score', 0):.3f})"
                    )

question = st.chat_input(
    "Ask a contract, entitlement or usage-rights question"
)

if "pending_question" in st.session_state:
    question = st.session_state.pop("pending_question")

if question:
    st.session_state.messages.append(
        {"role": "user", "content": question}
    )

    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant"):
        with st.spinner("Retrieving and analyzing contract evidence..."):
            try:
                result = ask_question(question)
                answer = result.get(
                    "answer",
                    "No answer was returned.",
                )
                sources = result.get("retrieved_sources", [])

                st.markdown(answer)

                if sources:
                    with st.expander("Retrieved sources"):
                        for source in sources:
                            st.write(
                                f"- {source.get('filename')} "
                                f"(score: "
                                f"{source.get('score', 0):.3f})"
                            )

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                        "sources": sources,
                    }
                )
            except WorkbenchAPIError as error:
                error_message = str(error)
                st.error(error_message)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": error_message,
                    }
                )