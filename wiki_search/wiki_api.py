import asyncio
import hashlib
import pickle  # noqa S403
from typing import List, Optional

import httpx
from fastapi import Depends, Query
from starlette.background import BackgroundTasks

from wiki_search import config
from wiki_search import context as ctx
from wiki_search.schemas import (
    PageRevision,
    RequestType,
    SearchAPIResponse,
    SearchResponse,
    WikiPage,
    inject_timing,
)

__all__ = ('get_pages_with_revisions',)

QueryList = List[str]


def _filter_search_response(original_response):
    return [page['pageid'] for page in original_response['query']['search']]


@inject_timing(RequestType.HTTP)
async def _perform_search_request(query_string: str) -> SearchAPIResponse:
    """See https://www.mediawiki.org/wiki/API:Search."""
    query_params = {
        'action': 'query',
        'list': 'search',
        'srsearch': query_string,
        'format': 'json',
        'srlimit': config.PAGES_LIMIT,
    }
    async with httpx.AsyncClient() as client:
        wiki_response = await client.get(config.WIKIPEDIA_API_URI, params=query_params)
    page_ids = _filter_search_response(wiki_response.json())  # TODO handle errors
    return SearchAPIResponse(page_ids=page_ids)


@inject_timing(RequestType.REDIS)
async def _try_cached_search(query) -> Optional[SearchAPIResponse]:
    page_ids = await ctx.redis.get(query)
    if page_ids:
        try:
            return pickle.loads(page_ids)  # noqa S301
        except (pickle.UnpicklingError, AttributeError, EOFError, ImportError, IndexError):
            return None
    return None


async def get_page_ids(
    bg_tasks: BackgroundTasks, query: QueryList = Query(...),  # noqa WPS404
) -> SearchAPIResponse:
    """Return Wikipedia pages' IDs for given search query.

    Look for cached query in Redis, if lookup fails make a search
    request to Wikipedia API and enqueue the response caching.
    """
    query_string = ','.join(query)
    query_hash = hashlib.sha1(query_string.encode()).hexdigest()  # noqa S303

    page_ids = await _try_cached_search(query_hash)
    if page_ids:
        return page_ids

    page_ids = await _perform_search_request(query_string)

    bg_tasks.add_task(
        ctx.redis.set,
        query_hash,
        pickle.dumps(page_ids),
        expire=config.CACHE_TTL_IN_SECONDS,
    )
    return page_ids


def _filter_revisions_response(original_response, page_id: int):
    response = original_response['query']['pages'][str(page_id)]
    return {
        'title': response['title'],
        'revisions': [PageRevision(**revision) for revision in response['revisions']],
    }


@inject_timing(RequestType.HTTP)
async def _perform_revisions_request(page_id: int) -> WikiPage:
    """See https://www.mediawiki.org/wiki/API:Revisions."""
    query_params = {
        'action': 'query',
        'prop': 'revisions',
        'pageids': page_id,
        'format': 'json',
        'rvlimit': config.REVISIONS_LIMIT,
        'rvprop': 'timestamp|ids|comment',
    }
    async with httpx.AsyncClient() as client:
        wiki_response = await client.get(config.WIKIPEDIA_API_URI, params=query_params)
    page = _filter_revisions_response(wiki_response.json(), page_id)  # TODO handle errors
    return WikiPage(**page)


@inject_timing(RequestType.REDIS)
async def _try_cached_page(page_id) -> Optional[WikiPage]:
    page = await ctx.redis.get(page_id)
    if page:
        try:
            return pickle.loads(page)  # noqa S301
        except (pickle.UnpicklingError, AttributeError, EOFError, ImportError, IndexError):
            return None
    return None


async def get_revisions(page_id: int, bg_tasks: BackgroundTasks) -> WikiPage:
    """Return revisions data for a given page ID."""
    page = await _try_cached_page(page_id)
    if page:
        return page

    page = await _perform_revisions_request(page_id)

    bg_tasks.add_task(
        ctx.redis.set,
        page_id,
        pickle.dumps(page),
        expire=config.CACHE_TTL_IN_SECONDS,
    )
    return page


async def get_pages_with_revisions(
    bg_tasks: BackgroundTasks,
    search_api_response: SearchAPIResponse = Depends(get_page_ids),  # noqa WPS404
) -> SearchResponse:
    """Search pages matching given query and return their titles and latest revisions.

    Top-level FastAPI dependency, it's subdependency
    (see https://fastapi.tiangolo.com/tutorial/dependencies/sub-dependencies/)
    represented by `search_api_response` implements searching and returns results.
    Then, SearchResponse is aggregated from revisions fetched for every page.
    """
    revisions = await asyncio.gather(
        *(get_revisions(page_id, bg_tasks) for page_id in search_api_response.page_ids),
    )
    return SearchResponse(search_results=revisions, timing=search_api_response.timing)
