
from sentence_transformers import SentenceTransformer
from langchain_core.embeddings import Embeddings


class SentenceTransformersEmbedding(Embeddings):

    def __init__(self):
        self.emb_model = SentenceTransformer("all-MiniLM-L6-v2")

    def embed_documents(self, texts):
        embeddings = self.emb_model.encode(
            texts,
            normalize_embeddings=True
        )
        return embeddings.tolist()

    def embed_query(self, text):
        embedding = self.emb_model.encode(
            text,
            normalize_embeddings=True
        )
        return embedding.tolist()
