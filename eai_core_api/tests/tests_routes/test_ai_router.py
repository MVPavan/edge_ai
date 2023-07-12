
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


base_url=f"http://localhost:{FASTAPI_PORT}{API_V1_STR}/ai"
fastapi_client = TestClient(fastapi_app,base_url=base_url)


# Test AI Category routes

def test_create_ai_category():
    test_tables.delete_table(AICategories)
    category = {"name": "test_category", "description": "test_description"}
    response = fastapi_client.post("ai_categories/", json=category)
    assert response.status_code == 200
    assert response.json()["name"] == category["name"]
    assert response.json()["description"] == category["description"]

def test_read_ai_category():
    test_tables.delete_table(AICategories)
    category = {"name": "test_category", "description": "test_description"}
    db = get_pgdb_session().__next__()
    db_category = crud.create_ai_category(db, schemas.AICategories(**category))
    db.commit()
    db.refresh(db_category)
    db.close()
    response = fastapi_client.get(f"ai_categories/{db_category.name}")
    assert response.status_code == 200
    assert response.json()["name"] == db_category.name
    assert response.json()["description"] == db_category.description

def test_read_ai_categories():
    response = fastapi_client.get("ai_categories/")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_update_ai_category():
    test_tables.delete_table(AICategories)
    category = {"name": "test_category", "description": "test_description"}
    db = get_pgdb_session().__next__()
    db_category = crud.create_ai_category(db, schemas.AICategories(**category))
    db.commit()
    db.refresh(db_category)
    db.close()
    updated_category = {"name": "updated_category", "description": "updated_description"}
    response = fastapi_client.put(f"ai_categories/{db_category.name}", json=updated_category)
    assert response.status_code == 200
    assert response.json()["name"] == updated_category["name"]
    assert response.json()["description"] == updated_category["description"]

def test_delete_ai_category():
    test_tables.delete_table(AICategories)
    category = {"name": "test_category", "description": "test_description"}
    db = get_pgdb_session().__next__()
    db_category = crud.create_ai_category(db, schemas.AICategories(**category))
    db.commit()
    db.refresh(db_category)
    db.close()
    response = fastapi_client.delete(f"ai_categories/{db_category.name}")
    assert response.status_code == 200
    assert response.json()["name"] == db_category.name
    assert response.json()["description"] == db_category.description



# Test AI Analytics routes

def test_create_ai_analytics():
    test_tables.delete_table(AIAnalytics)
    analytics = {"name": "test_analytics", "description": "test_description"}
    response = fastapi_client.post("ai_analytics/", json=analytics)
    assert response.status_code == 200
    assert response.json()["name"] == analytics["name"]
    assert response.json()["description"] == analytics["description"]

def test_read_ai_analytics():
    test_tables.delete_table(AIAnalytics)
    analytics = {"name": "test_analytics", "description": "test_description"}
    db = get_pgdb_session().__next__()
    db_analytics = crud.create_ai_analytics(db, schemas.AIAnalyticsCreate(**analytics))
    db.commit()
    db.refresh(db_analytics)
    db.close()
    response = fastapi_client.get(f"ai_analytics/{db_analytics.analytics_id}")
    assert response.status_code == 200
    assert response.json()["name"] == db_analytics.name
    assert response.json()["description"] == db_analytics.description

def test_read_all_ai_analytics():
    response = fastapi_client.get("ai_analytics/")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_read_ai_analytics_by_name():
    test_tables.delete_table(AIAnalytics)
    analytics = {"name": "test_analytics", "description": "test_description"}
    db = get_pgdb_session().__next__()
    db_analytics = crud.create_ai_analytics(db, schemas.AIAnalyticsCreate(**analytics))
    db.commit()
    db.refresh(db_analytics)
    db.close()
    response = fastapi_client.get(f"ai_analytics/name/{db_analytics.name}")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_read_ai_analytics_by_category():
    test_tables.delete_table(AICategories)
    test_tables.delete_table(AIAnalytics)
    category = {"name": "test_category", "description": "test_description"}
    db = get_pgdb_session().__next__()
    db_category = crud.create_ai_category(db, schemas.AICategories(**category))
    db.commit()
    db.refresh(db_category)
    analytics = {"name": "test_analytics","ai_category_name":db_category.name, "description": "test_description"}
    db = get_pgdb_session().__next__()
    db_analytics = crud.create_ai_analytics(db, schemas.AIAnalyticsCreate(**analytics))
    db.commit()
    db.refresh(db_analytics)
    db.close()
    response = fastapi_client.get(f"ai_analytics/category/{db_analytics.ai_category_name}")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_update_ai_analytics():
    test_tables.delete_table(AIAnalytics)
    analytics = {"name": "test_analytics", "description": "test_description"}
    db = get_pgdb_session().__next__()
    db_analytics = crud.create_ai_analytics(db, schemas.AIAnalyticsCreate(**analytics))
    db.commit()
    db.refresh(db_analytics)
    db.close()
    updated_analytics = {"name": "updated_analytics", "description": "updated_description"}
    response = fastapi_client.put(f"ai_analytics/{db_analytics.analytics_id}", json=updated_analytics)
    assert response.status_code == 200
    assert response.json()["name"] == updated_analytics["name"]
    assert response.json()["description"] == updated_analytics["description"]

def test_delete_ai_analytics():
    test_tables.delete_table(AIAnalytics)
    analytics = {"name": "test_analytics", "description": "test_description"}
    db = get_pgdb_session().__next__()
    db_analytics = crud.create_ai_analytics(db, schemas.AIAnalyticsCreate(**analytics))
    db.commit()
    db.refresh(db_analytics)
    db.close()
    response = fastapi_client.delete(f"ai_analytics/{db_analytics.analytics_id}")
    assert response.status_code == 200
    assert response.json()["name"] == db_analytics.name
    assert response.json()["description"] == db_analytics.description


# # Test AI Jobs routes

# def create_analytics_camera_row():
#     test_tables.delete_table(AIAnalytics)
#     test_tables.delete_table(Cameras)
#     analytics = {"name": "test_analytics",  "description": "test_description"}
#     camera = {"name": "test_camera", "cam_url": "rtsp://test_rtsp_url", "description": "test_description"}
#     db = get_pgdb_session().__next__()
#     db_analytics = crud.create_ai_analytics(db, schemas.AIAnalyticsCreate(**analytics))
#     db.commit()
#     db.refresh(db_analytics)
#     db_camera = crud.create_camera(db, schemas.CamerasCreate(**camera))
#     db.commit()
#     db.refresh(db_camera)
#     db.close()
#     return db_analytics, db_camera

# def test_create_ai_job():
#     db_analytics, db_camera = create_analytics_camera_row()
#     job = {"name": "test_job", "analytics_id": db_analytics.analytics_id, "cam_id": db_camera.cam_id, "description": "test_status"}
#     response = fastapi_client.post("ai_jobs/", json=job)
#     assert response.status_code == 200
#     assert response.json()["name"] == job["name"]
#     assert response.json()["analytics_id"] == job["analytics_id"]
#     assert response.json()["cam_id"] == job["cam_id"]
#     assert response.json()["description"] == job["description"]

# def test_read_ai_job():
#     db_analytics, db_camera = create_analytics_camera_row()
#     job = {"name": "test_job", "analytics_id": db_analytics.analytics_id, "cam_id": db_camera.cam_id, "description": "test_status"}
#     db = get_pgdb_session().__next__()
#     db_job = crud.create_ai_job(db, schemas.AIJobsCreate(**job))
#     db.commit()
#     db.refresh(db_job)
#     db.close()
#     response = fastapi_client.get(f"ai_jobs/{db_job.job_id}")
#     assert response.status_code == 200
#     assert response.json()["name"] == db_job.name
#     assert response.json()["analytics_id"] == db_job.analytics_id
#     assert response.json()["cam_id"] == db_job.cam_id
#     assert response.json()["description"] == db_job.description

# def test_read_all_ai_jobs():
#     response = fastapi_client.get("ai_jobs/")
#     assert response.status_code == 200
#     assert len(response.json()) > 0

# def test_read_ai_job_by_name():
#     db_analytics, db_camera = create_analytics_camera_row()
#     job = {"name": "test_job", "analytics_id": db_analytics.analytics_id, "cam_id": db_camera.cam_id, "description": "test_status"}
#     db = get_pgdb_session().__next__()
#     db_job = crud.create_ai_job(db, schemas.AIJobsCreate(**job))
#     db.commit()
#     db.refresh(db_job)
#     db.close()
#     response = fastapi_client.get(f"ai_jobs/name/{db_job.name}")
#     assert response.status_code == 200
#     assert len(response.json()) > 0

# def test_read_ai_job_by_ai_analytics():
#     db_analytics, db_camera = create_analytics_camera_row()
#     job = {"name": "test_job", "analytics_id": db_analytics.analytics_id, "cam_id": db_camera.cam_id, "description": "test_status"}
#     db = get_pgdb_session().__next__()
#     db_job = crud.create_ai_job(db, schemas.AIJobsCreate(**job))
#     db.commit()
#     db.refresh(db_job)
#     db.close()
#     response = fastapi_client.get(f"ai_jobs/analytics/{db_job.analytics_id}")
#     assert response.status_code == 200
#     assert len(response.json()) > 0

# def test_read_ai_job_by_camera():
#     db_analytics, db_camera = create_analytics_camera_row()
#     job = {"name": "test_job", "analytics_id": db_analytics.analytics_id, "cam_id": db_camera.cam_id, "description": "test_status"}
#     db = get_pgdb_session().__next__()
#     db_job = crud.create_ai_job(db, schemas.AIJobsCreate(**job))
#     db.commit()
#     db.refresh(db_job)
#     db.close()
#     response = fastapi_client.get(f"ai_jobs/camera/{db_job.cam_id}")
#     assert response.status_code == 200
#     assert len(response.json()) > 0

# def test_update_ai_job():
#     db_analytics, db_camera = create_analytics_camera_row()
#     job = {"name": "test_job", "analytics_id": db_analytics.analytics_id, "cam_id": db_camera.cam_id, "description": "test_status"}
#     db = get_pgdb_session().__next__()
#     db_job = crud.create_ai_job(db, schemas.AIJobsCreate(**job))
#     db.commit()
#     db.refresh(db_job)
#     db.close()
#     updated_job = {"name": "updated_job", "analytics_id": db_analytics.analytics_id, "cam_id": db_camera.cam_id, "description": "updated_status"}
#     response = fastapi_client.put(f"ai_jobs/{db_job.job_id}", json=updated_job)
#     assert response.status_code == 200
#     assert response.json()["name"] == updated_job["name"]
#     assert response.json()["analytics_id"] == updated_job["analytics_id"]
#     assert response.json()["cam_id"] == updated_job["cam_id"]
#     assert response.json()["description"] == updated_job["description"]

# def test_delete_ai_job():
#     db_analytics, db_camera = create_analytics_camera_row()
#     job = {"name": "test_job", "analytics_id": db_analytics.analytics_id, "cam_id": db_camera.cam_id, "description": "test_status"}
#     db = get_pgdb_session().__next__()
#     db_job = crud.create_ai_job(db, schemas.AIJobsCreate(**job))
#     db.commit()
#     db.refresh(db_job)
#     db.close()
#     response = fastapi_client.delete(f"ai_jobs/{db_job.job_id}")
#     assert response.status_code == 200
#     assert response.json()["name"] == db_job.name
#     assert response.json()["analytics_id"] == db_job.analytics_id
#     assert response.json()["cam_id"] == db_job.cam_id
#     assert response.json()["description"] == db_job.status