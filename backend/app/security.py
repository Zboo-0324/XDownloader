import re
from urllib.parse import urlparse, urlunparse

from app.errors import ExtractorError


_ALLOWED_HOSTS = {
    "x.com",
    "www.x.com",
    "twitter.com",
    "www.twitter.com",
    "mobile.twitter.com",
}
_USER_STATUS_RE = re.compile(r"^/([^/]+)/status(?:es)?/(\d+)(?:/.*)?$")
_I_STATUS_RE = re.compile(r"^/i/status/(\d+)(?:/.*)?$")
_WEB_STATUS_RE = re.compile(r"^/i/web/status/(\d+)(?:/.*)?$")


def validate_tweet_url(raw_url: str) -> str:
    """Validate and normalize a public X/Twitter status URL."""

    try:
        parsed = urlparse(raw_url.strip())
    except ValueError as exc:
        raise _invalid_url() from exc

    host = (parsed.hostname or "").lower()
    if parsed.scheme not in {"http", "https"} or host not in _ALLOWED_HOSTS:
        raise _invalid_url()

    path = parsed.path.rstrip("/")
    i_status_match = _I_STATUS_RE.match(path)
    user_match = _USER_STATUS_RE.match(path)
    web_match = _WEB_STATUS_RE.match(path)

    if i_status_match:
        (status_id,) = i_status_match.groups()
        normalized_path = f"/i/web/status/{status_id}"
    elif user_match:
        username, status_id = user_match.groups()
        normalized_path = f"/{username}/status/{status_id}"
    elif web_match:
        (status_id,) = web_match.groups()
        normalized_path = f"/i/web/status/{status_id}"
    else:
        raise _invalid_url()

    return urlunparse(("https", host, normalized_path, "", "", ""))


def _invalid_url() -> ExtractorError:
    return ExtractorError(
        "INVALID_URL",
        "请输入公开的 X/Twitter 帖子链接。",
        status_code=400,
    )
