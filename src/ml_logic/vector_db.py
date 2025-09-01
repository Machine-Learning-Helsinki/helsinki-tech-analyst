import os
import re
import math
import hashlib
from typing import List, Dict, Optional, Iterable, Tuple
from dotenv import load_dotenv
from ..data_pipeline.storage import connect_storage

import psycopg2
import psycopg2.extras
import numpy as np

DB_URL = os.getenv("DB_URL")
EMBED_DIM = int(os.getenv("EMBED_DIM", "512"))
TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")

def tokenize(text: str) -> List[str]:
    return TOKEN_RE.findall(text.lower())

def hash_str_to_bucket(s: str, dim: int) -> int:
    h = hashlib.sha1(s.encode("utf-8")).hexdigest()
    return int(h, 16) % dim

def encode_custom(text: str, dim: int = EMBED_DIM, use_bigrams: bool = True):
    toks = tokenize(text)
    vec = np.zeros(dim, dtype=np.float32)

    try:
        for t in toks:
            idx = hash_str_to_bucket(f"uni::{t}", dim)
            vec[idx] += 1.0

        if use_bigrams and len(toks) >= 2:
            for a, b in zip(toks, toks[1:]):
                idx = hash_str_to_bucket(f"bi::{a}|{b}", dim)
                vec[idx] += 1.0

        np.log1p(vec, out=vec)
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec /= norm
    except Exception as e:
        print(f"ERROR encoding text: {e}")
    return vec


class vectordatabasePg:
    def __init__(self):
        try:
            self.conn = connect_storage()
            self.conn.autocommit = True
            print("INFO: Connected to PostgreSQL successfully.")
        except Exception as e:
            print(f"ERROR connecting to PostgreSQL: {e}")
            self.conn = None

    def close(self):
        try:
            if self.conn:
                self.conn.close()
                print("INFO: Connection closed.")
        except Exception as e:
            print(f"ERROR closing connection: {e}")

    def create_ivfflat_index(self, lists: int = 100, use_cosine: bool = True):
        if not self.conn:
            print("ERROR: No DB connection.")
            return
        try:
            opclass = "vector_cosine_ops" if use_cosine else "vector_l2_ops"
            with self.conn.cursor() as cur:
                cur.execute("DROP INDEX IF EXISTS idx_articles_vector")
                cur.execute(
                    f"""
                    CREATE INDEX articles_embedding_idx
                    ON articles USING ivfflat (embedding {opclass})
                    WITH (lists = %s);
                    """,
                    (lists,)
                )
                cur.execute("ANALYZE articles;")
                print("INFO: Index created successfully.")
        except Exception as e:
            print(f"ERROR creating index: {e}")

    def upsert_articles(self):
        if not self.conn:
            print("ERROR: No DB connection.")
            return
        print("INFO: Inserting/updating article embeddings...")
        try:
            with self.conn.cursor() as cur:
                # Ensure embedding column exists
                try:
                    cur.execute(
                        f"ALTER TABLE articles ADD COLUMN IF NOT EXISTS embedding vector({EMBED_DIM})"
                    )
                    print("INFO: Verified embedding column exists.")
                except Exception as e:
                    print(f"ERROR adding embedding column: {e}")

                # Fetch articles
                cur.execute("SELECT * FROM articles;")
                docs = cur.fetchall()
                if not docs:
                    print("INFO: No articles found.")
                    return

                docs = [dict(zip([col[0] for col in cur.description], row)) for row in docs]
                print(f"INFO: Found {len(docs)} articles.")

                for d in docs:
                    try:
                        summary = ""
                        doc_id = d.get("articles_id") or d.get("id")
                        if d.get("summary") is None or d.get("summary").strip() == "":
                            print(f"WARNING: Article id={doc_id} has no summary, skipping...")
                            summary = d.get("title", "")
                        else: 
                            summary = d.get("summary", "")
                        emb = encode_custom(summary, EMBED_DIM).tolist()

                        cur.execute(
                            """
                            UPDATE articles
                            SET embedding = %s
                            WHERE articles_id = %s
                            """,
                            (emb, doc_id)
                        )
                        print(f"INFO: Updated embedding for article_id={doc_id}")
                    except Exception as e:
                        print(f"ERROR updating article {d}: {e}")
        except Exception as e:
            print(f"ERROR in upsert_articles: {e}")

    def fetch_all_articles(self, table: str = "articles") -> List[Dict]:
        """
        Fetch all rows (id, title, content, embedding)
        """
        with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(f"SELECT id, title, content, embedding FROM {table};")
            rows = cur.fetchall()
            return [dict(r) for r in rows]

    def count(self) -> int:
        if not self.conn:
            print("ERROR: No DB connection.")
            return 0
        try:
            with self.conn.cursor() as cur:
                cur.execute("SELECT COUNT(*) FROM articles;")
                count = cur.fetchone()[0]
                print(f"INFO: Articles count = {count}")
                return count
        except Exception as e:
            print(f"ERROR counting articles: {e}")
            return 0
    def query_similar_articles(self, query_text: str, top_k: int = 5):
        """
        Query the vector database for the most similar articles to the given text.
        Uses <-> operator for cosine distance (pgvector).
        """
        if not self.conn:
            print("ERROR: No DB connection.")
            return []

        try:
            # Generate embedding for the query
            query_vec = encode_custom(query_text, EMBED_DIM).tolist()
            vec_str = "[" + ",".join([str(x) for x in query_vec]) + "]"

            with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
                cur.execute(
                    """
                    SELECT articles_id, link_name, title, link, published, summary, authors,tags,embedding
                    FROM articles
                    WHERE embedding IS NOT NULL
                    ORDER BY embedding <=> %s::vector
                    LIMIT %s;
                    """,
                    (vec_str, top_k)
                )
                rows = cur.fetchall()
                return [dict(r) for r in rows]
        except Exception as e:
            print(f"ERROR querying similar articles: {e}")
            return []
