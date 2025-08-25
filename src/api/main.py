from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from fastapi.middleware.cors import CORSMiddleware

from ..ml_logic.rag import answer_questions

app = FastAPI()
class Question(BaseModel):
    question: str
    context: Union[str, None] = None
s
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/ask")
async def asking(question: Question):
    """
    Endpoint to answer questions using the provided context.
    """
    print(question)
    
    if question.context:
        return {"answer": answer_questions(question.question, question.context)}
    else:
        return {"answer": answer_questions(question.question)}
    



if __name__ == "__main__":
    uvicorn.run(app)
    



