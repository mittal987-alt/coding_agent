from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
@router.get("/health/ready")
@router.get("/health/live")
@router.get("/health/startup")
async def health():
    return {
        "status": "ok",
        "message": "Backend Running"
    }