import streamlit as st
from src.query import ask
from src.config import DB_PATH, CHROMA_DIR

st.set_page_config(page_title="Instagram Insights RAG", page_icon="🔎", layout="wide")
st.title("Instagram Insights RAG")
st.caption("Ask questions grounded in your exported Instagram data.")
if not DB_PATH.exists() or not CHROMA_DIR.exists():
    st.warning("Index not found. Run `python -m src.ingest` first.")
    st.stop()

question = st.text_input("Ask a question", placeholder="Find reels about non-technical Google career paths")
top_k = st.slider("Retrieved documents (Top-K)", 1, 10, 5)
if st.button("Ask", type="primary", disabled=not question.strip()):
    with st.spinner("Retrieving evidence and generating answer..."):
        answer, hits = ask(question, top_k)
    st.subheader("Answer")
    st.write(answer)
    if hits:
        st.subheader("Retrieved evidence")
        for h in hits:
            with st.expander(f"{h['id']} · distance {h['distance']:.3f}"):
                st.write(h["text"])
                st.json(h["metadata"])
st.divider()
st.caption("Static prototype: data is limited to the export files used to build this index.")
