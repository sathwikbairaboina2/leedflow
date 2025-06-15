from sqlalchemy import Column, Integer, String, Text
from app.model.database import Base


class AISimilaritySearch(Base):
    __tablename__ = "AIsimilaritysearch"

    id = Column(String, primary_key=True, index=True)
    fullname = Column(String, nullable=False)
    country = Column(String, nullable=False)
    generatedlist = Column(Text)
