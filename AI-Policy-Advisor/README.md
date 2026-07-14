# AI Policy Advisor

A production-ready Agentic AI system that analyzes policy documents (education,
healthcare, environment, agriculture, cybersecurity, HR, college, government
circulars) using RAG + a 10-agent CrewAI crew.

Being built phase by phase — see `AI-Policy-Advisor-Master-Plan.md` for the
full roadmap. This README will grow with each phase.

## Phase 1 Setup (do this now)

**Prerequisites:** Python 3.10+ installed on your machine.

```bash
# 1. Move into the project folder
cd AI-Policy-Advisor

# 2. Create a virtual environment
python3 -m venv venv

# 3. Activate it
# macOS/Linux:
source venv/bin/activate
# Windows (PowerShell):
venv\Scripts\Activate.ps1

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create your real .env file from the template
cp .env.example .env
# then open .env and add your real GOOGLE_API_KEY (not required until Phase 8)

# 6. Run the Phase 1 smoke test
python main.py
```

### Expected output

You should see console log lines like:

```
2026-07-10 10:00:00 | INFO     | __main__ | AI Policy Advisor — Phase 1 environment check
2026-07-10 10:00:00 | INFO     | __main__ | Gemini model configured as: gemini-1.5-pro
2026-07-10 10:00:00 | INFO     | __main__ | Embedding model configured as: all-MiniLM-L6-v2
2026-07-10 10:00:00 | INFO     | __main__ | Chroma DB path: /.../AI-Policy-Advisor/vector_db
2026-07-10 10:00:00 | WARNING  | __main__ | GOOGLE_API_KEY is still the placeholder value...
2026-07-10 10:00:00 | INFO     | __main__ | Phase 1 environment check complete — everything loaded correctly.
```

And a new file at `logs/app.log` containing the same lines.

## Phase 2 Setup (PDF Parsing + OCR + Cleaning)

**Additional prerequisite:** the Tesseract OCR *engine* (not just the Python
wrapper) must be installed on your system — `pytesseract` only talks to it.

```bash
# macOS
brew install tesseract

# Ubuntu/Debian
sudo apt-get install tesseract-ocr

# Windows
# Download installer: https://github.com/UB-Mannheim/tesseract/wiki
# Then add the install folder to your PATH
```

Then, with your venv still active:

```bash
pip install -r requirements.txt   # picks up pymupdf, pytesseract, pillow
pytest tests/test_pdf_pipeline.py -v
```

### Expected output

```
tests/test_pdf_pipeline.py::test_text_pdf_uses_text_layer_not_ocr PASSED
tests/test_pdf_pipeline.py::test_scanned_pdf_falls_back_to_ocr PASSED
tests/test_pdf_pipeline.py::test_clean_text_dehyphenates PASSED
tests/test_pdf_pipeline.py::test_clean_text_collapses_whitespace PASSED
tests/test_pdf_pipeline.py::test_clean_document_pages_removes_repeated_headers PASSED

===== 5 passed in ~2-4s =====
```

You can also try it manually:

```python
from rag.parser import parse_pdf
from rag.cleaner import clean_document_pages

doc = parse_pdf("assets/sample_scanned_policy.pdf")
print(doc.pages[0].source)   # "ocr"
print(doc.full_text)
```

## Full Setup (all 10 phases — complete system)

### 1. Prerequisites
- Python 3.10+
- Tesseract OCR engine (`brew install tesseract` / `apt-get install tesseract-ocr` / [Windows installer](https://github.com/UB-Mannheim/tesseract/wiki))
- A free [Google Gemini API key](https://aistudio.google.com/apikey)

### 2. Install

```bash
cd AI-Policy-Advisor
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\Activate.ps1
pip install -r requirements.txt
cp .env.example .env
# Edit .env and set GOOGLE_API_KEY=your_real_key
```

### 3. Run tests

```bash
pytest tests/ -v
```

### 4. Run it — three ways

**A) Streamlit Dashboard (recommended for first use)**
```bash
streamlit run ui/dashboard.py
```
Open the URL it prints, go to **Upload**, pick a category, upload a PDF (try `assets/sample_text_policy.pdf` or `assets/sample_scanned_policy.pdf`), click **Ingest & Analyze**.

**B) FastAPI backend**
```bash
uvicorn app:app --reload
```
Swagger UI at `http://localhost:8000/docs`. Flow: `POST /api/v1/upload` → `POST /api/v1/analyze` → `GET /api/v1/report/{doc_id}`.

**C) CLI (scripting / batch use)**
```bash
python main.py assets/sample_text_policy.pdf --category education --topic "digital literacy"
```

### 5. Docker (optional, runs both API + Dashboard)

```bash
docker-compose up --build
```
API on `:8000`, Dashboard on `:8501`.

## The 10 Agents

| Agent | File | Job |
|---|---|---|
| Reader | `agents/reader_agent.py` | Structures raw document facts |
| Summary | `agents/summary_agent.py` | 2-line / 10-line / detailed summaries |
| Comparison | `agents/comparison_agent.py` | Diffs against a previous version (searches internal DB via its tool) |
| Impact Analysis | `agents/impact_agent.py` | Per-stakeholder pros/cons/risk |
| Recommendation | `agents/recommendation_agent.py` | Action items & compliance checklist |
| Timeline | `agents/timeline_agent.py` | Chronological policy history |
| Government Search | `agents/government_agent.py` | Live web search for circulars/notifications |
| FAQ | `agents/faq_agent.py` | Anticipated stakeholder Q&A |
| Report Generator | `agents/report_agent.py` + `tools/report_builder.py` | Assembles + renders the final PDF |
| Orchestrator | `agents/orchestrator.py` | Sequences all 9 agents, wires context between them |

## What was verified in the build sandbox vs. what you'll verify locally

This project was built in an offline sandbox with no internet access, so packages like `crewai`, `chromadb`, `sentence-transformers`, and `pymupdf` could not be installed or executed there. What **was** verified directly, with real passing output:
- Every one of the 54 `.py` files compiles with zero syntax errors
- `rag/chunker.py` — full functional test: correct chunk counts and exact word-level overlap
- `tools/report_builder.py` — full functional test: builds a real, valid, non-empty PDF (`%PDF` signature confirmed, rendered and visually inspected)
- `rag/parser.py` + `rag/cleaner.py` logic — validated using equivalent tools (`pdftotext`, `pdftoppm`, real Tesseract OCR) against two purpose-built sample PDFs (one digital, one scanned)

Everything involving Gemini, ChromaDB, Sentence Transformers, and the live CrewAI crew execution needs your real API key and full `pip install`, so that's the first thing to run locally.

## Project Status

- [x] Phase 1 — Project Planning & Environment Setup
- [x] Phase 2 — PDF Ingestion Pipeline (Parsing + OCR + Cleaning)
- [x] Phase 3 — Chunking & Embeddings
- [x] Phase 4 — Vector Database & Retrieval (RAG)
- [x] Phase 5 — CrewAI Foundation + Reader Agent + Orchestrator Agent
- [x] Phase 6 — Summary Agent + Comparison Agent
- [x] Phase 7 — Impact Analysis Agent + Recommendation Agent
- [x] Phase 8 — Timeline Agent + Government Search Agent + FAQ Agent
- [x] Phase 9 — Report Generator Agent + Streamlit Dashboard
- [x] Phase 10 — FastAPI + Production Readiness (Docker included)
