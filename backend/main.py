from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
import shutil, os
from ingest import ingest_file
from query import query

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = QdrantClient("http://localhost:6333")
COLLECTION_NAME = "documents"

class QueryRequest(BaseModel):
    question: str
    source: str = None

@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    tmp_path = f"tmp_{file.filename}"
    with open(tmp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    try:
        ingest_file(tmp_path)
    finally:
        os.remove(tmp_path)
    return {"message": f"{file.filename} 已成功寫入"}

@app.get("/documents")
async def list_documents():
    try:
        points = client.scroll(
            collection_name=COLLECTION_NAME,
            limit=10000,
            with_payload=True
        )[0]
        sources = list(set([p.payload.get("source", "unknown") for p in points]))
        return {"documents": sorted(sources)}
    except:
        return {"documents": []}

@app.delete("/documents/{filename}")
async def delete_document(filename: str):
    try:
        client.delete(
            collection_name=COLLECTION_NAME,
            points_selector=Filter(
                must=[FieldCondition(key="source", match=MatchValue(value=filename))]
            )
        )
        return {"message": f"{filename} 已刪除"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/query")
async def ask(req: QueryRequest):
    result = query(req.question, source=req.source)
    return result