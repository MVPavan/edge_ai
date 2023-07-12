from eai_core_api.imports import (
    APIRouter, Depends, Session, HTTPException
)

from ..database.manage import get_pgdb_session
from ..database import tables as schemas
from ..database import crud


ai_router = APIRouter()


@ai_router.post("/ai_categories/", response_model=schemas.AICategories, tags=["AI Categories"])
def create_ai_category(ai_category: schemas.AICategories, db: Session = Depends(get_pgdb_session)):
    db_ai_category = crud.create_ai_category(db, ai_category)
    return db_ai_category

@ai_router.get("/ai_categories/{name}", response_model=schemas.AICategories, tags=["AI Categories"])
def read_ai_category(name: str, db: Session = Depends(get_pgdb_session)):
    db_ai_category = crud.get_ai_category(db, name=name)
    if db_ai_category is None:
        raise HTTPException(status_code=404, detail="AI category not found")
    return db_ai_category

@ai_router.get("/ai_categories/", response_model=list[schemas.AICategories], tags=["AI Categories"])
def read_ai_categories(skip: int = 0, limit: int = 100, db: Session = Depends(get_pgdb_session)):
    ai_categories = crud.get_ai_categories(db, skip=skip, limit=limit)
    return ai_categories

@ai_router.put("/ai_categories/{name}", response_model=schemas.AICategories, tags=["AI Categories"])
def update_ai_category(name: str, ai_category: schemas.AICategories, db: Session = Depends(get_pgdb_session)):
    db_ai_category = crud.get_ai_category(db, name=name)
    if db_ai_category is None:
        raise HTTPException(status_code=404, detail="AI category not found")
    db_ai_category = crud.update_ai_category(db, name=name, ai_category=ai_category)
    return db_ai_category

@ai_router.delete("/ai_categories/{name}", response_model=schemas.AICategories, tags=["AI Categories"])
def delete_ai_category(name: str, db: Session = Depends(get_pgdb_session)):
    db_ai_category = crud.get_ai_category(db, name=name)
    if db_ai_category is None:
        raise HTTPException(status_code=404, detail="AI category not found")
    db_ai_category = crud.delete_ai_category(db, name=name)
    return db_ai_category



# AI Analytics routes

@ai_router.post("/ai_analytics/", response_model=schemas.AIAnalytics, tags=["AI Analytics"])
def create_ai_analytics(ai_analytics: schemas.AIAnalyticsCreate, db: Session = Depends(get_pgdb_session)):
    db_ai_analytics = crud.create_ai_analytics(db, ai_analytics)
    return db_ai_analytics

@ai_router.get("/ai_analytics/{analytics_id}", response_model=schemas.AIAnalytics, tags=["AI Analytics"])
def read_ai_analytics(analytics_id: str, db: Session = Depends(get_pgdb_session)):
    db_ai_analytics = crud.get_ai_analytics(db, analytics_id=analytics_id)
    if db_ai_analytics is None:
        raise HTTPException(status_code=404, detail="AI analytics not found")
    return db_ai_analytics

@ai_router.get("/ai_analytics/", response_model=list[schemas.AIAnalytics], tags=["AI Analytics"])
def read_all_ai_analytics(skip: int = 0, limit: int = 100, db: Session = Depends(get_pgdb_session)):
    ai_analytics = crud.get_all_ai_analytics(db, skip=skip, limit=limit)
    return ai_analytics

@ai_router.get("/ai_analytics/name/{name}", response_model=list[schemas.AIAnalytics], tags=["AI Analytics"])
def read_ai_analytics_by_name(name: str, db: Session = Depends(get_pgdb_session)):
    db_ai_analytics = crud.get_ai_analytics_by_name(db, name=name)
    if not db_ai_analytics:
        raise HTTPException(status_code=404, detail="AI analytics not found")
    return db_ai_analytics

@ai_router.get("/ai_analytics/category/{category_name}", response_model=list[schemas.AIAnalytics], tags=["AI Analytics"])
def read_ai_analytics_by_category(category_name: str, db: Session = Depends(get_pgdb_session)):
    db_ai_analytics = crud.get_ai_analytics_by_category(db, category_name=category_name)
    if not db_ai_analytics:
        raise HTTPException(status_code=404, detail="AI analytics not found")
    return db_ai_analytics

@ai_router.put("/ai_analytics/{analytics_id}", response_model=schemas.AIAnalytics, tags=["AI Analytics"])
def update_ai_analytics(analytics_id: str, ai_analytics: schemas.AIAnalyticsCreate, db: Session = Depends(get_pgdb_session)):
    db_ai_analytics = crud.get_ai_analytics(db, analytics_id=analytics_id)
    if db_ai_analytics is None:
        raise HTTPException(status_code=404, detail="AI analytics not found")
    db_ai_analytics = crud.update_ai_analytics(db, analytics_id=analytics_id, ai_analytics=ai_analytics)
    return db_ai_analytics

@ai_router.delete("/ai_analytics/{analytics_id}", response_model=schemas.AIAnalytics, tags=["AI Analytics"])
def delete_ai_analytics(analytics_id: str, db: Session = Depends(get_pgdb_session)):
    db_ai_analytics = crud.get_ai_analytics(db, analytics_id=analytics_id)
    if db_ai_analytics is None:
        raise HTTPException(status_code=404, detail="AI analytics not found")
    db_ai_analytics = crud.delete_ai_analytics(db, analytics_id=analytics_id)
    return db_ai_analytics


# AI Jobs routes

@ai_router.post("/ai_jobs/", response_model=schemas.AIJobs, tags=["AI Jobs"])
def create_ai_job(ai_job: schemas.AIJobsCreate, db: Session = Depends(get_pgdb_session)):
    db_ai_job = crud.create_ai_job(db, ai_job)
    return db_ai_job

@ai_router.get("/ai_jobs/{job_id}", response_model=schemas.AIJobs, tags=["AI Jobs"])
def read_ai_job(job_id: str, db: Session = Depends(get_pgdb_session)):
    db_ai_job = crud.get_ai_job(db, job_id=job_id)
    if db_ai_job is None:
        raise HTTPException(status_code=404, detail="AI job not found")
    return db_ai_job

@ai_router.get("/ai_jobs/", response_model=list[schemas.AIJobs], tags=["AI Jobs"])
def read_all_ai_jobs(skip: int = 0, limit: int = 100, db: Session = Depends(get_pgdb_session)):
    ai_jobs = crud.get_all_ai_jobs(db, skip=skip, limit=limit)
    return ai_jobs

@ai_router.get("/ai_jobs/name/{name}", response_model=list[schemas.AIJobs], tags=["AI Jobs"])
def read_ai_job_by_name(name: str, db: Session = Depends(get_pgdb_session)):
    db_ai_jobs = crud.get_ai_job_by_name(db, name=name)
    if not db_ai_jobs:
        raise HTTPException(status_code=404, detail="AI jobs not found")
    return db_ai_jobs

@ai_router.get("/ai_jobs/analytics/{analytics_id}", response_model=list[schemas.AIJobs], tags=["AI Jobs"])
def read_ai_job_by_ai_analytics(analytics_id: str, db: Session = Depends(get_pgdb_session)):
    db_ai_jobs = crud.get_ai_job_by_ai_analytics(db, analytics_id=analytics_id)
    if not db_ai_jobs:
        raise HTTPException(status_code=404, detail="AI jobs not found")
    return db_ai_jobs

@ai_router.get("/ai_jobs/camera/{cam_id}", response_model=list[schemas.AIJobs], tags=["AI Jobs"])
def read_ai_job_by_camera(cam_id: str, db: Session = Depends(get_pgdb_session)):
    db_ai_jobs = crud.get_ai_job_by_camera(db, cam_id=cam_id)
    if not db_ai_jobs:
        raise HTTPException(status_code=404, detail="AI jobs not found")
    return db_ai_jobs

@ai_router.put("/ai_jobs/{job_id}", response_model=schemas.AIJobs, tags=["AI Jobs"])
def update_ai_job(job_id: str, ai_job: schemas.AIJobsCreate, db: Session = Depends(get_pgdb_session)):
    db_ai_job = crud.get_ai_job(db, job_id=job_id)
    if db_ai_job is None:
        raise HTTPException(status_code=404, detail="AI job not found")
    db_ai_job = crud.update_ai_job(db, job_id=job_id, ai_job=ai_job)
    return db_ai_job

@ai_router.delete("/ai_jobs/{job_id}", response_model=schemas.AIJobs, tags=["AI Jobs"])
def delete_ai_job(job_id: str, db: Session = Depends(get_pgdb_session)):
    db_ai_job = crud.get_ai_job(db, job_id=job_id)
    if db_ai_job is None:
        raise HTTPException(status_code=404, detail="AI job not found")
    db_ai_job = crud.delete_ai_job(db, job_id=job_id)
    return db_ai_job


