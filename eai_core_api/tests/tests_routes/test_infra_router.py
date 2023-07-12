
from eai_core_api.imports import (
    select, MetaData, SQLModel, TestClient
)

from eai_core_api.config import FASTAPI_PORT, API_V1_STR

from eai_core_api.backend.database.tables import (
    Organizations, Buildings, Cameras,
    AICategories, AIAnalytics, AIJobs
)
from eai_core_api.backend.database.manage import (
    create_db, get_pgdb_session
)

from eai_core_api.backend.database import tables as schemas
from eai_core_api.backend.database import crud
from eai_core_api.backend.fastapi_app import fastapi_app

from tests.tests_database import test_tables 


base_url=f"http://localhost:{FASTAPI_PORT}{API_V1_STR}/infrastructure"
fastapi_client = TestClient(fastapi_app,base_url=base_url)

# Test Organizations CRUD

def test_create_organization():
    test_tables.delete_table(Organizations)
    db = get_pgdb_session().__next__()
    db_organization = schemas.OrganizationsCreate(name="Test Organization")
    response = fastapi_client.post("organizations/", json=db_organization.dict())
    assert response.status_code == 200
    assert response.json()["name"] == db_organization.name
    db_organization_1 = crud.get_organization(db, name=db_organization.name)
    db.refresh(db_organization_1)
    assert db_organization_1 is not None
    assert db_organization_1.name == db_organization.name
    db.close()

def test_read_organizations():
    db = get_pgdb_session().__next__()
    db_organizations = crud.get_organizations(db)
    response = fastapi_client.get("organizations/")
    assert response.status_code == 200
    assert len(response.json()) == len(db_organizations)
    db.close()

def test_read_organization():
    test_tables.delete_table(Organizations)
    db = get_pgdb_session().__next__()
    db_organization = crud.create_organization(db, schemas.OrganizationsCreate(name="Test Organization"))
    response = fastapi_client.get(f"organizations/{db_organization.name}")
    assert response.status_code == 200
    assert response.json()["name"] == db_organization.name
    db.close()

def test_update_organization():
    test_tables.delete_table(Organizations)
    db = get_pgdb_session().__next__()
    db_organization = crud.create_organization(db, schemas.OrganizationsCreate(name="Test Organization"))
    new_organization = schemas.OrganizationsCreate(name="New Test Organization")
    response = fastapi_client.put(f"organizations/{db_organization.name}", json=new_organization.dict())
    assert response.status_code == 200
    assert response.json()["name"] == new_organization.name
    db_organization = crud.get_organization(db, name=new_organization.name)
    db.refresh(db_organization)
    assert db_organization is not None
    assert db_organization.name == new_organization.name
    db.close()

def test_delete_organization():
    test_tables.delete_table(Organizations)
    db = get_pgdb_session().__next__()
    db_organization = crud.create_organization(db, schemas.OrganizationsCreate(name="Test Organization"))
    response = fastapi_client.delete(f"organizations/{db_organization.name}")
    assert response.status_code == 200
    assert response.json()["name"] == db_organization.name
    db_organization_1 = crud.get_organization(db, name=db_organization.name)
    assert db_organization_1 is None
    db.close()


# Test Buildings CRUD

def test_create_building():
    test_tables.delete_table(Buildings)
    db = get_pgdb_session().__next__()
    db_building = schemas.BuildingsCreate(name="Test Building")
    response = fastapi_client.post("buildings/", json=db_building.dict())
    assert response.status_code == 200
    assert response.json()["name"] == db_building.name
    db_building_1 = crud.get_building(db, name=db_building.name)
    db.refresh(db_building_1)
    assert db_building_1 is not None
    assert db_building_1.name == db_building.name
    db.close()

def test_read_buildings():
    db = get_pgdb_session().__next__()
    db_buildings = crud.get_buildings(db)
    response = fastapi_client.get("buildings/")
    assert response.status_code == 200
    assert len(response.json()) == len(db_buildings)
    db.close()

def test_read_building():
    test_tables.delete_table(Buildings)
    db = get_pgdb_session().__next__()
    db_building = crud.create_building(db, schemas.BuildingsCreate(name="Test Building"))
    response = fastapi_client.get(f"buildings/{db_building.name}")
    assert response.status_code == 200
    assert response.json()["name"] == db_building.name
    db.close()

def test_update_building():
    test_tables.delete_table(Buildings)
    db = get_pgdb_session().__next__()
    db_building = crud.create_building(db, schemas.BuildingsCreate(name="Test Building"))
    new_building = schemas.BuildingsCreate(name="New Test Building")
    response = fastapi_client.put(f"buildings/{db_building.name}", json=new_building.dict())
    assert response.status_code == 200
    assert response.json()["name"] == new_building.name
    db_building = crud.get_building(db, name=new_building.name)
    db.refresh(db_building)
    assert db_building is not None
    assert db_building.name == new_building.name
    db.close()

def test_delete_building():
    test_tables.delete_table(Buildings)
    db = get_pgdb_session().__next__()
    db_building = crud.create_building(db, schemas.BuildingsCreate(name="Test Building"))
    response = fastapi_client.delete(f"buildings/{db_building.name}")
    assert response.status_code == 200
    assert response.json()["name"] == db_building.name
    db_building_1 = crud.get_building(db, name=db_building.name)
    assert db_building_1 is None
    db.close()


# Test Cameras CRUD

def test_create_camera():
    test_tables.delete_table(Cameras)
    db = get_pgdb_session().__next__()
    db_camera = schemas.CamerasCreate(name="Test Camera", cam_url="http://test.com")
    response = fastapi_client.post("cameras/", json=db_camera.dict())
    assert response.status_code == 200
    assert response.json()["name"] == db_camera.name
    db_camera_1 = crud.get_camera_by_url(db, cam_url=db_camera.cam_url)
    db.refresh(db_camera_1)
    assert db_camera_1 is not None
    assert db_camera_1.name == db_camera.name
    db.close()

def test_read_cameras():
    db = get_pgdb_session().__next__()
    db_cameras = crud.get_all_cameras(db)
    response = fastapi_client.get("cameras/")
    assert response.status_code == 200
    assert len(response.json()) == len(db_cameras)
    db.close()

def test_read_camera():
    test_tables.delete_table(Cameras)
    db = get_pgdb_session().__next__()
    db_camera = crud.create_camera(db, schemas.CamerasCreate(name="Test Camera", cam_url="http://test.com"))
    response = fastapi_client.get(f"cameras/{db_camera.cam_id}")
    assert response.status_code == 200
    assert response.json()["cam_url"] == db_camera.cam_url
    db.close()

def test_read_camera_by_name():
    test_tables.delete_table(Cameras)
    db = get_pgdb_session().__next__()
    db_camera = crud.create_camera(db, schemas.CamerasCreate(name="Test Camera", cam_url="http://test.com"))
    response = fastapi_client.get(f"cameras/name/{db_camera.name}")
    assert response.status_code == 200
    assert response.json()[0]["cam_url"] == db_camera.cam_url
    db.close()

def test_update_camera():
    test_tables.delete_table(Cameras)
    db = get_pgdb_session().__next__()
    db_camera = crud.create_camera(db, schemas.CamerasCreate(name="Test Camera", cam_url="http://test.com"))
    new_camera = schemas.CamerasCreate(name="New Test Camera", cam_url="http://newtest.com")
    response = fastapi_client.put(f"cameras/{db_camera.cam_id}", json=new_camera.dict())
    assert response.status_code == 200
    assert response.json()["cam_url"] == new_camera.cam_url
    assert response.json()["cam_id"] == db_camera.cam_id
    db_camera = crud.get_camera(db, cam_id=db_camera.cam_id)
    db.refresh(db_camera)
    assert db_camera is not None
    assert db_camera.cam_url == new_camera.cam_url
    db.close()

def test_delete_camera():
    test_tables.delete_table(Cameras)
    db = get_pgdb_session().__next__()
    db_camera = crud.create_camera(db, schemas.CamerasCreate(name="Test Camera", cam_url="http://test.com"))
    response = fastapi_client.delete(f"cameras/{db_camera.cam_id}")
    assert response.status_code == 200
    assert response.json()["cam_url"] == db_camera.cam_url
    db_camera_1 = crud.get_camera(db, cam_id=db_camera.cam_id) 
    assert db_camera_1 is None
    db.close()