from typing import List, Optional
from pydantic import BaseModel


class CSEThumbnail(BaseModel):
    src: str
    width: str
    height: str


class PageMap(BaseModel):
    cse_thumbnail: List[CSEThumbnail]


class SearchDoc(BaseModel):
    link: str
    title: Optional[str] = None
    displayLink: Optional[str] = None
    snippet: Optional[str] = None
    pagemap: Optional[PageMap] = None


class SearchResult(BaseModel):
    items: list[SearchDoc]
