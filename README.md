# SuperKart Sales Forecasting – Containerized Deployment

| Component | Folder | Port | Technology |
|-----------|--------|------|------------|
| Backend API | `backend_files/` | 7860 | Flask + Gunicorn, XGBoost pipeline |
| Frontend UI | `frontend_files/` | 8501 | Streamlit |

## Run in a GitHub Codespace
1. Open this repository → **Code** → **Codespaces** → **Create codespace on main**.
2. In the terminal: `bash run_containers.sh`
3. Open the **PORTS** tab and set ports **7860** and **8501** to **Public**.
4. Open the forwarded 8501 URL for the app; use the 7860 URL for direct API calls.

## API
- `GET /` – health check
- `POST /v1/predict` – JSON body with the 10 model features
- `POST /v1/predictbatch` – multipart upload, form field `file` (CSV)
