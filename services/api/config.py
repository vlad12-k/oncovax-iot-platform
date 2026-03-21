import os

MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB: str = os.getenv("MONGO_DB", "oncovax")
MONGO_COLLECTION: str = os.getenv("MONGO_COLLECTION", "audit_events")

# CORS allowed origins.
# The dashboard is served by the same FastAPI process, so same-origin requests
# do not need CORS at all.  This setting only matters when the API is accessed
# from a different origin (e.g. a separately hosted frontend or curl during dev).
#
# Set CORS_ALLOWED_ORIGINS in the environment as a comma-separated list, e.g.:
#   CORS_ALLOWED_ORIGINS=https://your-domain.example.com,http://localhost:3000
#
# Defaults to an empty list, which means only same-origin requests are allowed
# (the wildcard "*" is intentionally NOT used as a default).
_raw_cors: str = os.getenv("CORS_ALLOWED_ORIGINS", "")
CORS_ALLOWED_ORIGINS: list[str] = [o.strip() for o in _raw_cors.split(",") if o.strip()]
