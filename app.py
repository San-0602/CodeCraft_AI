
# File: app.py
# Project: CodeCraft AI
# Author: S. Sandhya (San-0602)
# Created: 03-06-2025

import streamlit as st
import cohere
import io
from fpdf import FPDF
import uuid
import json
from datetime import datetime

# API Key
co = cohere.Client(st.secrets["COHERE_API_KEY"])
st.set_page_config(page_title="CodeCraft AI", layout="wide")

# ---------- Custom CSS ---------- #
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(145deg, #1e1f26, #2c2f3f);
        color: #f0f0f0;
    }
    h1, h3, .stSelectbox label, .stTextInput label {
        color: #ffe600;
        font-weight: 800;
        text-shadow: 2px 2px 4px #00000080;
    }
    .stTextInput, .stSelectbox, .stDownloadButton, .stButton button {
        border-radius: 8px;
        font-weight: bold;
    }
    .stButton>button {
        background-color: #ffe600;
        color: #000;
        border: none;
        padding: 10px 20px;
        border-radius: 10px;
        box-shadow: 0 4px 10px rgba(255, 230, 0, 0.6);
    }
    .stButton>button:hover {
        background-color: #ffd700;
    }
    .share-btn {
        background: #25D366;
        color: white;
        border-radius: 8px;
        padding: 10px;
        font-weight: bold;
        cursor: pointer;
        margin: 10px 0;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Header ---------- #
st.title("🚀 CodeCraft AI")
st.caption("From Prompt to Project — Built for Final Year Warriors 💪")

st.markdown("""
<div style="background: #ffe600; color: #000; padding: 15px; border-radius: 12px; font-size: 16px; font-weight: bold;">
    ✨ Instantly generate code, report, and viva questions for your dream project. Just type your idea and hit GO!
</div>
""", unsafe_allow_html=True)

# ---------- Input Controls ---------- #
col1, col2, col3 = st.columns(3)
with col1:
    project_type = st.selectbox("Choose Project Type:", ["Web App", "Android App", "ML", "CLI Tool", "Other"])
with col2:
    difficulty = st.selectbox("Difficulty Level:", ["Beginner", "Intermediate", "Advanced"])
with col3:
    language = st.selectbox("Programming Language:", ["Python", "Java", "Kotlin", "JavaScript", "C++", "Other"])

topic = st.text_input("💡 Describe your project idea:")

# ---------- Prompt Builder ---------- #
def build_prompt(ptype, diff, lang, top):
    return f"Generate a {diff.lower()} {ptype.lower()} project in {lang}. Topic: {top}. Include code, project report, and viva questions."

# ---------- PDF Generator ---------- #
def create_pdf(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for line in content.split('\n'):
        pdf.multi_cell(0, 10, line.encode('latin-1', 'replace').decode('latin-1'))
    buf = io.BytesIO(pdf.output(dest='S').encode('latin-1'))
    return buf

# ---------- Session State ---------- #
if 'pdf_buffer' not in st.session_state:
    st.session_state.pdf_buffer = None
if 'generated_text' not in st.session_state:
    st.session_state.generated_text = ""

# ---------- Project Generator ---------- #
if st.button("⚙️ Generate My Project") and topic:
    st.info("Generating project with AI... please wait")
    try:
        prompt = build_prompt(project_type, difficulty, language, topic)
        response = co.generate(model='command-r-plus', prompt=prompt, max_tokens=1500)
        gen = response.generations[0].text.strip()
        st.session_state.generated_text = gen
        st.session_state.pdf_buffer = create_pdf(gen)
        st.success("🎉 Done! See the preview below and download if satisfied.")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

# ---------- Code Preview ---------- #
if st.session_state.generated_text:
    st.markdown("#### 📄 Project Preview")
    st.code(st.session_state.generated_text[:1000] + "...", language="text")

# ---------- Download + Share ---------- #
if st.session_state.pdf_buffer:
    st.download_button(
        label="💾 Download Project PDF",
        data=st.session_state.pdf_buffer,
        file_name=f"{topic[:20].replace(' ', '_')}_CodeCraft.pdf",
        mime="application/pdf"
    )
    st.markdown(f"""
    <a class='share-btn' href='https://twitter.com/intent/tweet?text=Just+generated+my+project+using+%23CodeCraftAI+%F0%9F%9A%80!+Try+it+out+now!'>
        📣 Share on Twitter/X
    </a>
    <a class='share-btn' href='https://www.linkedin.com/sharing/share-offsite/?url=https://codecraft-ai'>
        👔 Share on LinkedIn
    </a>
    """, unsafe_allow_html=True)

# ---------- Footer ---------- #
st.markdown("---")
st.markdown("Made with ❤️ by San-0602 | Connect on [GitHub](https://github.com/San-0602)")
