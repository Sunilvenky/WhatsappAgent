"""
Simple LLM stub service for local development. Responds to POST /v1/complete with deterministic responses.
"""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="LLM Stub")


class CompleteRequest(BaseModel):
    prompt: str
    max_tokens: Optional[int] = 50


@app.post("/v1/complete")
def complete(req: CompleteRequest):
    p = req.prompt.lower()
    # deterministic behavior used by tests and dev
    if "redraft" in p:
        return {"id": "stub-1", "text": "[Redraft] " + req.prompt}
    if "classify" in p:
        return {"id": "stub-1", "label": "positive", "score": 0.95}
    # default deterministic echo
    return {"id": "stub-1", "text": "[Echo] " + req.prompt}