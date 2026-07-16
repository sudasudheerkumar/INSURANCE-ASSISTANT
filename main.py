import streamlit as st

from insurance-assistant import answer_question
from quary import get_retriever


st.set_page_config(page_title="RAG Pipeline", layout="wide")
st.title("insurance-assistant")

question = st.text_input("Ask a question")

if question:
    retriever = get_retriever()
    result = answer_question(question, retriever)

    st.subheader("Answer")
    st.write(result["answer"])

    st.subheader("Sources")
    st.json(result["sources"])