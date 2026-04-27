import asyncio

import pytest

from app.errors import ExtractorError
from app.extractor import extract_media, normalize_info


def test_normalize_info_returns_sorted_video_formats():
    info = {
        "title": "A demo post",
        "uploader": "alice",
        "thumbnail": "https://pbs.twimg.com/thumb.jpg",
        "webpage_url": "https://x.com/alice/status/1",
        "formats": [
            {
                "url": "https://video.twimg.com/low.mp4",
                "ext": "mp4",
                "height": 360,
                "width": 640,
                "tbr": 800,
                "filesize": 100,
                "vcodec": "avc1",
            },
            {
                "url": "https://video.twimg.com/high.mp4",
                "ext": "mp4",
                "height": 720,
                "width": 1280,
                "tbr": 1800,
                "filesize": 300,
                "vcodec": "avc1",
            },
            {
                "url": "https://video.twimg.com/audio.m4a",
                "ext": "m4a",
                "vcodec": "none",
                "acodec": "mp4a",
            },
        ],
    }

    result = normalize_info(info, "https://x.com/alice/status/1")

    assert result.title == "A demo post"
    assert result.author == "alice"
    assert [item.quality for item in result.items] == ["720p", "360p"]
    assert [item.url for item in result.items] == [
        "https://video.twimg.com/high.mp4",
        "https://video.twimg.com/low.mp4",
    ]


def test_normalize_info_returns_images_from_entries():
    info = {
        "title": "Photos",
        "entries": [
            {
                "title": "Photo 1",
                "images": [
                    {
                        "url": "https://pbs.twimg.com/media/a.jpg?format=jpg&name=orig",
                        "width": 1200,
                        "height": 900,
                        "ext": "jpg",
                    }
                ],
            },
            {
                "title": "Photo 2",
                "url": "https://pbs.twimg.com/media/b.png?format=png&name=orig",
                "ext": "png",
                "width": 800,
                "height": 600,
            },
        ],
    }

    result = normalize_info(info, "https://x.com/alice/status/2")

    assert [item.type for item in result.items] == ["image", "image"]
    assert [item.quality for item in result.items] == ["原图", "原图"]
    assert result.items[0].url.endswith("name=orig")


def test_normalize_info_uses_thumbnails_as_image_fallback_when_no_formats_exist():
    info = {
        "title": "Photo",
        "thumbnails": [
            {
                "url": "https://pbs.twimg.com/media/photo.jpg?format=jpg&name=small",
                "width": 680,
                "height": 510,
                "ext": "jpg",
            },
            {
                "url": "https://pbs.twimg.com/media/photo.jpg?format=jpg&name=orig",
                "width": 2048,
                "height": 1536,
                "ext": "jpg",
            },
        ],
    }

    result = normalize_info(info, "https://x.com/alice/status/7")

    assert result.items[0].type == "image"
    assert result.items[0].url.endswith("name=orig")


def test_normalize_info_raises_no_media_when_nothing_downloadable_exists():
    with pytest.raises(ExtractorError) as exc_info:
        normalize_info({"title": "No media"}, "https://x.com/alice/status/3")

    assert exc_info.value.code == "NO_MEDIA"
    assert exc_info.value.message == "没有找到可下载的媒体。"


@pytest.mark.asyncio
async def test_extract_media_maps_timeout_to_structured_error():
    def slow_extract(_url):
        import time

        time.sleep(0.2)
        return {}

    with pytest.raises(ExtractorError) as exc_info:
        await extract_media(
            "https://x.com/alice/status/4",
            timeout_seconds=0.01,
            extract_info=slow_extract,
        )

    assert exc_info.value.code == "TIMEOUT"
    assert exc_info.value.message == "解析超时，请稍后重试。"


@pytest.mark.asyncio
async def test_extract_media_maps_login_errors_to_structured_error():
    def login_required(_url):
        raise RuntimeError("This tweet is protected and requires authentication")

    with pytest.raises(ExtractorError) as exc_info:
        await extract_media(
            "https://x.com/alice/status/5",
            extract_info=login_required,
        )

    assert exc_info.value.code == "LOGIN_REQUIRED"
    assert exc_info.value.message == "该帖子可能是私密、受保护或需要登录，当前版本无法解析。"


@pytest.mark.asyncio
async def test_extract_media_maps_unknown_errors_to_structured_error():
    def broken(_url):
        raise RuntimeError("upstream changed")

    with pytest.raises(ExtractorError) as exc_info:
        await extract_media(
            "https://x.com/alice/status/6",
            extract_info=broken,
        )

    assert exc_info.value.code == "EXTRACT_FAILED"
    assert exc_info.value.message == "解析失败，请确认链接有效或稍后重试。"
