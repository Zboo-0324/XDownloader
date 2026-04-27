from typing import Literal

from pydantic import BaseModel, Field


class ExtractRequest(BaseModel):
    url: str = Field(..., min_length=1)


class MediaItem(BaseModel):
    type: Literal["video", "gif", "image"]
    url: str
    quality: str
    ext: str | None = None
    width: int | None = None
    height: int | None = None
    filesize: int | None = None


class ExtractResponse(BaseModel):
    title: str | None = None
    author: str | None = None
    thumbnail: str | None = None
    source_url: str
    items: list[MediaItem]


class ErrorBody(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    error: ErrorBody
