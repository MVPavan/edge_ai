from imports import Session
from .tables import (
    Organizations, OrganizationsCreate,
    Buildings, BuildingsCreate,
    AICategories,
    AIAnalytics, AIAnalyticsCreate,
    Cameras, CamerasCreate,
    AIJobs, AIJobsCreate
)

# Common CRUD functions

def create(db: Session, table:object, model: object) -> object:
    """
    Create a new record in the database.

    Args:
    - db: SQLAlchemy session object
    - table: SQLAlchemy table object
    - model: Pydantic model object

    Returns:
    - The created record
    """
    db_model = table(**model.dict())
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model

def get_by_col(db: Session, model: object, col_name:str, col_value: str, many=False) -> object:
    """
    Get a record from the database by a column value.

    Args:
    - db: SQLAlchemy session object
    - model: SQLAlchemy table object
    - col_name: Name of the column to filter by
    - col_value: Value of the column to filter by
    - many: Whether to return a single record or a list of records

    Returns:
    - The record(s) matching the filter criteria
    """
    if not many:
        return db.query(model).filter(model.__dict__[col_name] == col_value).first()
    else:
        return db.query(model).filter(model.__dict__[col_name] == col_value).all()


def get_all(db: Session, model: object, skip: int = 0, limit: int = 100) -> list[object]:
    """
    Get all records from the database.

    Args:
    - db: SQLAlchemy session object
    - model: SQLAlchemy table object
    - skip: Number of records to skip
    - limit: Maximum number of records to return

    Returns:
    - A list of all records in the table
    """
    return db.query(model).offset(skip).limit(limit).all()

def update(db: Session, model: object, col_name:str, col_value: str, update_data: dict) -> object:
    """
    Update a record in the database.

    Args:
    - db: SQLAlchemy session object
    - model: SQLAlchemy table object
    - col_name: Name of the column to filter by
    - col_value: Value of the column to filter by
    - update_data: Dictionary containing the updated data

    Returns:
    - The updated record
    """
    db_model = get_by_col(db, model, col_name, col_value)
    if db_model:
        for key, value in update_data.items():
            setattr(db_model, key, value)
        db.add(db_model)
        db.commit()
        db.refresh(db_model)
        return db_model

def delete(db: Session, model: object, col_name:str, col_value: str) -> object:
    """
    Delete a record from the database.

    Args:
    - db: SQLAlchemy session object
    - model: SQLAlchemy table object
    - col_name: Name of the column to filter by
    - col_value: Value of the column to filter by

    Returns:
    - The deleted record
    """
    db_model = get_by_col(db, model, col_name, col_value)
    if db_model:
        db.delete(db_model)
        db.commit()
        return db_model



# Organizations CRUD

def create_organization(db: Session, organization: OrganizationsCreate) -> Organizations:
    return create(db, Organizations, organization)

def get_organization(db: Session, name: str) -> Organizations:
    return get_by_col(db, Organizations, col_name="name", col_value=name)

def get_organizations(db: Session, skip: int = 0, limit: int = 100) -> list[Organizations]:
    return get_all(db, Organizations, skip, limit)

def update_organization(db: Session, name: str, organization: OrganizationsCreate) -> Organizations:
    return update(
        db, Organizations, col_name="name", col_value=name, 
        update_data=organization.dict(exclude_unset=True)
    )

def delete_organization(db: Session, name: str) -> Organizations:
    return delete(db, Organizations, col_name="name", col_value=name)

# Buildings CRUD

def create_building(db: Session, building: BuildingsCreate) -> Buildings:
    return create(db, Buildings, building)

def get_building(db: Session, name: str) -> Buildings:
    return get_by_col(db, Buildings, col_name="name", col_value=name)

def get_buildings(db: Session, skip: int = 0, limit: int = 100) -> list[Buildings]:
    return get_all(db, Buildings, skip, limit)

def update_building(db: Session, name: str, building: BuildingsCreate) -> Buildings:
    return update(
        db, Buildings, col_name="name", col_value=name, 
        update_data=building.dict(exclude_unset=True)
    )

def delete_building(db: Session, name: str) -> Buildings:
    return delete(db, Buildings, col_name="name", col_value=name)

# AICategories CRUD

def create_ai_category(db: Session, ai_category: AICategories) -> AICategories:
    return create(db, AICategories, ai_category)

def get_ai_category(db: Session, name: str) -> AICategories:
    return get_by_col(db, AICategories, col_name="name", col_value=name)

def get_ai_categories(db: Session, skip: int = 0, limit: int = 100) -> list[AICategories]:
    return get_all(db, AICategories, skip, limit)

def update_ai_category(db: Session, name: str, ai_category: AICategories) -> AICategories:
    return update(
        db, AICategories, col_name="name", col_value=name, 
        update_data=ai_category.dict(exclude_unset=True)
    )

def delete_ai_category(db: Session, name: str) -> AICategories:
    return delete(db, AICategories, col_name="name", col_value=name)

# AIAnalytics CRUD

def create_ai_analytics(db: Session, ai_analytics: AIAnalyticsCreate) -> AIAnalytics:
    return create(db, AIAnalytics, ai_analytics)

def get_ai_analytics(db: Session, analytics_id: str) -> AIAnalytics:
    return get_by_col(db, AIAnalytics, col_name="analytics_id", col_value=analytics_id)

def get_ai_analytics_by_name(db: Session, name: str) -> list[AIAnalytics]:
    return get_by_col(db, AIAnalytics, col_name="name", col_value=name, many=True)

def get_ai_analytics_by_category(db: Session, category_name: str) -> list[AIAnalytics]:
    return db.query(AIAnalytics).join(AIAnalytics.ai_category).filter(AICategories.name == category_name).all()

def get_all_ai_analytics(db: Session, skip: int = 0, limit: int = 100) -> list[AIAnalytics]:
    return get_all(db, AIAnalytics, skip, limit)

def update_ai_analytics(db: Session, analytics_id: str, ai_analytics: AIAnalyticsCreate) -> AIAnalytics:
    return update(db, AIAnalytics, col_name="analytics_id", col_value=analytics_id, 
        update_data=ai_analytics.dict(exclude_unset=True)
    )

def delete_ai_analytics(db: Session, analytics_id: str) -> AIAnalytics:
    return delete(db, AIAnalytics, col_name="analytics_id", col_value=analytics_id)

# Cameras CRUD

def create_camera(db: Session, camera: CamerasCreate) -> Cameras:
    return create(db, Cameras, camera)

def get_camera(db: Session, cam_id: str) -> Cameras:
    return get_by_col(db, Cameras, col_name="cam_id", col_value=cam_id)

def get_camera_by_url(db: Session, cam_url: str) -> Cameras:
    return get_by_col(db, Cameras, col_name="cam_url", col_value=cam_url)

def get_camera_by_name(db: Session, name: str) -> list[Cameras]:
    return get_by_col(db, Cameras, col_name="name", col_value=name, many=True)

def get_camera_by_building(db: Session, building_name: str) -> list[Cameras]:
    return db.query(Cameras).join(Cameras.building).filter(Buildings.name == building_name).all()

def get_all_cameras(db: Session, skip: int = 0, limit: int = 100) -> list[Cameras]:
    return get_all(db, Cameras, skip, limit)

def update_camera(db: Session, cam_id: str, camera: CamerasCreate) -> Cameras:
    return update(db, Cameras, col_name="cam_id", col_value=cam_id, 
        update_data=camera.dict(exclude_unset=True)
    )

def delete_camera(db: Session, cam_id: str) -> Cameras:
    return delete(db, Cameras, col_name="cam_id", col_value=cam_id)


# AIJobs CRUD

def create_ai_job(db: Session, ai_job: AIJobsCreate) -> AIJobs:
    return create(db, AIJobs, ai_job)

def get_ai_job(db: Session, job_id: str) -> AIJobs:
    return get_by_col(db, AIJobs, col_name="job_id", col_value=job_id)

def get_ai_job_by_name(db: Session, name: str) -> list[AIJobs]:
    return get_by_col(db, AIJobs, col_name="name", col_value=name, many=True)

def get_ai_job_by_ai_analytics(db: Session, analytics_id: str) -> list[AIJobs]:
    return db.query(AIJobs).join(AIJobs.ai_analytics).filter(AIAnalytics.analytics_id == analytics_id).all()

def get_ai_job_by_camera(db: Session, cam_id: str) -> list[AIJobs]:
    return db.query(AIJobs).join(AIJobs.camera).filter(Cameras.cam_id == cam_id).all()

def get_all_ai_jobs(db: Session, skip: int = 0, limit: int = 100) -> list[AIJobs]:
    return get_all(db, AIJobs, skip, limit)

def update_ai_job(db: Session, job_id: str, ai_job: AIJobsCreate) -> AIJobs:
    return update(db, AIJobs, col_name="job_id", col_value=job_id, 
        update_data=ai_job.dict(exclude_unset=True)
    )

def delete_ai_job(db: Session, job_id: str) -> AIJobs:
    return delete(db, AIJobs, col_name="job_id", col_value=job_id)