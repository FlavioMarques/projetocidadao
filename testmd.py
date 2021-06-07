from pathlib import Path
import streamlit as st


def read_markdown_file(markdown_file):
    return Path(markdown_file, encoding='utf-8').read_text()

intro_markdown = read_markdown_file("testmd.md")
readme_text = st.markdown(intro_markdown, unsafe_allow_html=True)


