from imports import (
    SQLModel, Field, Relationship,
    datetime, Optional, uuid
)

class Organizations(SQLModel, table=True):
    name: str = Field(primary_key=True)
    description: Optional[str] = None
    buildings: list["Buildings"] = Relationship(back_populates="organization")

# create uniqueness constraint on name and organization_id
class Buildings(SQLModel, table=True):
    name: str = Field(primary_key=True)
    description: Optional[str] = None
    organization_name: Optional[str] = Field(default=None, foreign_key="organizations.name")
    organization: Optional[Organizations] = Relationship(back_populates="buildings")
    cameras: list["Cameras"] = Relationship(back_populates="building")

class AICategories(SQLModel, table=True):
    name: str = Field(primary_key=True)
    description: Optional[str] = None
    ai_analytics: list["AIAnalytics"] = Relationship(back_populates="ai_category")

class AIAnalyticsCamerasLink(SQLModel, table=True):
    ai_id: str = Field(default=None, foreign_key="aianalytics.ai_id", primary_key=True)
    cam_id: str = Field(default=None, foreign_key="cameras.cam_id", primary_key=True)


class AIAnalytics(SQLModel, table=True):
    ai_id:str = Field(primary_key=True, default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(index=True)
    description: Optional[str] = None
    created_at: Optional[datetime] = Field(default=datetime.utcnow())
    updated_at: Optional[datetime] = Field(default=datetime.utcnow())
    ai_category_name: Optional[str] = Field(default=None, foreign_key="aicategories.name")
    ai_category: Optional[AICategories] = Relationship(back_populates="ai_analytics")
    cameras: list["Cameras"] = Relationship(
        link_model=AIAnalyticsCamerasLink,
        back_populates="ai_analytics"
    )

class Cameras(SQLModel, table=True):
    cam_id: str = Field(primary_key=True, default_factory=lambda: str(uuid.uuid4()))
    name: str = Field(index=True)
    cam_url: str = Field(unique=True)
    description: Optional[str] = None
    created_at: Optional[datetime] = Field(default=datetime.utcnow())
    updated_at: Optional[datetime] = Field(default=datetime.utcnow())
    building_name: Optional[str] = Field(default=None, foreign_key="buildings.name")
    building: Optional[Buildings] = Relationship(back_populates="cameras")
    ai_analytics: list["AIAnalytics"] = Relationship(
        link_model=AIAnalyticsCamerasLink,
        back_populates="cameras"
    )