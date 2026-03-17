import os
from datetime import datetime, timezone
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "oncovax")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "audit_events")

app = FastAPI(title="OncoVax API", version="0.1.0")

mongo_client = MongoClient(MONGO_URI)
collection = mongo_client[MONGO_DB][MONGO_COLLECTION]


def now_iso():
    return datetime.now(timezone.utc).isoformat()


class AcknowledgeRequest(BaseModel):
    acknowledged_by: str
    incident_note: Optional[str] = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/alerts")
def list_alerts(limit: int = 20):
    docs = list(
        collection.find({}, {"_id": 0})
        .sort("time", -1)
        .limit(limit)
    )
    return {"count": len(docs), "items": docs}


@app.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: str, body: AcknowledgeRequest):
    update_doc = {
        "$set": {
            "acknowledged": True,
            "acknowledged_by": body.acknowledged_by,
            "acknowledged_at": now_iso(),
        }
    }

    if body.incident_note is not None:
        update_doc["$set"]["incident_note"] = body.incident_note

    result = collection.update_one({"alert_id": alert_id}, update_doc)

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")

    updated = collection.find_one({"alert_id": alert_id}, {"_id": 0})
    return {"message": "Alert acknowledged", "item": updated}
