import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer
from celery import Celery, signals
from celery.result import AsyncResult

celery = Celery(
    "faiss", broker="redis://127.0.0.1:6379/0", backend="redis://127.0.0.1:6379/0"
)


# Use a strong sentence embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# Sample Scandinavian names & country
testdata = pd.read_json("app/utils/dataset.json")
data = pd.DataFrame(testdata)

# Combine name + country for embedding (combined vector)
data["full_text"] = data["name"] + "," + data["country"]
embeddings = model.encode(data["full_text"].tolist(), convert_to_numpy=True)

# Build FAISS index
dim = embeddings.shape[1]
index = faiss.IndexFlatL2(dim)
index.add(embeddings)


def find_scandinavian_person(name: str, country: str, top_k=3):
    query = name + "," + country
    query_vec = model.encode([query], convert_to_numpy=True)
    distances, indices = index.search(query_vec, top_k)

    results = data.iloc[indices[0]].copy()
    results["similarity_score"] = 1 / (1 + distances[0])  # data normalization
    results = results.sort_values(by="similarity_score", ascending=False)
    return results


if __name__ == "__main__":
    results = find_scandinavian_person("tord bsdk", "Amagerbrogade 88")
    print(results)
