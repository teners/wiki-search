import aioredis
import uvicorn
from fastapi import Depends, FastAPI
from starlette.requests import Request
from starlette.responses import HTMLResponse

from wiki_search import config
from wiki_search import context as ctx
from wiki_search import templates
from wiki_search.schemas import SearchResponse
from wiki_search.wiki_api import get_pages_with_revisions

app = FastAPI(title='wiki-search')


@app.on_event('startup')
async def init_redis_pool():
    ctx.redis = await aioredis.create_redis_pool(config.REDIS_URI)


@app.on_event('shutdown')
async def close_redis_pool():
    ctx.redis.close()
    await ctx.redis.wait_closed()


@app.get('/api/json/search/', response_model=SearchResponse)
async def search_wiki(wikipages: SearchResponse = Depends(get_pages_with_revisions)):  # noqa WPS404
    """Search Wikipedia.

    Return top 5 pages for a given query, 10 latest revisions
    for each page and requests benchmark.
    """
    return wikipages.dict(by_alias=True)


@app.get('/api/html/search/', response_class=HTMLResponse)
async def search_html(
    request: Request, response: SearchResponse = Depends(get_pages_with_revisions),  # noqa WPS404
):
    """Search Wikipedia.

    Return top 5 pages for a given query, 10 latest revisions
    for each page and requests benchmark.
    """
    queries_list = [query for query in request.query_params.getlist('query')]
    response_dict = response.dict()

    return templates.search_result_template.render(
        wikipages=response_dict['search_results'],
        timing=response_dict['timing'],
        queries=queries_list,
        wikipedia_url=config.WIKIPEDIA_URL,
    )


if __name__ == '__main__':
    uvicorn.run(app)
