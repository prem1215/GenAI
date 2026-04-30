import os
from langchain.chat_models import ChatGroq
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Set up LLM (still uses Groq)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
llm = ChatGroq(model_name="mixtral-8x7b-32768", groq_api_key=GROQ_API_KEY)

# HuggingFace Embedding setup
embedding_model_name = "sentence-transformers/all-MiniLM-L6-v2"
embeddings = HuggingFaceEmbeddings(
    model_name=embedding_model_name,
    model_kwargs={"device": "cpu"}  # use "cuda" if you have GPU
)

# Create FAISS vectorstore from input text
def create_vectorstore(text, index_path):
    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = [Document(page_content=chunk) for chunk in splitter.split_text(text)]
    db = FAISS.from_documents(docs, embeddings)
    db.save_local(index_path)
    return db

# Load existing vectorstore from disk
def load_vectorstore(index_path):
    return FAISS.load_local(index_path, embeddings)
