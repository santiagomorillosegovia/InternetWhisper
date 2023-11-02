from abc import ABC, abstractmethod
import os
from urllib.parse import urlencode
from models.search import SearchResult
import aiohttp

from mocks.test_dict import provisional_search_result

GOOGLE_API_URL = os.environ["GOOGLE_API_HOST"]
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
GOOGLE_CX = os.environ["GOOGLE_CX"]
GOOGLE_FIELDS = os.environ["GOOGLE_FIELDS"]
HEADER_ACCEPT_ENCODING = os.environ["HEADER_ACCEPT_ENCODING"]
HEADER_USER_AGENT = os.environ["HEADER_USER_AGENT"]
REQUEST_HEADERS = {
    "Accept-Encoding": HEADER_ACCEPT_ENCODING,
    "User-Agent": HEADER_USER_AGENT,
}


class Searcher(ABC):
    @abstractmethod
    async def run(self, query: str) -> SearchResult:
        pass


class GoogleAPI(Searcher):
    def __init__(self) -> None:
        super().__init__()

    async def run(self, query: str) -> SearchResult:
        query_params = urlencode(
            {
                "key": GOOGLE_API_KEY,
                "fields": GOOGLE_FIELDS,
                "cx": GOOGLE_CX,
                "q": query,
            }
        )
        url = f"{GOOGLE_API_URL}{query_params}"

        async with aiohttp.ClientSession() as session:
            async with session.get(
                url,
                headers=REQUEST_HEADERS,
            ) as response:
                r = await response.json()
                try:
                    return SearchResult(**r)
                except Exception as e:
                    print("SEARCHER", e)
                    return SearchResult(**provisional_search_result)
