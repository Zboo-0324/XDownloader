from fastapi.testclient import TestClient

from app.errors import ExtractorError
from app.main import app, build_cors_origins
from app.schemas import ExtractResponse, MediaItem


def test_build_cors_origins_includes_configured_deployments(monkeypatch):
    monkeypatch.setenv(
        "XDOWNLOADER_CORS_ORIGINS",
        "https://xdownloader.example, https://preview.example/",
    )

    assert build_cors_origins() == [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://xdownloader.example",
        "https://preview.example",
    ]


def test_extract_endpoint_returns_media(monkeypatch):
    async def fake_extract(url: str):
        return ExtractResponse(
            title="Demo",
            author="alice",
            thumbnail=None,
            source_url=url,
            items=[
                MediaItem(
                    type="video",
                    url="https://video.twimg.com/demo.mp4",
                    quality="720p",
                    ext="mp4",
                    width=1280,
                    height=720,
                    filesize=None,
                )
            ],
        )

    monkeypatch.setattr("app.main.extract_media", fake_extract)
    client = TestClient(app)

    response = client.post("/api/extract", json={"url": "https://x.com/alice/status/1"})

    assert response.status_code == 200
    assert response.json()["items"][0]["quality"] == "720p"


def test_extract_endpoint_returns_structured_errors(monkeypatch):
    async def fake_extract(_url: str):
        raise ExtractorError("NO_MEDIA", "没有找到可下载的媒体。", status_code=404)

    monkeypatch.setattr("app.main.extract_media", fake_extract)
    client = TestClient(app)

    response = client.post("/api/extract", json={"url": "https://x.com/alice/status/1"})

    assert response.status_code == 404
    assert response.json() == {
        "error": {"code": "NO_MEDIA", "message": "没有找到可下载的媒体。"}
    }
