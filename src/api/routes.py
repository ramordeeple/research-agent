from fastapi import APIRouter, status

router = APIRouter(prefix="/api/v1", tags=["v1"])

@router.get("/health")
async def health() -> dict[str, int]:
    return {"status": status.HTTP_200_OK}