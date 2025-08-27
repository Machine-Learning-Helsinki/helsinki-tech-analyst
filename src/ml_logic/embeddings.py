from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
from sklearn.metrics.pairwise import cosine_similarity
import chromadb
import os


def process_exceddings(text):
    load_dotenv()

    print("STEP 1: Preparing sentences for embeddings...")
    sentences = [article[2] for article in text]  # Assuming (id, content, ...) format
    print(f"INFO: Found {len(sentences)} sentences to embed.")

    print("STEP 2: Loading embedding model...")
    model = SentenceTransformer("all-MiniLM-L6-v2")
    print("INFO: Model loaded successfully.")

    print("STEP 3: Encoding sentences...")
    embeddings = model.encode(sentences)
    print(f"INFO: Generated embeddings with shape {embeddings.shape}")

    print("STEP 4: Connecting to ChromaDB...")
    chromadb_client = chromadb.CloudClient(
        api_key=os.getenv("CHROMADB_API_KEY"),
        tenant=os.getenv("CHROMADB_TENANT"),
        database=os.getenv("CHROMADB_DATABASE"),
    )
    print("INFO: Connected to ChromaDB.")

    print("STEP 5: Creating/getting collection...")
    collection = chromadb_client.get_or_create_collection(name="article_embeddings")
    print("INFO: Collection ready.")

    print("STEP 6: Adding embeddings to collection...")
    collection.add(
        documents=sentences,
        embeddings=embeddings.tolist(),  # Convert numpy array to list
        ids=[str(i) for i in range(len(sentences))]
    )
    print("INFO: Embeddings stored successfully in ChromaDB.")

    

    print("INFO: 🎉 Embedding process completed.")
def process_embedding_without():
    """
    This function is a placeholder for processing embeddings without using ChromaDB.
    It can be used for testing or alternative processing methods.
    """
    print("This function is a placeholder for processing embeddings without ChromaDB.")
    # Implement alternative embedding processing logic here if needed



