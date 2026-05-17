FROM python:3.13-slim

WORKDIR /app

# Install Python dependencies (PyMySQL is pure Python — no system deps needed)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY frontend/ ./frontend/
COPY run.py .

EXPOSE 8000

CMD ["python", "run.py"]