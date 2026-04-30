import pytest
from fastapi.testclient import TestClient
from app.main import app
from unittest.mock import patch

client = TestClient(app)

@patch("app.utils.fetch_terms_text")
def test_upload_tos_new(mock_fetch):
    mock_fetch.return_value = "These are some sample terms of service."
    response = client.post("/upload_tos", json={"url": "https://example.com/tos.pdf"})
    assert response.status_code == 200
    assert "queued" in response.json().get("message", "") or "unchanged" in response.json().get("message", "")

@patch("app.langchain_qna.load_vectorstore")
@patch("app.langchain_qna.get_qa_chain")
def test_ask_question_valid(mock_chain, mock_load):
    mock_chain.return_value.run.return_value = "Refunds are available within 30 days."
    mock_load.return_value.as_retriever.return_value = None
    response = client.post("/ask", json={"domain": "example.com", "question": "What is the refund policy?"})
    assert response.status_code == 200
    assert "answer" in response.json()

@patch("app.utils.fetch_terms_text")
def test_upload_invalid_url(mock_fetch):
    mock_fetch.side_effect = Exception("Invalid URL")
    response = client.post("/upload_tos", json={"url": "bad-url"})
    assert response.status_code in [422, 500]