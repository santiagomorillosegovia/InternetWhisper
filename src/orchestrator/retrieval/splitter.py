from abc import ABC, abstractmethod
import numpy as np
import spacy
from langchain.text_splitter import RecursiveCharacterTextSplitter


class Splitter(ABC):
    @abstractmethod
    async def split(self, text: str) -> list[str]:
        pass


class LangChainSplitter(Splitter):
    def __init__(self, chunk_size, chunk_overlap, length_function) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.length_function = length_function

    async def split(self, text: str) -> list[str]:
        text_splitter = RecursiveCharacterTextSplitter(
            # Set a really small chunk size, just to show.
            separators=["\n\n", "\n", " ", ""],
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=self.length_function,
            # is_separator_regex=False,
        )
        chunks = text_splitter.split_text(text)

        return chunks


nlp = spacy.load("en_core_web_sm")


class AdjSenSplitter(Splitter):
    def __init__(self) -> None:
        pass

    async def process(self, text):
        # Load the Spacy model
        doc = nlp(text)
        sents = list(doc.sents)
        vecs = np.stack([sent.vector / sent.vector_norm for sent in sents])  # type: ignore

        return sents, vecs

    async def cluster_text(self, sents, vecs, threshold):
        clusters = [[0]]
        for i in range(1, len(sents)):
            if np.dot(vecs[i], vecs[i - 1]) < threshold:
                clusters.append([])
            clusters[-1].append(i)

        return clusters

    async def split(self, text: str, similarity_treshold: float = 0.6):
        # Initialize the clusters lengths list and final texts list
        clusters_lens = []
        final_texts = []

        # Process the chunk
        threshold = 0.5
        sents, vecs = await self.process(text)

        # Cluster the sentences
        clusters = await self.cluster_text(sents, vecs, threshold)

        for cluster in clusters:
            cluster_txt = " ".join([sents[i].text for i in cluster])
            cluster_len = len(cluster_txt)

            # Check if the cluster is too short
            if cluster_len < 60:
                continue

            # Check if the cluster is too long
            elif cluster_len > 3000:
                threshold = similarity_treshold
                sents_div, vecs_div = await self.process(cluster_txt)
                reclusters = await self.cluster_text(sents_div, vecs_div, threshold)

                for subcluster in reclusters:
                    div_txt = " ".join([sents_div[i].text for i in subcluster])
                    div_len = len(div_txt)

                    if div_len < 60 or div_len > 3000:
                        continue

                    clusters_lens.append(div_len)
                    final_texts.append(div_txt)

            else:
                clusters_lens.append(cluster_len)
                final_texts.append(cluster_txt)

        return final_texts
