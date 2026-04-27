from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.errors import ExtractorError
from app.extractor import extract_media
from app.schemas import ErrorResponse, ExtractRequest, ExtractResponse


app = FastAPI(title="XDownloader API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=False,
    allow_methods=["POST", "GET", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/api/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post(
    "/api/extract",
    response_model=ExtractResponse,
    responses={
        400: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        502: {"model": ErrorResponse},
        504: {"model": ErrorResponse},
    },
)
async def extract(payload: ExtractRequest) -> ExtractResponse | JSONResponse:
    try:
        return await extract_media(payload.url)
    except ExtractorError as exc:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": {"code": exc.code, "message": exc.message}},
        )
