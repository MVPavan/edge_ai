from imports import (
    SQLModel, Field, Relationship,
    datetime, Optional, list
)

class Organizations(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    buildings: list["Buildings"] = Relationship(back_populates="organization")


class Buildings(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    organization_id: Optional[int] = Field(default=None, foreign_key="organization.id")
    organization: Optional[Organizations] = Relationship(back_populates="buildings")
    cameras: list["Cameras"] = Relationship(back_populates="building")


class Cameras(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    cam_url: str
    description: Optional[str] = None
    building_id: Optional[int] = Field(default=None, foreign_key="buildings.id")
    building: Optional[Buildings] = Relationship(back_populates="cameras")
    created_at: Optional[datetime] = Field(default=datetime.utcnow())
    updated_at: Optional[datetime] = Field(default=datetime.utcnow())