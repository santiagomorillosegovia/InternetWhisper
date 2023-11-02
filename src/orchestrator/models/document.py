from pydantic import BaseModel
from typing import Optional


class Document(BaseModel):
    text: str
    url: str
    vector: list[float]
    similarity: float
