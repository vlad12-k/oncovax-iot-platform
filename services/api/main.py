"""
OncoVax FastAPI service – entry point.

Routes are organised in:
  services/api/routes/alerts.py  – alert retrieval and acknowledgement
  services/api/routes/health.py  – health check
"""

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient

from services.api.config import MONGO_URI, MONGO_DB, MONGO_COLLECTION
from services.api.routes.alerts import router as alerts_router
from services.api.routes.health import router as health_router

BASE_DIR = Path(__file__).resolve().parents[2]
WEB_DIR = BASE_DIR / "services" / "web"

app = FastAPI(title="OncoVax API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

mongo_client = MongoClient(MONGO_URI)
collection = mongo_client[MONGO_DB][MONGO_COLLECTION]

# Inject the collection into the routers via app state
app.state.collection = collection

app.include_router(health_router)
app.include_router(alerts_router)


@app.get("/")
def dashboard():
    return FileResponse(WEB_DIR / "index.html")


app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")
