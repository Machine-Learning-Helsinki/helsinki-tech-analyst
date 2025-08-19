from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
import chromadb
import os


def process_exceddings(text):
    load_dotenv()

    print("STEP 1: Preparing sentences for embeddings...")
    sentences = [article[1] for article in text]  # Assuming (id, content, ...) format
    print(f"INFO: Found {len(sentences)} sentences to embed.")

    print("STEP 2: Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("INFO: Model loaded successfully.")

    print("STEP 3: Encoding sentences...")
    embeddings = model.encode(sentences)
    print(f"INFO: Generated embeddings with shape {embeddings.shape}")
    print(embeddings)

    
