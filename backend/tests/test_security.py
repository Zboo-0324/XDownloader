import pytest

from app.errors import ExtractorError
from app.security import validate_tweet_url


def test_validate_tweet_url_accepts_x_status_url_and_strips_tracking_query():
    result = validate_tweet_url("https://x.com/example/status/1234567890?s=20#ignored")

    assert result == "https://x.com/example/status/1234567890"


def test_validate_tweet_url_accepts_twitter_status_url():
    result = validate_tweet_url("https://twitter.com/example/status/1234567890")

    assert result == "https://twitter.com/example/status/1234567890"


@pytest.mark.parametrize(
    "url",
    [
        "https://example.com/example/status/1234567890",
        "https://x.com/example",
        "javascript:alert(1)",
        "not a url",
    ],
)
def test_validate_tweet_url_rejects_non_public_status_urls(url):
    with pytest.raises(ExtractorError) as exc_info:
        validate_tweet_url(url)

    assert exc_info.value.code == "INVALID_URL"
    assert exc_info.value.message == "请输入公开的 X/Twitter 帖子链接。"
