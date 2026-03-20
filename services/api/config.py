import os


MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB: str = os.getenv("MONGO_DB", "oncovax")
MONGO_COLLECTION: str = os.getenv("MONGO_COLLECTION", "audit_events")
