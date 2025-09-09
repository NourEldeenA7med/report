# Deploying Streamlit + pyodbc to Railway

## Files
- `Dockerfile`: builds a Debian-based image, installs MS ODBC Driver 18, and runs Streamlit on `$PORT`.
- `requirements.txt`: Python dependencies.
- `.streamlit/config.toml`: ensures Streamlit binds to `0.0.0.0:8080` (Railway sets `$PORT`).
- Your existing `app.py` should be at repo root.

## Railway steps
1. Create a new project → **Deploy from GitHub** (recommended) or **Deploy from Repo Template/Empty**.
2. Push these files along with your `app.py` to a GitHub repo.
3. In Railway → Variables:
   - `SQL_DRIVER=ODBC Driver 18 for SQL Server`
   - `SQL_SERVER=...`
   - `SQL_DATABASE=...`
   - `SQL_USER=...`
   - `SQL_PWD=...`
4. Deploy. Logs should show `Running on network URL: http://0.0.0.0:<PORT>`.
