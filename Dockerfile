\
# ---- Base Python image ----
FROM python:3.11-slim

# ---- System deps for MS ODBC + build tools ----
ENV ACCEPT_EULA=Y
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        curl gnupg apt-transport-https unixodbc unixodbc-dev build-essential && \
    curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - && \
    curl https://packages.microsoft.com/config/debian/12/prod.list > /etc/apt/sources.list.d/microsoft-prod.list && \
    apt-get update && \
    # MS SQL ODBC Driver 18
    apt-get install -y --no-install-recommends msodbcsql18 && \
    # Cleanup
    rm -rf /var/lib/apt/lists/*

# ---- App dir ----
WORKDIR /app

# ---- Python deps ----
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# ---- Copy app ----
COPY . .

# ---- Streamlit config ----
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

# Streamlit needs to listen on 0.0.0.0 and Railway's $PORT
CMD ["bash", "-lc", "streamlit run app.py --server.address 0.0.0.0 --server.port ${PORT}"]
