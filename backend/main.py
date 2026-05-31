from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
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

class QueryRequest(BaseModel):
    question: str

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

@app.post("/query")
async def ask(req: QueryRequest):
    answer = query(req.question)
    return {"answer": answer}