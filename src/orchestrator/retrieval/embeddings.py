from abc import ABC, abstractmethod
import json
import aiohttp

import openai


class Embeddings(ABC):
    """Abstraction of embeddings client."""

    @abstractmethod
    async def run(self, chunks: list[str]) -> list[list[float]]:
        pass


class RemoteEmbeddings(Embeddings):
    """Instanciates a client that implements _embeddings service."""

    vector_dimension = 384

    async def run(self, chunks: list[str]) -> list[list[float]]:
        url = f"http://embeddings/encode"
        headers = {"Content-Type": "application/json"}
        payload = json.dumps({"text": chunks})
        async with aiohttp.ClientSession() as session:
            async with session.post(url, data=payload, headers=headers) as response:
                if response.status == 200:
                    r = await response.json()
                    return r["embedding"]
        return [[]]


class OpenAIEmbeddings(Embeddings):
    """OpenAI embeddings client wrapper"""

    vector_dimension = 1536

    async def run(
        self, chunks: list[str], model="text-embedding-ada-002"
    ) -> list[list[float]]:
        response = await openai.Embedding.acreate(input=chunks, model=model)
        vectors = map(lambda x: x["embedding"], response["data"])  # type: ignore
        return list(vectors)
