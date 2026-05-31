from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
import requests

client = QdrantClient("http://localhost:6333")
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# 查詢 Qdrant
query = "什麼是晶圓測試"
query_vec = model.encode(query).tolist()
results = client.query_points(collection_name="demo", query=query_vec, limit=2)

# 組 context
context = "\n".join([r.payload["text"] for r in results.points])
print(f"檢索到的 context：\n{context}\n")

# 丟給 Ollama
response = requests.post("http://localhost:11434/api/generate", json={
    "model": "qwen2:7b",
    "prompt": f"Context:\n{context}\n\n問題：{query}\n\n請只根據上面的 context 回答。",
    "stream": False
})

print(f"LLM 回答：\n{response.json()['response']}")