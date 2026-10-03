from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import Review
from app.schemas.schemas import ReviewCreate, ReviewOut

router = APIRouter(prefix="/reviews")

@router.post("", response_model=ReviewOut)
def create_review(rev_in: ReviewCreate, db: Session = Depends(get_db)):
    existing = db.query(Review).filter(Review.review_id == rev_in.review_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Review {rev_in.review_id} already exists")
    rev = Review(**rev_in.model_dump())
    db.add(rev)
    db.commit()
    db.refresh(rev)
    return rev

@router.get("", response_model=List[ReviewOut])
def list_reviews(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(Review).order_by(Review.timestamp.desc()).limit(limit).all()

@router.get("/{review_id}", response_model=ReviewOut)
def get_review(review_id: str, db: Session = Depends(get_db)):
    rev = db.query(Review).filter(Review.review_id == review_id).first()
    if not rev:
        raise HTTPException(status_code=404, detail=f"Review {review_id} not found")
    return rev

@router.get("/by-pr/{pr_id}", response_model=List[ReviewOut])
def get_reviews_by_pr(pr_id: str, db: Session = Depends(get_db)):
    return db.query(Review).filter(Review.pr_id == pr_id).all()
