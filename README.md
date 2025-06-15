# LeedFlow - FastAPI App with Celery and Docker

## 🚀 Setup Instructions

### 🔧 Build the Docker Image

```bash
docker build -t leedflow .
```

> ⚠️ This may take 7–10 minutes on the first build due to dependency installation.

### 🐳 Start the Containers

```bash
docker-compose up -d
```

> This starts the FastAPI server and Celery worker. You are good to go now!

---

## 🌐 Access the API

Visit Swagger docs in your browser:

```
http://localhost:8001/docs
```

---

## 🧠 API Endpoints Summary

| POST| `/predicted_names/vector_search` | Perform vector similarity search |
| GET | `/predicted_names/vector_search/{job_id}` | Get vector search results by job ID  
| GET | `/predicted_names/vector_search/history` | Retrieve history of predictions |
| POST| `/predicted_names/claude_predictions` | Get name suggestions from Claude AI |
| POST| `/predicted_names/rule_based_predictions` | Get rule-based name transliterations |

---

## 📝 Notes

-   Ensure port `8001` (FastAPI) is open and accessible.
-   Make sure your Celery broker (e.g., Redis) is configured and running.
-   You can customize the concurrency level of Celery workers via the `--concurrency` flag.
-   add ANTHROPIC_API_KEY in env file to use claude predictions.
-   **Dataset Configuration**:  
    Replace the contents of `dataset.json` with any file of your choice. For better results, use data in the following format:

```json
[
    {
        "name": "Oskar Svensson",
        "country": "Sweden"
    }
]
```

```

```
