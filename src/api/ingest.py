import logging

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from src.schemas.ingest import IngestResponse
from src.services.ingest_service import process_upload

logger = logging.getLogger(__name__)

router = APIRouter(tags=["ingest"])


@router.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile = File(...)) -> IngestResponse:
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename is required",
        )

    try:
        chunks_indexed = process_upload(file.filename, file.file)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e

    return IngestResponse(
        filename=file.filename,
        chunks_indexed=chunks_indexed,
    )