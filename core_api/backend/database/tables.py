from imports import (
    SQLModel, Field, Relationship,
    datetime, Optional
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


class Cameras(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    cam_url: str
    description: Optional[str] = None
    building_name: Optional[str] = Field(default=None, foreign_key="buildings.name")
    building: Optional[Buildings] = Relationship(back_populates="cameras")
    created_at: Optional[datetime] = Field(default=datetime.utcnow())
    updated_at: Optional[datetime] = Field(default=datetime.utcnow())