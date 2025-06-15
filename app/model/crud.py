import json
from app.model import models, schemas, database
from fastapi import HTTPException
from sqlalchemy.orm import Session


models.Base.metadata.create_all(bind=database.engine)


def create_ai_entry(payload: schemas.AISimilaritySearchBase):
    db: Session = database.SessionLocal()
    try:
        existing = db.query(models.AISimilaritySearch).filter_by(id=payload.id).first()
        if existing:
            raise HTTPException(
                status_code=400, detail="Entry with given ID already exists"
            )
        print("payload", payload)
        new_entry = models.AISimilaritySearch(
            id=payload.id,
            fullname=payload.fullname,
            country=payload.country,
            generatedlist="[]",
        )
        print("new_entry", new_entry)
        db.add(new_entry)
        db.commit()
        db.refresh(new_entry)
        return new_entry
    finally:
        db.close()


def update_generated_list(entry_id: int, generatedlist: str):
    db: Session = database.SessionLocal()
    try:
        entry = db.query(models.AISimilaritySearch).filter_by(id=entry_id).first()
        if not entry:
            raise HTTPException(status_code=404, detail="Entry not found")

        entry.generatedlist = json.dumps(generatedlist)
        db.commit()
        db.refresh(entry)
        return entry
    finally:
        db.close()


def get_all_ai_entries():
    db: Session = database.SessionLocal()
    try:
        return db.query(models.AISimilaritySearch).all()
    finally:
        db.close()
