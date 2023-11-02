from fastapi import FastAPI
from pydantic import BaseModel
from sentence_transformers import SentenceTransformer
import logging

# setup loggers
logging.config.fileConfig("logging.conf", disable_existing_loggers=False)  # type: ignore
logger = logging.getLogger(__name__)
app = FastAPI()


class Body(BaseModel):
    text: str | list[str]


MODEL = SentenceTransformer("multi-qa-MiniLM-L6-cos-v1")


@app.post("/encode")
async def encode(body: Body):
    embedding = MODEL.encode(body.text)
    data = embedding.astype(float)  # type: ignore
    return {"embedding": data.tolist()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8080)
