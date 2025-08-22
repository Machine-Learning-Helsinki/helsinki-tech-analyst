import os 
import psycopg2
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from ..data_pipeline.storage import connect_storage
import chromadb
from openai import OpenAI

load_dotenv()

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
    print(results)
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

    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    response = client.chat.completions.create(
        model="gpt-5",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    print("INFO: Response generated from OpenAI API.")
    print(response)

    



    #Build prompt







