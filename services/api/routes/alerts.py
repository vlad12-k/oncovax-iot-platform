from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, HTTPException, Query, Request

from services.api.models import AcknowledgeRequest

router = APIRouter()


def _get_collection(request: Request):
    return request.app.state.collection


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@router.get("/alerts")
def list_alerts(
    request: Request,
    limit: int = Query(default=20, ge=1, le=200),
    acknowledged: Optional[bool] = Query(default=None),
):
    collection = _get_collection(request)
    query: dict = {}
    if acknowledged is not None:
        query["acknowledged"] = acknowledged

    docs = list(
        collection.find(query, {"_id": 0})
        .sort("time", -1)
        .limit(limit)
    )
    return {"count": len(docs), "items": docs}


@router.get("/alerts/{alert_id}")
def get_alert(alert_id: str, request: Request):
    collection = _get_collection(request)
    doc = collection.find_one({"alert_id": alert_id}, {"_id": 0})
    if not doc:
        raise HTTPException(status_code=404, detail="Alert not found")
    return doc


@router.get("/summary")
def alert_summary(request: Request):
    collection = _get_collection(request)
    total = collection.count_documents({})
    acknowledged = collection.count_documents({"acknowledged": True})
    unacknowledged = collection.count_documents({"acknowledged": False})

    return {
        "total_alerts": total,
        "acknowledged_alerts": acknowledged,
        "unacknowledged_alerts": unacknowledged,
    }


@router.post("/alerts/{alert_id}/acknowledge")
def acknowledge_alert(alert_id: str, body: AcknowledgeRequest, request: Request):
    collection = _get_collection(request)

    update_fields: dict = {
        "acknowledged": True,
        "acknowledged_by": body.acknowledged_by,
        "acknowledged_at": _now_iso(),
    }
    if body.incident_note is not None:
        update_fields["incident_note"] = body.incident_note

    result = collection.update_one(
        {"alert_id": alert_id},
        {"$set": update_fields},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Alert not found")

    updated = collection.find_one({"alert_id": alert_id}, {"_id": 0})
    return {"message": "Alert acknowledged", "item": updated}
