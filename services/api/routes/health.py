from fastapi import APIRouter, Response

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/public-health")
def public_health():
    return {"status": "ok"}


@router.head("/public-health")
def public_health_head():
    return Response(status_code=200)
