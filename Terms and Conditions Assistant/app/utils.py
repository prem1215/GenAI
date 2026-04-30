import requests
from bs4 import BeautifulSoup
import fitz  # PyMuPDF
import os
from sqlalchemy import create_engine, Column, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import hashlib

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class TermsCache(Base):
    __tablename__ = "terms_cache"
    domain = Column(String, primary_key=True, index=True)
    text_hash = Column(String)
    raw_text = Column(Text)

Base.metadata.create_all(bind=engine)

def fetch_terms_text(url):
    if url.lower().endswith(".pdf"):
        return extract_pdf_text(url)
    else:
        return extract_html_text(url)

def extract_html_text(url):
    res = requests.get(url)
    soup = BeautifulSoup(res.text, "html.parser")
    return soup.get_text()

def extract_pdf_text(url):
    res = requests.get(url)
    tmp_path = "/tmp/temp.pdf"
    with open(tmp_path, "wb") as f:
        f.write(res.content)
    doc = fitz.open(tmp_path)
    text = "\n".join(page.get_text() for page in doc)
    doc.close()
    os.remove(tmp_path)
    return text

def hash_text(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()

def is_updated(domain, new_text):
    session = SessionLocal()
    new_hash = hash_text(new_text)
    cached = session.query(TermsCache).filter_by(domain=domain).first()
    if cached:
        if cached.text_hash == new_hash:
            session.close()
            return False
        else:
            cached.text_hash = new_hash
            cached.raw_text = new_text
            session.commit()
            session.close()
            return True
    else:
        session.add(TermsCache(domain=domain, text_hash=new_hash, raw_text=new_text))
        session.commit()
        session.close()
        return True