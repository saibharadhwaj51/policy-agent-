FROM python:3.11-slim

# System dependencies: Tesseract OCR + fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    libgl1 \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p uploads reports vector_db logs

EXPOSE 8000 8501

# Default: run the FastAPI backend. Override CMD to run Streamlit instead:
#   docker run <image> streamlit run ui/dashboard.py --server.address 0.0.0.0
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
