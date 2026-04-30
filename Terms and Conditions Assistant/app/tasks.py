from celery import Celery
from langchain_qna import create_vectorstore
import os

BROKER_URL = os.getenv("BROKER_URL")
celery_app = Celery("tasks", broker=BROKER_URL)

@celery_app.task
def process_terms(domain, text):
    os.makedirs(f"faiss_indexes/{domain}", exist_ok=True)
    create_vectorstore(text, index_path=f"faiss_indexes/{domain}")