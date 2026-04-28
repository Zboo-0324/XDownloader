import asyncio
import base64
import binascii
import hashlib
import json
import logging
import math
import os
import tempfile
import urllib.error
import urllib.request
from collections.abc import Callable, Iterable
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

from app.errors import ExtractorError
from app.schemas import ExtractResponse, MediaItem
from app.security import validate_tweet_url


ExtractInfoFn = Callable[[str], dict[str, Any]]

_IMAGE_EXTENSIONS = {"jpg", "jpeg", "png", "webp", "gif"}
_VIDEO_EXTENSIONS = {"mp4", "mov", "m4v", "webm"}
_X_COOKIES_ENV = "XDOWNLOADER_X_COOKIES_B64"
_NO_MEDIA_MESSAGE = "没有找到可下载的媒体。帖子可能没有公开视频或图片，或已删除、受限、需要登录。"
logger = logging.getLogger(__name__)


async def extract_media(
    url: str,
    timeout_seconds: float = 30.0,
    extract_info: ExtractInfoFn | None = None,
) -> ExtractResponse:
    normalized_url = validate_tweet_url(url)
    extractor = extract_info or _extract_info_with_ytdlp

    try:
        info = await asyncio.wait_for(
            asyncio.to_thread(extractor, normalized_url),
            timeout=timeout_seconds,
        )
    except TimeoutError as exc:
        raise ExtractorError(
            "TIMEOUT",
            "解析超时，请稍后重试。",
            status_code=504,
        ) from exc
    except ExtractorError:
        raise
    except Exception as exc:
        if _looks_like_login_required(exc):
            logger.exception("Failed to extract media from %s", normalized_url)
            raise ExtractorError(
                "LOGIN_REQUIRED",
                "该帖子可能是私密、受保护或需要登录，当前版本无法解析。",
                status_code=403,
            ) from exc
        if _looks_like_no_video_found(exc):
            fallback_info = await asyncio.to_thread(_extract_syndication_info, normalized_url)
            if fallback_info:
                try:
                    return normalize_info(fallback_info, normalized_url)
                except ExtractorError:
                    pass
            raise ExtractorError("NO_MEDIA", _NO_MEDIA_MESSAGE, status_code=404) from exc

        logger.exception("Failed to extract media from %s", normalized_url)
        raise ExtractorError(
            "EXTRACT_FAILED",
            "解析失败，请确认链接有效或稍后重试。",
            status_code=502,
        ) from exc

    return normalize_info(info, normalized_url)


def normalize_info(info: dict[str, Any], source_url: str) -> ExtractResponse:
    entries = list(_iter_entries(info))
    items: list[MediaItem] = []

    for entry in entries:
        video_items = _video_items_from_entry(entry)
        items.extend(video_items)
        if not video_items:
            items.extend(_image_items_from_entry(entry))

    items = _dedupe_items(items)
    videos = [item for item in items if item.type in {"video", "gif"}]
    images = [item for item in items if item.type == "image"]
    videos.sort(key=_video_sort_key, reverse=True)

    ordered_items = videos + images
    if not ordered_items:
        raise ExtractorError(
            "NO_MEDIA",
            "没有找到可下载的媒体。",
            status_code=404,
        )

    return ExtractResponse(
        title=_first_text(info, "title", "fulltitle", "description"),
        author=_first_text(info, "uploader", "uploader_id", "channel", "creator"),
        thumbnail=_first_text(info, "thumbnail"),
        source_url=source_url,
        items=ordered_items,
    )


def _extract_info_with_ytdlp(url: str) -> dict[str, Any]:
    from yt_dlp import YoutubeDL

    options = {
        "quiet": True,
        "no_warnings": True,
        "skip_download": True,
        "noplaylist": True,
        "socket_timeout": 25,
    }
    cookiefile = _cookiefile_from_env()
    if cookiefile:
        options["cookiefile"] = cookiefile

    with YoutubeDL(options) as ydl:
        return ydl.extract_info(url, download=False)


def _cookiefile_from_env() -> str | None:
    encoded = os.getenv(_X_COOKIES_ENV)
    if not encoded:
        return None

    normalized = "".join(encoded.split())
    try:
        cookie_bytes = base64.b64decode(normalized, validate=True)
    except (binascii.Error, ValueError):
        logger.warning("%s is not valid base64; continuing without X cookies", _X_COOKIES_ENV)
        return None

    if not cookie_bytes.strip():
        return None

    digest = hashlib.sha256(cookie_bytes).hexdigest()[:16]
    cookie_path = Path(tempfile.gettempdir()) / f"xdownloader-x-cookies-{digest}.txt"
    try:
        if not cookie_path.exists() or cookie_path.read_bytes() != cookie_bytes:
            cookie_path.write_bytes(cookie_bytes)
            try:
                cookie_path.chmod(0o600)
            except OSError:
                pass
    except OSError:
        logger.exception("Failed to prepare X cookies file")
        return None

    return str(cookie_path)


def _extract_syndication_info(url: str) -> dict[str, Any] | None:
    status_id = _status_id_from_url(url)
    if not status_id:
        return None

    token = _generate_syndication_token(status_id)
    request = urllib.request.Request(
        f"https://cdn.syndication.twimg.com/tweet-result?{urlencode({'id': status_id, 'token': token})}",
        headers={"User-Agent": "Googlebot"},
    )
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (OSError, urllib.error.URLError, json.JSONDecodeError):
        logger.exception("Failed to load syndication fallback for %s", url)
        return None

    if not isinstance(payload, dict):
        return None
    return _syndication_info_from_payload(payload)


def _syndication_info_from_payload(payload: dict[str, Any]) -> dict[str, Any] | None:
    entries: list[dict[str, Any]] = []
    for tweet in (payload, payload.get("quoted_tweet")):
        if not isinstance(tweet, dict):
            continue

        media_details = tweet.get("mediaDetails")
        if not isinstance(media_details, list):
            continue

        for media in media_details:
            if not isinstance(media, dict) or media.get("type") != "photo":
                continue

            image_url = media.get("media_url_https") or media.get("media_url")
            if not isinstance(image_url, str) or not image_url:
                continue

            original_info = (
                media.get("original_info") if isinstance(media.get("original_info"), dict) else {}
            )
            entries.append(
                {
                    "images": [
                        {
                            "url": _with_image_quality(image_url, "orig"),
                            "width": _int_or_none(original_info.get("width") or original_info.get("w")),
                            "height": _int_or_none(original_info.get("height") or original_info.get("h")),
                            "ext": _extension({"url": image_url}),
                        }
                    ]
                }
            )

    if not entries:
        return None

    user = payload.get("user") if isinstance(payload.get("user"), dict) else {}
    return {
        "title": _first_text(payload, "text", "full_text"),
        "uploader": _first_text(user, "name", "screen_name"),
        "thumbnail": entries[0]["images"][0]["url"],
        "entries": entries,
    }


def _generate_syndication_token(status_id: str) -> str:
    from yt_dlp.jsinterp import js_number_to_string

    translation = str.maketrans(dict.fromkeys("0."))
    return js_number_to_string((int(status_id) / 1e15) * math.pi, 36).translate(translation)


def _iter_entries(info: dict[str, Any]) -> Iterable[dict[str, Any]]:
    entries = info.get("entries")
    if isinstance(entries, list) and entries:
        for entry in entries:
            if isinstance(entry, dict):
                yield entry
        return
    yield info


def _video_items_from_entry(entry: dict[str, Any]) -> list[MediaItem]:
    formats = entry.get("formats")
    if not isinstance(formats, list):
        return []

    items: list[MediaItem] = []
    video_formats = [
        media_format
        for media_format in formats
        if isinstance(media_format, dict) and _is_direct_video_format(media_format)
    ]
    video_formats.sort(key=_format_sort_key, reverse=True)

    for media_format in video_formats:
        items.append(
            MediaItem(
                type=_video_type(entry, media_format),
                url=str(media_format["url"]),
                quality=_quality_label(media_format),
                ext=_extension(media_format),
                width=_int_or_none(media_format.get("width")),
                height=_int_or_none(media_format.get("height")),
                filesize=_int_or_none(
                    media_format.get("filesize")
                    or media_format.get("filesize_approx")
                ),
            )
        )
    return items


def _image_items_from_entry(entry: dict[str, Any]) -> list[MediaItem]:
    candidates: list[dict[str, Any]] = []

    images = entry.get("images")
    if isinstance(images, list):
        for image in images:
            if isinstance(image, str):
                candidates.append({"url": image})
            elif isinstance(image, dict):
                candidates.append(image)

    if _looks_like_image_url(entry.get("url"), entry.get("ext")):
        candidates.append(entry)

    if not candidates:
        thumbnails = entry.get("thumbnails")
        if isinstance(thumbnails, list):
            candidates.extend(_sorted_image_thumbnails(thumbnails))

    items: list[MediaItem] = []
    for candidate in candidates:
        image_url = candidate.get("url")
        if not isinstance(image_url, str) or not image_url:
            continue
        items.append(
            MediaItem(
                type="image",
                url=image_url,
                quality="原图",
                ext=_extension(candidate),
                width=_int_or_none(candidate.get("width")),
                height=_int_or_none(candidate.get("height")),
                filesize=_int_or_none(
                    candidate.get("filesize") or candidate.get("filesize_approx")
                ),
            )
        )
    return items


def _is_direct_video_format(media_format: dict[str, Any]) -> bool:
    media_url = media_format.get("url")
    if not isinstance(media_url, str) or not media_url:
        return False

    ext = _extension(media_format)
    protocol = str(media_format.get("protocol") or "").lower()
    if ext not in _VIDEO_EXTENSIONS:
        return False
    if "m3u8" in protocol or "dash" in protocol:
        return False
    return media_format.get("vcodec") != "none"


def _video_type(entry: dict[str, Any], media_format: dict[str, Any]) -> str:
    signals = [
        entry.get("media_type"),
        entry.get("type"),
        entry.get("format"),
        media_format.get("format_note"),
    ]
    if any("gif" in str(signal).lower() for signal in signals if signal):
        return "gif"
    return "video"


def _quality_label(media_format: dict[str, Any]) -> str:
    height = _int_or_none(media_format.get("height"))
    if height:
        return f"{height}p"

    width = _int_or_none(media_format.get("width"))
    if width:
        return f"{width}px"

    for key in ("format_note", "resolution", "format_id"):
        value = media_format.get(key)
        if value:
            return str(value)

    return "原始"


def _dedupe_items(items: list[MediaItem]) -> list[MediaItem]:
    seen: set[str] = set()
    result: list[MediaItem] = []
    for item in items:
        if item.url in seen:
            continue
        seen.add(item.url)
        result.append(item)
    return result


def _sorted_image_thumbnails(thumbnails: list[Any]) -> list[dict[str, Any]]:
    image_thumbnails = [
        thumbnail
        for thumbnail in thumbnails
        if isinstance(thumbnail, dict)
        and _looks_like_image_url(thumbnail.get("url"), thumbnail.get("ext"))
    ]
    return sorted(
        image_thumbnails,
        key=lambda thumbnail: (
            _int_or_none(thumbnail.get("width")) or 0,
            _int_or_none(thumbnail.get("height")) or 0,
        ),
        reverse=True,
    )


def _video_sort_key(item: MediaItem) -> tuple[int, int]:
    return (item.height or 0, item.filesize or 0)


def _format_sort_key(media_format: dict[str, Any]) -> tuple[int, int, int]:
    return (
        _int_or_none(media_format.get("height")) or 0,
        _int_or_none(media_format.get("tbr")) or 0,
        _int_or_none(media_format.get("filesize") or media_format.get("filesize_approx"))
        or 0,
    )


def _looks_like_image_url(value: Any, ext: Any = None) -> bool:
    if not isinstance(value, str) or not value:
        return False
    if _normalize_ext(ext) in _IMAGE_EXTENSIONS:
        return True

    parsed = urlparse(value)
    query_format = parse_qs(parsed.query).get("format", [None])[0]
    if _normalize_ext(query_format) in _IMAGE_EXTENSIONS:
        return True

    suffix = parsed.path.rsplit(".", 1)[-1] if "." in parsed.path else ""
    return _normalize_ext(suffix) in _IMAGE_EXTENSIONS


def _extension(data: dict[str, Any]) -> str | None:
    ext = _normalize_ext(data.get("ext"))
    if ext:
        return ext

    url = data.get("url")
    if not isinstance(url, str):
        return None

    parsed = urlparse(url)
    query_format = parse_qs(parsed.query).get("format", [None])[0]
    ext = _normalize_ext(query_format)
    if ext:
        return ext

    if "." not in parsed.path:
        return None
    return _normalize_ext(parsed.path.rsplit(".", 1)[-1])


def _normalize_ext(value: Any) -> str | None:
    if not value:
        return None
    return str(value).lower().lstrip(".")


def _first_text(data: dict[str, Any], *keys: str) -> str | None:
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value:
            return value
    return None


def _int_or_none(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _status_id_from_url(url: str) -> str | None:
    path_parts = [part for part in urlparse(url).path.split("/") if part]
    if len(path_parts) >= 3 and path_parts[-2] == "status" and path_parts[-1].isdigit():
        return path_parts[-1]
    if len(path_parts) >= 4 and path_parts[-3:] == ["web", "status", path_parts[-1]] and path_parts[-1].isdigit():
        return path_parts[-1]
    return None


def _with_image_quality(url: str, quality: str) -> str:
    parsed = urlparse(url)
    query = dict(parse_qs(parsed.query, keep_blank_values=True))
    query["name"] = [quality]
    return urlunparse(
        (
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            urlencode(query, doseq=True),
            parsed.fragment,
        )
    )


def _looks_like_no_video_found(exc: Exception) -> bool:
    return "no video could be found in this tweet" in str(exc).lower()


def _looks_like_login_required(exc: Exception) -> bool:
    message = str(exc).lower()
    return any(
        signal in message
        for signal in (
            "login",
            "authenticate",
            "authentication",
            "protected",
            "private",
            "not authorized",
            "forbidden",
        )
    )
