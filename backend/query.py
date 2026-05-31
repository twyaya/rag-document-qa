from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import requests

client = QdrantClient("http://localhost:6333")
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
COLLECTION_NAME = "documents"

def query(question: str) -> str:
    # 問題向量化
    query_vec = model.encode(question).tolist()

    # Qdrant 搜尋
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vec,
        limit=3
    )

    # 組 context
    context = "\n".join([r.payload["text"] for r in results.points])

    # 呼叫 Ollama
    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "qwen2:0.5b",
        "prompt": f"Context:\n{context}\n\n問題：{question}\n\n請只根據上面的 context 回答，如果 context 沒有相關資訊請說不知道。",
        "stream": False
    })

    return response.json()["response"]

if __name__ == "__main__":
    import sys
    answer = query(sys.argv[1])
    print(f"\n回答：{answer}")