from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from sentence_transformers import SentenceTransformer
import requests

client = QdrantClient("http://localhost:6333")
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
COLLECTION_NAME = "documents"

def query(question: str, source: str = None) -> dict:
    query_vec = model.encode(question).tolist()

    # 有指定文件就過濾，沒有就搜全部
    search_filter = None
    if source:
        search_filter = Filter(
            must=[FieldCondition(key="source", match=MatchValue(value=source))]
        )

    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vec,
        query_filter=search_filter,
        limit=3
    )

    context = "\n".join([r.payload["text"] for r in results.points])

    response = requests.post("http://localhost:11434/api/generate", json={
        "model": "qwen2:0.5b",
        "prompt": f"Context:\n{context}\n\n問題：{question}\n\n請只根據上面的 context 回答，如果 context 沒有相關資訊請回答「根據提供的文件無法回答此問題」。",
        "stream": False
    })

    return {
        "answer": response.json()["response"],
        "sources": [
            {"text": r.payload["text"][:100], "source": r.payload.get("source", "unknown"), "score": r.score}
            for r in results.points
        ]
    }

if __name__ == "__main__":
    import sys
    result = query(sys.argv[1])
    print(f"\n回答：{result['answer']}")