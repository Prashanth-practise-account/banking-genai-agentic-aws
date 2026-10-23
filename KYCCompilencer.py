
import os
from pypdf import PdfReader
from embeddings.embedding import SentenceTransformersEmbedding
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever
from langchain_ollama import ChatOllama

from agents.PolicyRag import PolicyRag


class Compilencer:
    def __init__(self):
        self.llm = ChatOllama(
    model="qwen2.5:7b",
    temperature=0,
    num_predict=1000,
    timeout=30
)
        base = os.path.dirname(os.path.abspath(__file__))
        filepath = os.path.join(
            base, "data",
            "MD18KYCF6E92C82E1E1419D87323E3869BC9F13.pdf"
        )

        text = ""
        self.document = []
        self.splitter = PolicyRag().splitter
        self.embedding = SentenceTransformersEmbedding()

        read = PdfReader(filepath)

        for page_number, page in enumerate(read.pages, start=1):
            text = page.extract_text() or ""
            chunks = self.splitter.split_text(text)

            for chunk in chunks:
                self.document.append(
                    Document(
                        page_content=chunk,
                        metadata={"page": page_number}
                    )
                )

        print(len(self.document))

    def HybridSearch(self):
        vector_store = FAISS.from_documents(
            self.document, self.embedding
        )

        keyward_search = BM25Retriever.from_documents(
            self.document
        )
        keyward_search.k = 5

        HybridSearch = EnsembleRetriever(
            retrievers=[
                keyward_search,
                vector_store.as_retriever(search_kwargs={"k": 3})
            ],
            weights=[0.5, 0.5]
        )

        return HybridSearch

    def search(self, query, hybridsearch):
        res = hybridsearch.invoke(query)

        for doc in res:
            print("Page:", doc.metadata["page"])
            print("Policy chunk:", doc.page_content)
            print("-" * 50)

        return res

    def generate_asnwer(self,retreive_chunk,question):
        context = "\n\n".join(
        f"Page {doc.metadata['page']}:\n{doc.page_content}"
        for doc in retreive_chunk
    )
        prompt = f"""
            You are an AML/KYC compliance assistant.
            Answer the question using ONLY the context below.
            Do not invent regulatory thresholds or requirements.
            If the context does not answer the question, say so.
            Cite the supporting page number for every regulatory claim.
            Context:
            {context}

            Question: {question}

            Answer:
        """
        response = self.llm.invoke(prompt)
        return response

    
if __name__ == "__main__":
    agent = Compilencer()
    hybrid_search = agent.HybridSearch()

    query = input("Compliance officer question: ")
    result = agent.search(query, hybrid_search)
    print(agent.generate_asnwer(result,query))