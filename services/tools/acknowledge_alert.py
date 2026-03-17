import os
import sys
from datetime import datetime, timezone
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "oncovax")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "audit_events")


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def main():
    if len(sys.argv) < 3:
        print("Usage: python services/tools/acknowledge_alert.py <alert_id> <acknowledged_by> [incident_note]")
        sys.exit(1)

    alert_id = sys.argv[1]
    acknowledged_by = sys.argv[2]
    incident_note = sys.argv[3] if len(sys.argv) > 3 else None

    client = MongoClient(MONGO_URI)
    collection = client[MONGO_DB][MONGO_COLLECTION]

    update_doc = {
        "$set": {
            "acknowledged": True,
            "acknowledged_by": acknowledged_by,
            "acknowledged_at": now_iso(),
        }
    }

    if incident_note:
        update_doc["$set"]["incident_note"] = incident_note

    result = collection.update_one({"alert_id": alert_id}, update_doc)

    if result.matched_count == 0:
        print(f"[ack] no alert found for alert_id={alert_id}")
        sys.exit(1)

    print(f"[ack] updated alert_id={alert_id}")
    updated = collection.find_one({"alert_id": alert_id}, {"_id": 0})
    print(updated)


if __name__ == "__main__":
    main()
