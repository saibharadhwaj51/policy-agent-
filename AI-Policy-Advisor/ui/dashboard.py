"""
ui/dashboard.py
=================
Streamlit dashboard (Phase 9) — the main user-facing interface.

Run with:  streamlit run ui/dashboard.py

Pages: Upload, Summary, Comparison, Impact, Timeline, FAQs, Reports, Settings.
Calls api/services.py directly (no HTTP hop needed since Streamlit and the
pipeline run in the same Python process) -- the FastAPI layer in app.py is
for external/programmatic access, not required for the dashboard to work.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from api.services import ingest_uploaded_file, analyze_document, answer_question
from config import settings
from ui.components import metric_row, section_card, progress_steps
from utils.constants import POLICY_CATEGORIES

st.set_page_config(page_title="AI Policy Advisor", page_icon="📋", layout="wide")

if "analysis_results" not in st.session_state:
    st.session_state.analysis_results = None
if "doc_id" not in st.session_state:
    st.session_state.doc_id = None

st.sidebar.title("📋 AI Policy Advisor")
page = st.sidebar.radio(
    "Navigate",
    ["Upload", "Summary", "Comparison", "Impact", "Timeline", "FAQs", "Reports", "Ask a Question", "Settings"],
)

# ---------------- Upload Page ----------------
if page == "Upload":
    st.title("Upload a Policy Document")
    st.write("Upload a PDF (education, healthcare, HR, government circular, etc.) for analysis.")

    category = st.selectbox("Policy Category", POLICY_CATEGORIES)
    topic_hint = st.text_input("Topic hint (optional, improves government search)", "")
    uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"])

    if uploaded_file and st.button("Ingest & Analyze", type="primary"):
        dest = settings.upload_dir / uploaded_file.name
        dest.write_bytes(uploaded_file.getbuffer())

        steps = ["Parsing PDF", "Cleaning text", "Chunking", "Embedding", "Storing in vector DB", "Running agent crew"]
        progress_placeholder = st.empty()

        with progress_placeholder.container():
            progress_steps(2, steps)
            doc_id = ingest_uploaded_file(dest, category)
            st.session_state.doc_id = doc_id

            progress_steps(6, steps)
            results = analyze_document(doc_id, category, topic_hint)
            st.session_state.analysis_results = results

        st.success(f"Analysis complete for doc_id: {doc_id}")
        metric_row({
            "Category": category,
            "Sections Generated": len([k for k in results if k != "report_path"]),
        })

# ---------------- Result pages ----------------
elif page in ("Summary", "Comparison", "Impact", "Timeline", "FAQs"):
    st.title(page)
    if not st.session_state.analysis_results:
        st.info("Upload and analyze a document first (see the Upload page).")
    else:
        key_map = {
            "Summary": "summary", "Comparison": "comparison", "Impact": "impact",
            "Timeline": "timeline", "FAQs": "faqs",
        }
        section_card(page, st.session_state.analysis_results.get(key_map[page]))

# ---------------- Reports Page ----------------
elif page == "Reports":
    st.title("Download Report")
    if not st.session_state.analysis_results:
        st.info("Upload and analyze a document first.")
    else:
        report_path = Path(st.session_state.analysis_results["report_path"])
        if report_path.exists():
            with open(report_path, "rb") as f:
                st.download_button("Download PDF Report", f, file_name=report_path.name, mime="application/pdf")
        else:
            st.warning("Report file not found.")

# ---------------- Ask a Question Page ----------------
elif page == "Ask a Question":
    st.title("Ask a Question About This Document")
    if not st.session_state.doc_id:
        st.info("Upload a document first.")
    else:
        question = st.text_input("Your question")
        if question and st.button("Ask"):
            result = answer_question(st.session_state.doc_id, question)
            st.markdown(f"**Answer:** {result['answer']}")

# ---------------- Settings Page ----------------
elif page == "Settings":
    st.title("Settings")
    st.write(f"**Gemini model:** {settings.gemini_model}")
    st.write(f"**Embedding model:** {settings.embedding_model}")
    st.write(f"**Vector DB path:** {settings.chroma_db_path}")
    st.caption("Edit these in your .env file, then restart the app.")
