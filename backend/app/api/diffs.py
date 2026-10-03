from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.models.models import CodeDiff
from app.schemas.schemas import CodeDiffCreate, CodeDiffOut

router = APIRouter(prefix="/diffs")

@router.post("", response_model=CodeDiffOut)
def create_diff(diff_in: CodeDiffCreate, db: Session = Depends(get_db)):
    existing = db.query(CodeDiff).filter(CodeDiff.diff_id == diff_in.diff_id).first()
    if existing:
        raise HTTPException(status_code=400, detail=f"Diff {diff_in.diff_id} already exists")
    diff = CodeDiff(**diff_in.model_dump())
    db.add(diff)
    db.commit()
    db.refresh(diff)
    return diff

@router.get("", response_model=List[CodeDiffOut])
def list_diffs(limit: int = 50, db: Session = Depends(get_db)):
    return db.query(CodeDiff).limit(limit).all()

@router.get("/{diff_id}", response_model=CodeDiffOut)
def get_diff(diff_id: str, db: Session = Depends(get_db)):
    diff = db.query(CodeDiff).filter(CodeDiff.diff_id == diff_id).first()
    if not diff:
        raise HTTPException(status_code=404, detail=f"Code Diff {diff_id} not found")
    return diff

@router.get("/by-pr/{pr_id}", response_model=CodeDiffOut)
def get_diff_by_pr(pr_id: str, db: Session = Depends(get_db)):
    diff = db.query(CodeDiff).filter(CodeDiff.pr_id == pr_id).first()
    if not diff:
        raise HTTPException(status_code=404, detail=f"Code Diff for PR {pr_id} not found")
    return diff
