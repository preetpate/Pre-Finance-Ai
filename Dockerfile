FROM python:3.11-slim

WORKDIR /app

# System deps for PyMuPDF and argon2
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ libffi-dev libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source
COPY backend/ ./backend/
COPY .env.example .env

# Create data directories (used only for SQLite local fallback)
RUN mkdir -p data/uploads data/vector_store

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
