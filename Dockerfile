FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src ./src
COPY schema.sql .

ENV PYTHONPATH=src
# Download once at build time so containers start ready
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')"

CMD ["uvicorn", "music_observatory.api:app", "--host", "0.0.0.0", "--port", "8765"]