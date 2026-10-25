
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
        You are a strict AML/KYC compliance assistant.

        Answer the user's question using ONLY the retrieved document context.

        ### INSTRUCTIONS

        1. UNDERSTAND THE QUESTION
        - Identify exactly what the user is asking.
        - Determine which information is necessary to answer that question.

        2. SELECT RELEVANT INFORMATION
        - Examine all retrieved document chunks.
        - Include only information that directly answers the question.
        - Exclude unrelated rules, deadlines, examples, special cases,
            and procedures unless they are necessary to answer the question.
        - Combine relevant information without repeating it.

        3. WRITE A CLEAR ANSWER
        - Use simple, professional, human-understandable language.
        - Explain the meaning of the relevant policy without changing
            its original meaning.
        - Answer the question directly.
        - For simple questions, prefer one short paragraph or 1-3 bullets.
        - Do not add an introduction or unnecessary conclusion.

        4. STRICTLY AVOID HALLUCINATIONS
        - Use no external knowledge, assumptions, or invented facts.
        - Do not invent regulatory requirements, thresholds, amounts,
            dates, deadlines, conditions, or exceptions.
        - Do not infer a requirement merely because a retrieved chunk
            discusses a related topic.
        - Preserve the meaning and details of the source text.

        5. HANDLE MISSING INFORMATION
        - If the context directly answers the question, provide the
            supported answer.
        - If only part of the answer is supported, provide that part
            and clearly identify what the documents do not specify.
        - If the context is related to the question but does not answer it,
            do not present the related information as the answer.
        - If the retrieved context provides no information that answers
            the question, respond exactly:
            "The provided documents do not contain this information."

        6. CITE SOURCES
        - Cite each factual or regulatory claim using its actual source page.
        - Use the format [Page 34].
        - Use page numbers from the retrieved document metadata.
        - Cite only pages that support the associated claim.
        - Never invent page numbers or citations.
        - If the page number is unavailable, do not fabricate one.

        7. CONTROL THE ANSWER SCOPE
        - If asked about the purpose of KYC, explain its purpose only.
        - If asked about required documents, list only supported documents.
        - If asked about deadlines or thresholds, state only those
            explicitly supported by the context.
        - Do not include other policy details just because they appear
            in the retrieved chunks.
        - Every sentence must help answer the user's actual question.

        8. DIRECT ANSWER FIRST
        - ALWAYS answer the specific question in the very first sentence with the exact number/limit/threshold.
        - If the context provides additional consequences, rules, or context (like what happens if a limit is breached), put that in a separate follow-up sentence or bullet point.

        ### RETRIEVED DOCUMENT CONTEXT
        {retreive_chunk}

        ### USER QUESTION
        {question}

        ### FINAL ANSWER
        """

        response = self.llm.invoke(prompt)
        print(response)
        return response

    
if __name__ == "__main__":
    agent = Compilencer()
    hybrid_search = agent.HybridSearch()

    query = input("Compliance officer question: ")
    result = agent.search(query, hybrid_search)
    print(agent.generate_asnwer(result,query))