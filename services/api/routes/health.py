from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/public-health")
def public_health():
    return {"status": "ok"}
