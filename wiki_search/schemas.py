import functools
from datetime import datetime, timedelta
from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Extra, Schema


class RequestType(str, Enum):
    HTTP = 'http'
    REDIS = 'redis'


class Timing(BaseModel):
    request_type: Optional[RequestType]
    request_time: timedelta


class TimingMixin(BaseModel):
    timing: Optional[Timing]


def inject_timing(request_type: Optional[RequestType]):
    def timed(func):  # noqa WPS430
        @functools.wraps(func)  # noqa WPS430
        async def wrapper(*args, **kwargs):
            time_start = datetime.now()
            func_result = await func(*args, **kwargs)
            time_end = datetime.now()
            delta = time_end - time_start
            if isinstance(func_result, TimingMixin):
                func_result.timing = Timing(request_type=request_type, request_time=delta)
            return func_result
        return wrapper
    return timed


class SearchQuery(BaseModel):
    query: List[str] = Schema(..., min_items=1)  # type: ignore


class PageRevision(BaseModel):
    class Config:  # noqa WPS431
        extra = Extra.ignore

    revision_id: int = Schema(..., alias='revid')  # type: ignore
    comment: str
    timestamp: datetime


class WikiPage(TimingMixin, BaseModel):
    title: str
    revisions: List[PageRevision]


class SearchResponse(TimingMixin, BaseModel):
    search_results: List[WikiPage]


class SearchAPIResponse(TimingMixin, BaseModel):
    page_ids: List[int]
