from fastapi import APIRouter
from app.api.events import router as events_router
from app.api.incidents import router as incidents_router
from app.api.pull_requests import router as pr_router
from app.api.diffs import router as diffs_router
from app.api.reviews import router as reviews_router
from app.api.runbooks import router as runbooks_router
from app.api.approvals import router as approvals_router
from app.api.metrics import router as metrics_router
from app.api.demo import router as demo_router

api_router = APIRouter()

api_router.include_router(events_router, tags=["Events"])
api_router.include_router(incidents_router, tags=["Incidents"])
api_router.include_router(pr_router, tags=["Pull Requests"])
api_router.include_router(diffs_router, tags=["Code Diffs"])
api_router.include_router(reviews_router, tags=["Reviews"])
api_router.include_router(runbooks_router, tags=["Runbooks"])
api_router.include_router(approvals_router, tags=["Approvals"])
api_router.include_router(metrics_router, tags=["Metrics"])
api_router.include_router(demo_router, tags=["Demo"])
