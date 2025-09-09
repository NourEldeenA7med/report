# Use Debian 12 (bookworm) so the MS repo matches
FROM python:3.11-slim-bookworm

ENV ACCEPT_EULA=Y \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Install deps + add Microsoft repo WITHOUT apt-key
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl ca-certificates gnupg2 apt-transport-https \
        unixodbc unixodbc-dev build-essential && \
    mkdir -p /usr/share/keyrings && \
    curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
      | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg && \
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
      > /etc/apt/sources.list.d/microsoft-prod.list && \
    apt-get update && \
    apt-get install -y --no-install-recommends msodbcsql18 && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Streamlit must bind to 0.0.0.0:$PORT on hosts like Railway/Render/Fly/Cloud Run
CMD ["bash", "-lc", "streamlit run app.py --server.address 0.0.0.0 --server.port ${PORT}"]
