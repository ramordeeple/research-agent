from fastapi import APIRouter, status

from src.core.constants import API_V1_PREFIX

router = APIRouter(prefix=API_V1_PREFIX, tags=["v1"])

@router.get("/health")
async def health() -> dict[str, int]:
    return {"status": status.HTTP_200_OK}