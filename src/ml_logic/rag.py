import os 
import psycopg2
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from ..data_pipeline.storage import connect_storage
import chromadb
from google import genai
from google.genai import types

load_dotenv()

# The client gets the API key from the environment variable `GEMINI_API_KEY`.
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))





model = SentenceTransformer("all-MiniLM-L6-v2")
chromo_client = chromadb.CloudClient(
    api_key=os.getenv("CHROMADB_API_KEY"),
    tenant=os.getenv("CHROMADB_TENANT"),
    database=os.getenv("CHROMADB_DATABASE"),
)
collection = chromo_client.get_or_create_collection(name="article_embeddings")



def answer_questions(question: str):

    print("INFO: Generating embeddings for the question...")
    q_embedding = model.encode([question])[0].tolist()

    print("INFO: Querying ChromoDB for top5 results...")
    results = collection.query(
        query_embeddings=[q_embedding],
        n_results=5,
        include=["documents"]
    )
    
    if not results["documents"]:
        return "No relevant documents found."
    context = results["documents"][0]

    prompt = (
        "You are a helpful assistant. Use the following context to answer the question.\n\n"
        "to answer the question, use the context provided below:\n\n"
        f"Context: {context}\n\n"   
        f"Question: {question}\n\n"
        "Answer the question based on the context provided."
    )
    print("INFO: Context retrieved from ChromoDB.")

    

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt
        
    )

    print("INFO: Response generated from OpenAI API.")
    return response.candidates[0].content.parts[0].text

    



    #Build prompt







