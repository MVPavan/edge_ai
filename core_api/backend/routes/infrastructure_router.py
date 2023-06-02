from imports import (
    APIRouter, Depends
)

from ..database.manage import get_pgdb_session

orders_api_router = APIRouter()


# @orders_api_router.post("/organizations/", response_model=order_crud_consts.OrderResponse)
# def modify_order(_order: order_crud_consts.ModifyOrder):
#     response = order_funcs.modify_order(_order)
#     return response


# @orders_api_router.post("/buildings/", response_model=order_crud_consts.OrderResponse)
# def cancel_order(_order: order_crud_consts.CancelOrder):
#     response = order_funcs.cancel_order(_order)
#     return response


# @orders_api_router.get("/cameras/", response_model=consolidated_consts.OrdersRead)
# def order_history(_order_id: str = None):
#     response = order_funcs.order_history(_order_id)
#     return response


infra_router = APIRouter()



@infra_router.post("/organizations/", response_model=schemas.Organizations)
def create_organization(organization: schemas.OrganizationsCreate, db: Session = Depends(get_pgdb_session)):
    db_organization = crud.get_organization_by_name(db, name=organization.name)
    if db_organization:
        raise HTTPException(status_code=400, detail="Organization already exists")
    return crud.create_organization(db=db, organization=organization)

@infra_router.get("/organizations/", response_model=List[schemas.Organizations])
def read_organizations(skip: int = 0, limit: int = 100, db: Session = Depends(get_pgdb_session)):
    organizations = crud.get_organizations(db, skip=skip, limit=limit)
    return organizations

@infra_router.get("/organizations/{organization_id}", response_model=schemas.Organizations)
def read_organization(organization_id: str, db: Session = Depends(get_pgdb_session)):
    db_organization = crud.get_organization(db, organization_id=organization_id)
    if db_organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return db_organization

@infra_router.put("/organizations/{organization_id}", response_model=schemas.Organizations)
def update_organization(organization_id: str, organization: schemas.OrganizationsCreate, db: Session = Depends(get_pgdb_session)):
    db_organization = crud.get_organization(db, organization_id=organization_id)
    if db_organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    return crud.update_organization(db=db, organization=organization, db_organization=db_organization)

@infra_router.delete("/organizations/{organization_id}")
def delete_organization(organization_id: str, db: Session = Depends(get_pgdb_session)):
    db_organization = crud.get_organization(db, organization_id=organization_id)
    if db_organization is None:
        raise HTTPException(status_code=404, detail="Organization not found")
    crud.delete_organization(db=db, db_organization=db_organization)
    return {"message": "Organization deleted"}

@infra_router.post("/buildings/", response_model=schemas.Buildings)
def create_building(building: schemas.BuildingsCreate, db: Session = Depends(get_pgdb_session)):
    db_building = crud.get_building_by_name(db, name=building.name)
    if db_building:
        raise HTTPException(status_code=400, detail="Building already exists")
    return crud.create_building(db=db, building=building)

@infra_router.get("/buildings/", response_model=List[schemas.Buildings])
def read_buildings(skip: int = 0, limit: int = 100, db: Session = Depends(get_pgdb_session)):
    buildings = crud.get_buildings(db, skip=skip, limit=limit)
    return buildings

@infra_router.get("/buildings/{building_id}", response_model=schemas.Buildings)
def read_building(building_id: str, db: Session = Depends(get_pgdb_session)):
    db_building = crud.get_building(db, building_id=building_id)
    if db_building is None:
        raise HTTPException(status_code=404, detail="Building not found")
    return db_building

@infra_router.put("/buildings/{building_id}", response_model=schemas.Buildings)
def update_building(building_id: str, building: schemas.BuildingsCreate, db: Session = Depends(get_pgdb_session)):
    db_building = crud.get_building(db, building_id=building_id)
    if db_building is None:
        raise HTTPException(status_code=404, detail="Building not found")
    return crud.update_building(db=db, building=building, db_building=db_building)

@infra_router.delete("/buildings/{building_id}")
def delete_building(building_id: str, db: Session = Depends(get_pgdb_session)):
    db_building = crud.get_building(db, building_id=building_id)
    if db_building is None:
        raise HTTPException(status_code=404, detail="Building not found")
    crud.delete_building(db=db, db_building=db_building)
    return {"message": "Building deleted"}

@infra_router.post("/cameras/", response_model=schemas.Cameras)
def create_camera(camera: schemas.CamerasCreate, db: Session = Depends(get_pgdb_session)):
    db_camera = crud.get_camera_by_url(db, cam_url=camera.cam_url)
    if db_camera:
        raise HTTPException(status_code=400, detail="Camera already exists")
    return crud.create_camera(db=db, camera=camera)

@infra_router.get("/cameras/", response_model=List[schemas.Cameras])
def read_cameras(skip: int = 0, limit: int = 100, db: Session = Depends(get_pgdb_session)):
    cameras = crud.get_cameras(db, skip=skip, limit=limit)
    return cameras

@infra_router.get("/cameras/{cam_id}", response_model=schemas.Cameras)
def read_camera(cam_id: str, db: Session = Depends(get_pgdb_session)):
    db_camera = crud.get_camera(db, cam_id=cam_id)
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return db_camera

@infra_router.put("/cameras/{cam_id}", response_model=schemas.Cameras)
def update_camera(cam_id: str, camera: schemas.CamerasCreate, db: Session = Depends(get_pgdb_session)):
    db_camera = crud.get_camera(db, cam_id=cam_id)
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    return crud.update_camera(db=db, camera=camera, db_camera=db_camera)

@infra_router.delete("/cameras/{cam_id}")
def delete_camera(cam_id: str, db: Session = Depends(get_pgdb_session)):
    db_camera = crud.get_camera(db, cam_id=cam_id)
    if db_camera is None:
        raise HTTPException(status_code=404, detail="Camera not found")
    crud.delete_camera(db=db, db_camera=db_camera)
    return {"message": "Camera deleted"}
