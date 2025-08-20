import os
import re
import math
import hashlib
from typing import List, Dict, Optional, Iterable, Tuple

import psycopg2
import psycopg2.extras
import numpy as np

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

