from imports import (
    SQLModel, Field, Relationship,
    datetime, Optional, uuid
)

class OrganizationsCreate(SQLModel):
    name: str = Field(primary_key=True)
    description: Optional[str] = None
    
class Organizations(OrganizationsCreate, table=True):
    buildings: list["Buildings"] = Relationship(back_populates="organization")

class BuildingsCreate(SQLModel):
    name: str = Field(primary_key=True)
    description: Optional[str] = None
    organization_name: Optional[str] = Field(default=None, foreign_key="organizations.name")
    

class Buildings(BuildingsCreate, table=True):
    organization: Optional[Organizations] = Relationship(back_populates="buildings")
    cameras: list["Cameras"] = Relationship(back_populates="building")

class AICategories(SQLModel, table=True):
    name: str = Field(primary_key=True)
    description: Optional[str] = None
    ai_analytics: list["AIAnalytics"] = Relationship(back_populates="ai_category")

class AIAnalyticsCreate(SQLModel):
    name: str = Field(index=True)
    description: Optional[str] = None
    ai_category_name: Optional[str] = Field(default=None, foreign_key="aicategories.name")

class AIAnalytics(AIAnalyticsCreate, table=True):
    analytics_id:str = Field(primary_key=True, default_factory=lambda: str(uuid.uuid4()))
    created_at: Optional[datetime] = Field(default=datetime.utcnow())
    updated_at: Optional[datetime] = Field(default=datetime.utcnow())
    ai_category: Optional[AICategories] = Relationship(back_populates="ai_analytics")
    ai_jobs: list["AIJobs"] = Relationship(back_populates="ai_analytics")

class CamerasCreate(SQLModel):
    name: str = Field(index=True)
    cam_url: str = Field(unique=True)
    description: Optional[str] = None
    building_name: Optional[str] = Field(default=None, foreign_key="buildings.name")

class Cameras(CamerasCreate, table=True):
    cam_id: str = Field(primary_key=True, default_factory=lambda: str(uuid.uuid4()))
    created_at: Optional[datetime] = Field(default=datetime.utcnow())
    updated_at: Optional[datetime] = Field(default=datetime.utcnow())
    building: Optional[Buildings] = Relationship(back_populates="cameras")
    ai_jobs: list["AIJobs"] = Relationship(back_populates="camera")

class AIJobsCreate(SQLModel):
    analytics_id: str = Field(default=None, foreign_key="aianalytics.analytics_id", primary_key=True)
    cam_id: str = Field(default=None, foreign_key="cameras.cam_id", primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    
class AIJobs(AIJobsCreate, table=True):
    job_id: str = Field(primary_key=True, default_factory=lambda: str(uuid.uuid4()))
    created_at: Optional[datetime] = Field(default=datetime.utcnow())
    updated_at: Optional[datetime] = Field(default=datetime.utcnow())
    ai_analytics: Optional[AIAnalytics] = Relationship(back_populates="ai_jobs")
    camera: Optional[Cameras] = Relationship(back_populates="ai_jobs")






