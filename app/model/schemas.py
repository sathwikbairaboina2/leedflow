from pydantic import BaseModel
from typing import Optional


class AISimilaritySearchBase(BaseModel):
    id: str
    fullname: str
    country: str
    generatedlist: Optional[str] = None  # <-- Changed to str


class AISimilaritySearchResponse(AISimilaritySearchBase):
    class Config:
        from_attributes = True
