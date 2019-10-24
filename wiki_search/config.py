from decouple import config
from dotenv import load_dotenv

__all__ = ('WIKIPEDIA_URL', 'WIKIPEDIA_API_URI', 'REDIS_URI', 'PAGES_LIMIT', 'REVISIONS_LIMIT')


load_dotenv()


WIKIPEDIA_URL = config('WIKIPEDIA_URL', default='https://ru.wikipedia.org/w/index.php')
WIKIPEDIA_API_URI = config('WIKIPEDIA_API_URI', default='https://ru.wikipedia.org/w/api.php')
REDIS_URI = config('REDIS_URI')

PAGES_LIMIT = config('PAGES_LIMIT', default=5)
REVISIONS_LIMIT = config('REVISIONS_LIMIT', default=10)
CACHE_TTL_IN_SECONDS = 24 * 60 * 60

