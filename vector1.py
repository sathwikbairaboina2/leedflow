import json
import os
from celery import Celery, signals
import faiss
import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer


# from app.main import celery_app

# Global variables to store model and index
model = None
index = None
data = None
testdata = None
broker_url = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379")
result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379")

celery_app = Celery("worker", backend=result_backend, broker=broker_url)

print("celery config", broker_url, result_backend)


@signals.worker_process_init.connect
def setup_model(**kwargs):
    """Initialize SentenceTransformer model, data, and FAISS index when worker starts."""
    global model, index, data

    # Load SentenceTransformer model
    model = SentenceTransformer("all-MiniLM-L6-v2")

    # Sample Scandinavian names & country
    with open("app/utils/dataset.json", "r") as f:
        global testdata
        testdata = json.load(f)

    data = pd.DataFrame(testdata)

    # Combine name + country for embedding (combined vector)
    data["full_text"] = data["name"] + "," + data["country"]
    embeddings = model.encode(data["full_text"].tolist(), convert_to_numpy=True)

    # Build FAISS index
    dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(dim)
    index.add(embeddings)


@celery_app.task
def find_scandinavian_person(name: str, country: str, top_k: int = 3):
    """Celery task to find similar Scandinavian names using vector search."""
    print("find_scandinavian_person", name, country)
    global model, index, data
    query = name + "," + country
    query_vec = model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_vec, top_k)

    results = data.iloc[indices[0]].copy()
    results["similarity_score"] = 1 / (1 + distances[0])  # data normalization
    results = results.sort_values(by="similarity_score", ascending=False)

    #  Explicitly convert to list of dicts and return
    return [
        {
            "name": row["name"],
            "country": row["country"],
            "similarity_score": float(row["similarity_score"]),
        }
        for _, row in results.iterrows()
    ]
