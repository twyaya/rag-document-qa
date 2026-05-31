from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import fitz  # pymupdf
import docx
import uuid

client = QdrantClient("http://localhost:6333")
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
COLLECTION_NAME = "documents"

def init_collection():
    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION_NAME not in existing:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )

def chunk_text(text: str, chunk_size: int = 300, overlap: int = 50) -> list[str]:
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def read_pdf(path: str) -> str:
    doc = fitz.open(path)
    return "\n".join(page.get_text() for page in doc)

def read_docx(path: str) -> str:
    doc = docx.Document(path)
    return "\n".join(p.text for p in doc.paragraphs if p.text.strip())

def ingest_file(path: str):
    init_collection()

    # 讀檔
    if path.endswith(".pdf"):
        text = read_pdf(path)
    elif path.endswith(".docx"):
        text = read_docx(path)
    else:
        raise ValueError("只支援 PDF 或 DOCX")

    # 切塊
    chunks = chunk_text(text)
    print(f"切成 {len(chunks)} 塊")

    # embedding + 寫入
    vectors = model.encode(chunks).tolist()
    points = [
        PointStruct(
            id=str(uuid.uuid4()),
            vector=v,
            payload={"text": c}
        )
        for v, c in zip(vectors, chunks)
    ]
    client.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"寫入完成，共 {len(points)} 筆")

if __name__ == "__main__":
    import sys
    ingest_file(sys.argv[1])