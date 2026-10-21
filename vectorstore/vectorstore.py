
from langchain_community.vectorstores import FAISS

from agents.PolicyRag import PolicyRag
from embeddings.embedding import SentenceTransformersEmbedding


class VectorStore:

    def __init__(self):
        self.vector_store = None

    def create_vector_store(self):

        policy_rag = PolicyRag()

        chunks = policy_rag.chunking()

        embedding_model = SentenceTransformersEmbedding()

        self.vector_store = FAISS.from_documents(
            documents=chunks,
            embedding=embedding_model
        )

        print("Policy chunks stored in FAISS.")

        return self.vector_store
