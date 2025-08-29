import os
import psycopg2
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb
from google import genai
from google.genai import types
from ..ml_logic.vector_db import vectordatabasePg

load_dotenv()

# -----------------------------
# Helper: Initialize Gemini API
# -----------------------------
def get_gemini_client():
    client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    if not client:
        raise ValueError("Gemini client not initialized. Check your API key.")
    return client


# -----------------------------
# 1. Answer questions using ChromaDB
# -----------------------------
def answer_questions(question: str):
    try:
        print("DEBUG: Initializing embedding model...")
        model = SentenceTransformer("all-MiniLM-L6-v2")

        # Connect to ChromaDB
        print("DEBUG: Connecting to ChromaDB Cloud...")
        chromo_client = chromadb.CloudClient(
            api_key=os.getenv("CHROMADB_API_KEY"),
            tenant=os.getenv("CHROMADB_TENANT"),
            database=os.getenv("CHROMADB_DATABASE"),
        )
        collection = chromo_client.get_or_create_collection(name="article_embeddings")

        # Get Gemini client
        client = get_gemini_client()

        # Encode question
        q_embedding = model.encode([question])[0].tolist()

        # Query ChromaDB
        results = collection.query(
            query_embeddings=[q_embedding],
            n_results=5,
            include=["documents"]
        )
        if not results.get("documents"):
            return "No relevant documents found."
        
        context_docs = results["documents"][0]

        # Build prompt
        prompt = (
            "You are a helpful assistant. Use the following context to answer the question.\n\n"
            "Context:\n" + "\n".join(context_docs) + "\n\n"
            f"Question: {question}\n\n"
            "Answer the question based on the context provided."
        )

        # Call Gemini API
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.candidates[0].content.parts[0].text

    except Exception as e:
        print(f"ERROR in answer_questions: {e}")
        return str(e)


# -----------------------------
# 2. Answer questions using PostgreSQL
# -----------------------------
def answer_question_for_postgre(question: str):
    try:
        vectordatabase = vectordatabasePg()
        results = vectordatabase.query_similar_articles(query_text=question, top_k=5)
        if not results:
            return "No relevant articles found."
        
        context_docs = [ ]

        for res in results:
            title = res.get("title")
            summary = res.get("summary")
            context_doc = f"Title: {title}\nSummary: {summary}" if summary else f"Title: {title}"
            context_docs.append(context_doc)
            


        prompt = (
            "You are a helpful assistant. Use the following context to answer the question.\n\n"
            "Context:\n" + "\n".join(context_docs) + "\n\n"
            f"Question: {question}\n\n"
            "Answer the question based on the context provided."
        )

        # Get Gemini client
        client = get_gemini_client()

        # Call Gemini API
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )

        return response.candidates[0].content.parts[0].text

    except Exception as e:
        print(f"ERROR in answer_question_for_postgre: {e}")
        return f"Exception: {e}"


# -----------------------------
# 3. Process embeddings & store in ChromaDB
# -----------------------------
def process_and_store_embeddings(documents: list[str]):
    try:
        print("DEBUG: Initializing embedding model...")
        model = SentenceTransformer("all-MiniLM-L6-v2")

        print("DEBUG: Connecting to ChromaDB Cloud...")
        chromo_client = chromadb.CloudClient(
            api_key=os.getenv("CHROMADB_API_KEY"),
            tenant=os.getenv("CHROMADB_TENANT"),
            database=os.getenv("CHROMADB_DATABASE"),
        )
        collection = chromo_client.get_or_create_collection(name="article_embeddings")

        # Encode documents
        embeddings = model.encode(documents).tolist()

        # Store in ChromaDB
        collection.add(
            documents=documents,
            embeddings=embeddings,
            ids=[f"doc_{i}" for i in range(len(documents))]
        )

        print(f"INFO: Stored {len(documents)} documents in ChromaDB.")
        return True

    except Exception as e:
        print(f"ERROR in process_and_store_embeddings: {e}")
        return False
