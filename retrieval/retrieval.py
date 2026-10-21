
from vectorstore.vectorstore import VectorStore

vector_store = VectorStore()
vector_store.create_vector_store()


def retrieve_policy(query, top_k=3):

    similarity_score = vector_store.vector_store.similarity_search_with_score(query,k=top_k)

    retrieved_policies = []

    for document, score in similarity_score:
        retrieved_policies.append({
            "policy_id": document.metadata["policy_id"],
            "chunk_id": document.metadata["chunk_id"],
            "source": document.metadata["source"],
            "policy_text": document.page_content,
            "distance": float(score)
        })

    return retrieved_policies


if __name__ == "__main__":

    results = retrieve_policy(
        "What is the minimum credit score required?",
        top_k=3
    )

    for result in results:
        print("\nPolicy ID:", result["policy_id"])
        print("Chunk ID:", result["chunk_id"])
        print("Source:", result["source"])
        print("Distance:", result["distance"])
        print("Policy:", result["policy_text"])
