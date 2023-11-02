from typing import AsyncGenerator
from fastapi import FastAPI
from sse_starlette.sse import EventSourceResponse
from util import logger

import prompt
import openai
from retrieval import Retriever
from retrieval.search import GoogleAPI
from retrieval.cache import RedisVectorCache
from retrieval.scraper import ScraperLocal, ScraperRemote
from retrieval.embeddings import OpenAIEmbeddings, RemoteEmbeddings
from retrieval.splitter import LangChainSplitter


# # setup loggers
# logging.config.fileConfig("logging.conf", disable_existing_loggers=False)  # type: ignore
# logger = logging.getLogger(__name__)
app = FastAPI()


def stream_chat(prompt: str):
    for chunk in openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    ):
        content = chunk["choices"][0].get("delta", {}).get("content")  # type: ignore
        if content is not None:
            yield content


async def event_generator(query) -> AsyncGenerator[dict, None]:
    redis = RedisVectorCache(host="cache", port=6379)
    embeddings = OpenAIEmbeddings()
    google = GoogleAPI()
    scraper = ScraperLocal()
    splitter = LangChainSplitter(chunk_size=400, chunk_overlap=50, length_function=len)

    # scraper = ScraperRemoteClient()
    # embeddings = RemoteEmbeddings()

    # redis.init_test()
    try:
        redis.init_index(vector_dimension=embeddings.vector_dimension)
        logger.info(
            f"Created index with vector dimensions {embeddings.vector_dimension}"
        )
    except:
        logger.info("Index already exists.")

    retriever = Retriever(
        cache=redis,
        searcher=google,
        scraper=scraper,
        embeddings=embeddings,
        splitter=splitter,
    )
    async for event in retriever.get_context(query=query, cache_treshold=0.85, k=10):
        yield event
        if event["event"] == "context":
            final_prompt = prompt.rag.format(context=event["data"], question=query)

            yield {"event": "prompt", "data": final_prompt}

            for text in stream_chat(prompt=final_prompt):
                yield {"event": "token", "data": text}


@app.get("/streamingSearch")
async def main(query: str) -> EventSourceResponse:
    return EventSourceResponse(event_generator(query))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
