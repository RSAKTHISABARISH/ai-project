from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import PullRequest
from app.schemas.schemas import PullRequestCreate, PullRequestOut

router = APIRouter(prefix="/pull-requests")

@router.post("", response_model=PullRequestOut)
def create_pull_request(pr_in: PullRequestCreate, db: Session = Depends(get_db)):
    existing = db.query(PullRequest).filter(PullRequest.pr_id == pr_in.pr_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"PR {pr_in.pr_id} already exists")
    pr = PullRequest(**pr_in.model_dump())
    db.add(pr)
    db.commit()
    db.refresh(pr)
    return pr

@router.get("", response_model=List[PullRequestOut])
def list_pull_requests(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(PullRequest).order_by(PullRequest.created_at.desc()).limit(limit).all()

@router.get("/{pr_id}", response_model=PullRequestOut)
def get_pull_request(pr_id: str, db: Session = Depends(get_db)):
    pr = db.query(PullRequest).filter(PullRequest.pr_id == pr_id).first()
    if not pr:
        raise HTTPException(status_code=404, detail=f"Pull Request {pr_id} not found")
    return pr
