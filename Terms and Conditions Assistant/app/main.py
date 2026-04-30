from fastapi import FastAPI
from pydantic import BaseModel
from utils import fetch_terms_text, is_updated
from tasks import process_terms
from urllib.parse import urlparse
import os

app = FastAPI()

class TOSRequest(BaseModel):
    url: str

class QuestionRequest(BaseModel):
    domain: str
    question: str

@app.post("/upload_tos")
def upload_tos(data: TOSRequest):
    domain = urlparse(data.url).netloc
    text = fetch_terms_text(data.url)
    if is_updated(domain, text):
        process_terms.delay(domain, text)
        return {"message": "TOS updated and queued for processing."}
    else:
        return {"message": "TOS unchanged, using existing data."}

@app.post("/ask")
def ask_question(data: QuestionRequest):
    from langchain_qna import load_vectorstore, get_qa_chain
    domain_index_path = f"faiss_indexes/mixtral{data.domain}"
    vs = load_vectorstore(domain_index_path)
    chain = get_qa_chain(vs)
    answer = chain.run(data.question)
    return {"answer": answer}
