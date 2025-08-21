import os
import re
import math
import hashlib
from typing import List, Dict, Optional, Iterable, Tuple

import psycopg2
import psycopg2.extras
import numpy as np

PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = int(os.getenv("PG_PORT", "5432"))
PG_DB   = os.getenv("PG_DB", "appdb")
PG_USER = os.getenv("PG_USER", "app")
PG_PASS = os.getenv("PG_PASS", "app")

EMBED_DIM = int(os.getenv("EMBED_DIM","512"))

TOKEN_RE = re.compile(r"[a-zA-Z0-9]+")

def tokenize(text:str) -> List[str]:
    #lowercase, keep alphanumerics
    return TOKEN_RE.findall(text.lower())

#-custom hashing encoder
def hash_str_to_bucket(s: str, dim: int) -> int:
    h = hashlib.sha1(s.encode("utf-8")).hexdigest()
    return int(h,16) % dim

def encode_custom(text: str, dim: int = EMBED_DIM, use_bigrams: bool = True):
    toks = tokenize(text)
    vec = np.zeros(dim, dtype= np.float32)

    #unigrams
    for t in toks:
        idx = hash_str_to_bucket(f"uni::{t}", dim)
        vec[idx]+= 1.0
    
    #bigrams
    if use_bigrams and len(toks) >= 2:
        for a,b in zip(toks, toks[1:]):
            idx = hash_str_to_bucket(f"bi::{a}|{b}", dim)
            vec[idx]+= 1.0
    
    #damp very frequent counts
    np.log1p(vec, out=vec)
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec/= norm
    return vec



# Postgres + pgvector client
class vectordatabasePg:
    def __init__(self, host: str = PG_HOST,
                 port: int = PG_PORT,
                 db: str = PG_DB,
                 user: str = PG_USER,
                 password: str = PG_PASS):
        self.conn = psycopg2.connect(
            host=host, port=port, dbname=db, user=user, password=password
        )
        self.conn.autocommit = True
    @classmethod
    def anotherCons(self, link:str):
        self.conn = psycopg2.connect(link)


    def close(self):
        if self.conn:
            self.conn.close()

    def create_ivfflat_index(self, lists: int= 100, use_cosine: bool = True):
        opclass = "vector_cosine_ops_v2" if use_cosine else "vector_l2_ops_v2"
        with self.conn.cursor() as cur:
            cur.execute(f"""
                DROP INDEX IF EXISTS idx_articles_vector""")
            cur.execute(
                f"CREATE INDEX articles_embedding_idx ON articles "
                f"USING ivfflat (embedding {opclass}) WITH (lists = %s);",
                (lists,)
            )
            cur.execute(f"ANALYZE articles;")
            print("INFO: Index created successfully.")
    
    

        
    



