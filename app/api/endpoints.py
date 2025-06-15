from enum import Enum
from multiprocessing.pool import AsyncResult
from app.handler.claude_predictions import suggest_names

# from app.handler.vector_similarity_search import find_scandinavian_person
from app.model import models, schemas
from app.model.crud import create_ai_entry, get_all_ai_entries, update_generated_list
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from app.handler.rule_based_prediction import transliterate_names
from vector1 import find_scandinavian_person
from vector1 import celery_app

router = APIRouter()


class ScandinavianCountry(str, Enum):
    Norway = "Norway"
    Sweden = "Sweden"
    Denmark = "Denmark"
    Iceland = "Iceland"
    FaroeIslands = "FaroeIslands"


class NameRequest(BaseModel):
    full_name: str
    country_code: ScandinavianCountry
    enable_fuzzy_search: bool = False


class NameRequestClaude(BaseModel):
    full_name: str
    country_code: ScandinavianCountry


class NameResponse(BaseModel):
    predicted_names: List[str]


@router.post("/predicted_names/rule_based", response_model=NameResponse)
async def get_predicted_names(params: NameRequest):
    print("params", params)
    try:
        predicted_names = transliterate_names(
            params.full_name, params.country_code, params.enable_fuzzy_search
        )
        print("predicted_names", predicted_names)

        return NameResponse(predicted_names=predicted_names)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predicted_names/claude")
async def get_predicted_names(params: NameRequestClaude):
    print("params", params)
    try:
        predicted_names = suggest_names(params.full_name, params.country_code)
        print("predicted_names", predicted_names)
        return NameResponse(predicted_names=predicted_names)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/predicted_names/vector_search")
async def get_predicted_names_vector(params: NameRequest):
    try:
        print("paramsqq", params)
        job = find_scandinavian_person.delay(params.full_name, params.country_code)
        create_ai_entry(
            schemas.AISimilaritySearchBase(
                id=job.id,
                fullname=params.full_name,
                country=params.country_code.value,
            )
        )
        print("job", job)
        return {"job_id": job.id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predicted_names/vector_search/{job_id}")
async def get_job_results(job_id: str):
    try:
        result = celery_app.AsyncResult(job_id)

        if result.successful():
            results = result.get()
            update_generated_list(job_id, results)
            return {
                "status": "completed",
                "result": results,  # <-- Fix here
            }
        elif result.state == "PENDING":
            return {"status": f"Task {job_id} is pending"}
        elif result.state == "FAILURE":
            return {
                "status": f"Task {job_id} failed",
                "error": str(result.info),  # better than result.get(propagate=False)
            }
        else:
            return {"status": f"Task {job_id} not completed yet, state: {result.state}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/vector_search/history")
async def get_job_history():
    try:
        return get_all_ai_entries()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
