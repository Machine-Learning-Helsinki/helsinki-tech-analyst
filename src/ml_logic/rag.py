import os 
import psycopg2
import numpy as np
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
import chromadb
from google import genai
from google.genai import types

load_dotenv()


def answer_questions(question: str):
    """
    Main function to answer a question using embeddings, ChromaDB, and Gemini API.
    """
    try:
        print("DEBUG: Initializing embedding model...")
        model = SentenceTransformer("all-MiniLM-L6-v2")
        print("DEBUG: Embedding model loaded successfully.")

        # Connect to ChromaDB
        print("DEBUG: Connecting to ChromaDB Cloud...")
        chromo_client = chromadb.CloudClient(
            api_key=os.getenv("CHROMADB_API_KEY"),
            tenant=os.getenv("CHROMADB_TENANT"),
            database=os.getenv("CHROMADB_DATABASE"),
        )

        if not chromo_client:
            print("ERROR: ChromoDB client not initialized.")
            return "ChromoDB client not initialized. Check your API keys and environment variables."
        print("INFO: ChromoDB client initialized successfully.")

        # Get or create collection
        print("DEBUG: Getting or creating 'article_embeddings' collection...")
        collection = chromo_client.get_or_create_collection(name="article_embeddings")
        if not collection:
            print("ERROR: Collection not found or could not be created.")
            return "Collection not found or could not be created. Check your ChromoDB setup."
        print("INFO: Collection 'article_embeddings' ready.")

        # Connect to Gemini API
        print("DEBUG: Connecting to Gemini API...")
        client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        if not client:
            print("ERROR: Gemini client not initialized.")
            return "Gemini client not initialized. Check your API keys and environment variables."
        print("INFO: Gemini client initialized successfully.")

        # Encode the question
        print(f"DEBUG: Encoding question: {question}")
        q_embedding = model.encode([question])[0].tolist()
        print(f"INFO: Question embedding generated. Dimension: {len(q_embedding)}")

        # Query ChromaDB
        print("DEBUG: Querying ChromaDB for top 5 similar documents...")
        results = collection.query(
            query_embeddings=[q_embedding],
            n_results=5,
            include=["documents"]
        )
        print(f"DEBUG: Raw ChromaDB query results: {results}")

        if not results.get("documents"):
            print("WARNING: No relevant documents found in ChromaDB.")
            return "No relevant documents found."
        
        context_docs = results["documents"][0]
        print(f"INFO: Retrieved {len(context_docs)} context documents.")

        # Build prompt
        prompt = (
            "You are a helpful assistant. Use the following context to answer the question.\n\n"
            "Context:\n" + "\n".join(context_docs) + "\n\n"
            f"Question: {question}\n\n"
            "Answer the question based on the context provided."
        )
        print("DEBUG: Prompt built successfully.")

        # Call Gemini API
        print("DEBUG: Sending prompt to Gemini API...")
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        print("INFO: Response generated from Gemini API.")

        # Extract text
        final_answer = response.candidates[0].content.parts[0].text
        print(f"DEBUG: Final answer extracted: {final_answer[:100]}...")  # preview only first 100 chars
        return final_answer

    except Exception as e:
        print(f"ERROR: Exception occurred: {e}")
        return str(e)
