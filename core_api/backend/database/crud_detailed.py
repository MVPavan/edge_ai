from imports import (
    Session, select
)
from .tables import (
    Organizations, OrganizationsCreate,
    Buildings, BuildingsCreate,
    AICategories,
    AIAnalytics, AIAnalyticsCreate,
    Cameras, CamerasCreate
)

# Organizations CRUD


def create_organization(db: Session, organization: OrganizationsCreate) -> Organizations:
    db_organization = Organizations(**organization.dict())
    db.add(db_organization)
    db.commit()
    db.refresh(db_organization)
    return db_organization

def get_organization(db: Session, name: str) -> Organizations:
    return db.query(Organizations).filter(Organizations.name == name).first()

def get_organizations(db: Session, skip: int = 0, limit: int = 100) -> list[Organizations]:
    return db.query(Organizations).offset(skip).limit(limit).all()

def update_organization(db: Session, name: str, organization: OrganizationsCreate) -> Organizations:
    db_organization = get_organization(db, name)
    if db_organization:
        update_data = organization.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_organization, key, value)
        db.add(db_organization)
        db.commit()
        db.refresh(db_organization)
        return db_organization

def delete_organization(db: Session, name: str) -> Organizations:
    db_organization = get_organization(db, name)
    if db_organization:
        db.delete(db_organization)
        db.commit()
        return db_organization

# Buildings CRUD

def create_building(db: Session, building: BuildingsCreate) -> Buildings:
    db_building = Buildings(**building.dict())
    db.add(db_building)
    db.commit()
    db.refresh(db_building)
    return db_building

def get_building(db: Session, name: str) -> Buildings:
    return db.query(Buildings).filter(Buildings.name == name).first()

def get_buildings(db: Session, skip: int = 0, limit: int = 100) -> list[Buildings]:
    return db.query(Buildings).offset(skip).limit(limit).all()

def update_building(db: Session, name: str, building: BuildingsCreate) -> Buildings:
    db_building = get_building(db, name)
    if db_building:
        update_data = building.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_building, key, value)
        db.add(db_building)
        db.commit()
        db.refresh(db_building)
        return db_building

def delete_building(db: Session, name: str) -> Buildings:
    db_building = get_building(db, name)
    if db_building:
        db.delete(db_building)
        db.commit()
        return db_building

# AICategories CRUD

def create_ai_category(db: Session, ai_category: AICategories) -> AICategories:
    db_ai_category = AICategories(**ai_category.dict())
    db.add(db_ai_category)
    db.commit()
    db.refresh(db_ai_category)
    return db_ai_category

def get_ai_category(db: Session, name: str) -> AICategories:
    return db.query(AICategories).filter(AICategories.name == name).first()

def get_ai_categories(db: Session, skip: int = 0, limit: int = 100) -> list[AICategories]:
    return db.query(AICategories).offset(skip).limit(limit).all()

def update_ai_category(db: Session, name: str, ai_category: AICategories) -> AICategories:
    db_ai_category = get_ai_category(db, name)
    if db_ai_category:
        update_data = ai_category.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_ai_category, key, value)
        db.add(db_ai_category)
        db.commit()
        db.refresh(db_ai_category)
        return db_ai_category

def delete_ai_category(db: Session, name: str) -> AICategories:
    db_ai_category = get_ai_category(db, name)
    if db_ai_category:
        db.delete(db_ai_category)
        db.commit()
        return db_ai_category

# AIAnalytics CRUD

def create_ai_analytics(db: Session, ai_analytics: AIAnalyticsCreate) -> AIAnalytics:
    db_ai_analytics = AIAnalytics(**ai_analytics.dict())
    db.add(db_ai_analytics)
    db.commit()
    db.refresh(db_ai_analytics)
    return db_ai_analytics

def get_ai_analytics(db: Session, ai_id: str) -> AIAnalytics:
    return db.query(AIAnalytics).filter(AIAnalytics.ai_id == ai_id).first()

def get_ai_analytics_by_name(db: Session, name: str) -> list[AIAnalytics]:
    return db.query(AIAnalytics).filter(AIAnalytics.name == name).all()

def get_ai_analytics_by_category(db: Session, category_name: str) -> list[AIAnalytics]:
    return db.query(AIAnalytics).join(AIAnalytics.ai_category).filter(AICategories.name == category_name).all()

def get_all_ai_analytics(db: Session, skip: int = 0, limit: int = 100) -> list[AIAnalytics]:
    return db.query(AIAnalytics).offset(skip).limit(limit).all()

def update_ai_analytics(db: Session, ai_id: str, ai_analytics: AIAnalyticsCreate) -> AIAnalytics:
    db_ai_analytics = get_ai_analytics(db, ai_id)
    if db_ai_analytics:
        update_data = ai_analytics.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_ai_analytics, key, value)
        db.add(db_ai_analytics)
        db.commit()
        db.refresh(db_ai_analytics)
        return db_ai_analytics

def delete_ai_analytics(db: Session, ai_id: str) -> AIAnalytics:
    db_ai_analytics = get_ai_analytics(db, ai_id)
    if db_ai_analytics:
        db.delete(db_ai_analytics)
        db.commit()
        return db_ai_analytics

# Cameras CRUD

def create_camera(db: Session, camera: CamerasCreate) -> Cameras:
    db_camera = Cameras(**camera.dict())
    db.add(db_camera)
    db.commit()
    db.refresh(db_camera)
    return db_camera

def get_camera(db: Session, cam_id: str) -> Cameras:
    return db.query(Cameras).filter(Cameras.cam_id == cam_id).first()

def get_camera_by_name(db: Session, name: str) -> list[Cameras]:
    return db.query(Cameras).filter(Cameras.name == name).all()

def get_camera_by_building(db: Session, building_name: str) -> list[Cameras]:
    return db.query(Cameras).join(Cameras.building).filter(Buildings.name == building_name).all()

def get_all_cameras(db: Session, skip: int = 0, limit: int = 100) -> list[Cameras]:
    return db.query(Cameras).offset(skip).limit(limit).all()

def update_camera(db: Session, cam_id: str, camera: CamerasCreate) -> Cameras:
    db_camera = get_camera(db, cam_id)
    if db_camera:
        update_data = camera.dict(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_camera, key, value)
        db.add(db_camera)
        db.commit()
        db.refresh(db_camera)
        return db_camera

def delete_camera(db: Session, cam_id: str) -> Cameras:
    db_camera = get_camera(db, cam_id)
    if db_camera:
        db.delete(db_camera)
        db.commit()
        return db_camera