#!/usr/bin/env python3
"""Test script to verify all imports work correctly."""

import sys
import traceback

print(f"Python: {sys.version}")
print(f"Executable: {sys.executable}")
print("-" * 70)

# List of critical imports to test
tests = [
    ("FastAPI", "from fastapi import FastAPI"),
    ("Uvicorn", "import uvicorn"),
    ("Pydantic", "from pydantic import BaseModel"),
    ("Python-dotenv", "from dotenv import load_dotenv"),
    ("PyMuPDF (fitz)", "import fitz"),
    ("PyTesseract", "import pytesseract"),
    ("Pillow", "from PIL import Image"),
    ("LangChain", "from langchain import LLMChain"),
    ("LangChain Community", "from langchain_community.vectorstores import Chroma"),
    ("Sentence Transformers", "from sentence_transformers import SentenceTransformer"),
    ("ChromaDB", "import chromadb"),
    ("CrewAI", "from crewai import Agent, Task, Crew"),
    ("Google GenerativeAI", "import google.generativeai as genai"),
    ("Streamlit", "import streamlit as st"),
    ("ReportLab", "from reportlab.lib.pagesizes import letter"),
    ("Requests", "import requests"),
    ("BeautifulSoup4", "from bs4 import BeautifulSoup"),
    ("NumPy", "import numpy as np"),
    ("Pytest", "import pytest"),
]

passed = 0
failed = 0

for name, import_stmt in tests:
    try:
        exec(import_stmt)
        print(f"✓ {name}")
        passed += 1
    except Exception as e:
        print(f"✗ {name}: {e}")
        failed += 1

print("-" * 70)

# Try to import the app
print("\nTesting app.py import...")
try:
    from app import app
    print("✓ app.py imported successfully")
    passed += 1
except Exception as e:
    print(f"✗ app.py import failed: {e}")
    traceback.print_exc()
    failed += 1

print("-" * 70)
print(f"\nResults: {passed} passed, {failed} failed")

if failed > 0:
    sys.exit(1)
else:
    print("\n🎉 All imports successful! Application is ready to run.")
    sys.exit(0)
