from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from datetime import datetime
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator, metrics

# DO NOT import rag functions here - causes circular import
# from ..ml_logic.rag import answer_questions, answer_question_for_postgre

app = FastAPI(
    title="Helsinki Tech Analyst API",
    description="API for Finnish news analysis and RAG-based question answering",
    version="1.0.0",
)

class Question(BaseModel):
    question: str
    context: Union[str, None] = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now(),
        "service": "Helsinki Tech Analyst API"
    }

@app.post("/ask")
async def asking(question: Question):
    """
    Endpoint to answer questions using the provided context.
    Import rag functions here to avoid circular imports.
    """
    # Import inside the function - only when endpoint is called
    from ..ml_logic.rag import answer_question_for_postgre
    
    print(question)
    
    if question.context:
        return {"answer": answer_question_for_postgre(question.question, question.context)}
    else:
        return {"answer": answer_question_for_postgre(question.question)}


if __name__ == "__main__":
    uvicorn.run(app)