from abc import ABC, abstractmethod
import hashlib
import json
import numpy as np
import pandas as pd
import redis
from redis.commands.search.field import (
    TextField,
    VectorField,
)
from redis.commands.search.indexDefinition import IndexDefinition, IndexType
from redis.commands.search.query import Query
from models.document import Document

VECTOR_DIMENSION = 1536


class VectorDbCache(ABC):
    @abstractmethod
    async def find_similar(self, vector: list[float], k=10) -> list[Document]:
        pass

    @abstractmethod
    async def write(self, documents: list[Document]):
        pass


SHA256 = hashlib.sha256()


class RedisVectorCache(VectorDbCache):
    _pool = None

    def __init__(self, host, port) -> None:
        if RedisVectorCache._pool is None:
            RedisVectorCache._pool = redis.ConnectionPool(host=host, port=port)

        self.client = redis.Redis(
            connection_pool=RedisVectorCache._pool, decode_responses=True
        )

    async def find_similar(self, vector: list[float], k=10) -> list[Document]:
        chunks = (
            self.client.ft("idx:chunks_vss")
            .search(
                Query(f"(*)=>[KNN {k} @vector $query_vector AS vector_score]")
                .sort_by("vector_score")
                .return_fields("vector_score", "text", "url", "vector")
                .dialect(2),
                {"query_vector": np.array(vector, dtype=np.float32).tobytes()},
            )
            .docs  # type: ignore
        )
        documents = map(
            lambda doc: Document(
                url=doc.url,
                text=doc.text,
                vector=json.loads(doc.vector),
                similarity=1 - float(doc.vector_score),
            ),
            chunks,
        )

        return list(documents)

    async def get_insertables(self, documents: list[Document]) -> list[Document]:
        insertables = []
        for document in documents:
            results = await self.find_similar(document.vector, k=1)
            if not results:
                insertables.append(document)
            elif results[0].similarity < 0.97:
                insertables.append(document)
        return insertables

    async def write(self, documents: list[Document]):
        documents = await self.get_insertables(documents)
        pipeline = self.client.pipeline()
        for document in documents:
            SHA256.update(document.text.encode("utf-8"))
            chunk_id = SHA256.hexdigest()
            redis_key = f"chunks:{chunk_id}"
            document.similarity = -1
            pipeline.json().set(redis_key, "$", document.model_dump())
            pipeline.expire(redis_key, 3600)

        pipeline.execute()

    def init_test(self):
        df = pd.read_pickle("mocks/database_pickle")
        df["vector"] = df["vector"].apply(lambda x: x.tolist()[0])
        chunks = df.to_dict("records")

        pipeline = self.client.pipeline()
        for chunk in chunks:
            SHA256.update(chunk["text"].encode("utf-8"))
            chunk_id = SHA256.hexdigest()
            redis_key = f"chunks:{chunk_id}"
            pipeline.json().set(redis_key, "$", chunk)
        pipeline.execute()

    def init_index(self, vector_dimension):
        schema = (
            TextField("$.text", no_stem=True, as_name="text"),
            TextField("$.url", no_stem=True, as_name="url"),
            VectorField(
                "$.vector",
                "FLAT",
                {
                    "TYPE": "FLOAT32",
                    "DIM": vector_dimension,
                    "DISTANCE_METRIC": "COSINE",
                },
                as_name="vector",
            ),
        )
        definition = IndexDefinition(prefix=["chunks:"], index_type=IndexType.JSON)
        self.client.ft("idx:chunks_vss").create_index(
            fields=schema, definition=definition
        )
