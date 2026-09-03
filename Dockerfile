FROM python:3.12-slim

WORKDIR /app

# atkarības
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# lietotnes kods + statika
COPY app.py .
COPY static ./static

# persistent volume punkts (Coolify montē šeit)
VOLUME ["/data"]

ENV DATA_DIR=/data
EXPOSE 8000

# uvicorn palaiž FastAPI
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
