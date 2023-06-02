from imports import Session
from backend.database.crud import (
    create_organization, get_organization, get_organizations, 
    update_organization, delete_organization,
    create_building, get_building, get_buildings, 
    update_building, delete_building,
    create_ai_category, get_ai_category, get_ai_categories, 
    update_ai_category, delete_ai_category,
    create_ai_analytics, get_ai_analytics, get_ai_analytics_by_name, 
    get_ai_analytics_by_category, get_ai_analytics_by_camera, get_all_ai_analytics,
    update_ai_analytics, delete_ai_analytics,
    create_camera, get_camera, get_camera_by_name, 
    get_camera_by_building, get_camera_by_analytics, get_all_cameras,
    update_camera, delete_camera
)
from backend.database.tables import (
    OrganizationsCreate, BuildingsCreate, AICategories, AIAnalyticsCreate, CamerasCreate
)

def test_organizations_crud(db: Session):
    # Create organization
    org_data = {"name": "Test Org", "description": "Test Org Description"}
    org = create_organization(db, OrganizationsCreate(**org_data))
    assert org.name == org_data["name"]
    assert org.description == org_data["description"]

    # Get organization
    org = get_organization(db, org_data["name"])
    assert org.name == org_data["name"]
    assert org.description == org_data["description"]

    # Get organizations
    orgs = get_organizations(db)
    assert len(orgs) == 1
    assert orgs[0].name == org_data["name"]
    assert orgs[0].description == org_data["description"]

    # Update organization
    new_org_data = {"description": "New Test Org Description"}
    org = update_organization(db, org_data["name"], OrganizationsCreate(**new_org_data))
    assert org.name == org_data["name"]
    assert org.description == new_org_data["description"]

    # Delete organization
    org = delete_organization(db, org_data["name"])
    assert org.name == org_data["name"]
    assert org.description == new_org_data["description"]

def test_buildings_crud(db: Session):
    # Create building
    building_data = {"name": "Test Building", "description": "Test Building Description"}
    building = create_building(db, BuildingsCreate(**building_data))
    assert building.name == building_data["name"]
    assert building.description == building_data["description"]

    # Get building
    building = get_building(db, building_data["name"])
    assert building.name == building_data["name"]
    assert building.description == building_data["description"]

    # Get buildings
    buildings = get_buildings(db)
    assert len(buildings) == 1
    assert buildings[0].name == building_data["name"]
    assert buildings[0].description == building_data["description"]

    # Update building
    new_building_data = {"description": "New Test Building Description"}
    building = update_building(db, building_data["name"], BuildingsCreate(**new_building_data))
    assert building.name == building_data["name"]
    assert building.description == new_building_data["description"]

    # Delete building
    building = delete_building(db, building_data["name"])
    assert building.name == building_data["name"]
    assert building.description == new_building_data["description"]

def test_ai_categories_crud(db: Session):
    # Create AI category
    ai_category_data = {"name": "Test AI Category", "description": "Test AI Category Description"}
    ai_category = create_ai_category(db, AICategories(**ai_category_data))
    assert ai_category.name == ai_category_data["name"]
    assert ai_category.description == ai_category_data["description"]

    # Get AI category
    ai_category = get_ai_category(db, ai_category_data["name"])
    assert ai_category.name == ai_category_data["name"]
    assert ai_category.description == ai_category_data["description"]

    # Get AI categories
    ai_categories = get_ai_categories(db)
    assert len(ai_categories) == 1
    assert ai_categories[0].name == ai_category_data["name"]
    assert ai_categories[0].description == ai_category_data["description"]

    # Update AI category
    new_ai_category_data = {"description": "New Test AI Category Description"}
    ai_category = update_ai_category(db, ai_category_data["name"], AICategories(**new_ai_category_data))
    assert ai_category.name == ai_category_data["name"]
    assert ai_category.description == new_ai_category_data["description"]

    # Delete AI category
    ai_category = delete_ai_category(db, ai_category_data["name"])
    assert ai_category.name == ai_category_data["name"]
    assert ai_category.description == new_ai_category_data["description"]

def test_ai_analytics_crud(db: Session):
    # Create AI analytics
    ai_analytics_data = {
        "name": "Test AI Analytics", 
        "description": "Test AI Analytics Description",
        "ai_category_name": "Object Detection",
        "camera_id": 1
    }
    ai_analytics = create_ai_analytics(db, AIAnalyticsCreate(**ai_analytics_data))
    assert ai_analytics.name == ai_analytics_data["name"]
    assert ai_analytics.description == ai_analytics_data["description"]
    assert ai_analytics.ai_category_name == ai_analytics_data["ai_category_name"]
    assert ai_analytics.camera_id == ai_analytics_data["camera_id"]

    # Get AI analytics by name
    ai_analytics = get_ai_analytics_by_name(db, ai_analytics_data["name"])
    assert ai_analytics.name == ai_analytics_data["name"]
    assert ai_analytics.description == ai_analytics_data["description"]
    assert ai_analytics.ai_category_name == ai_analytics_data["ai_category_name"]
    assert ai_analytics.camera_id == ai_analytics_data["camera_id"]

    # Get AI analytics by category
    ai_analytics_list = get_ai_analytics_by_category(db, ai_analytics_data["ai_category_name"])
    assert len(ai_analytics_list) == 1
    assert ai_analytics_list[0].name == ai_analytics_data["name"]
    assert ai_analytics_list[0].description == ai_analytics_data["description"]
    assert ai_analytics_list[0].ai_category_name == ai_analytics_data["ai_category_name"]
    assert ai_analytics_list[0].camera_id == ai_analytics_data["camera_id"]

    # Get AI analytics by camera
    ai_analytics_list = get_ai_analytics_by_camera(db, ai_analytics_data["camera_id"])
    assert len(ai_analytics_list) == 1
    assert ai_analytics_list[0].name == ai_analytics_data["name"]
    assert ai_analytics_list[0].description == ai_analytics_data["description"]
    assert ai_analytics_list[0].ai_category_name == ai_analytics_data["ai_category_name"]
    assert ai_analytics_list[0].camera_id == ai_analytics_data["camera_id"]

    # Get all AI analytics
    ai_analytics_list = get_all_ai_analytics(db)
    assert len(ai_analytics_list) == 1
    assert ai_analytics_list[0].name == ai_analytics_data["name"]
    assert ai_analytics_list[0].description == ai_analytics_data["description"]
    assert ai_analytics_list[0].ai_category_name == ai_analytics_data["ai_category_name"]
    assert ai_analytics_list[0].camera_id == ai_analytics_data["camera_id"]

    # Update AI analytics
    new_ai_analytics_data = {"description": "New Test AI Analytics Description"}
    ai_analytics = update_ai_analytics(db, ai_analytics_data["name"], AIAnalyticsCreate(**new_ai_analytics_data))
    assert ai_analytics.name == ai_analytics_data["name"]
    assert ai_analytics.description == new_ai_analytics_data["description"]
    assert ai_analytics.ai_category_name == ai_analytics_data["ai_category_name"]
    assert ai_analytics.camera_id == ai_analytics_data["camera_id"]

    # Delete AI analytics
    ai_analytics = delete_ai_analytics(db, ai_analytics_data["name"])
    assert ai_analytics.name == ai_analytics_data["name"]
    assert ai_analytics.description == new_ai_analytics_data["description"]
    assert ai_analytics.ai_category_name == ai_analytics_data["ai_category_name"]
    assert ai_analytics.camera_id == ai_analytics_data["camera_id"]

def test_cameras_crud(db: Session):
    # Create camera
    camera_data = {"name": "Test Camera", "description": "Test Camera Description", "building_id": 1}
    camera = create_camera(db, CamerasCreate(**camera_data))
    assert camera.name == camera_data["name"]
    assert camera.description == camera_data["description"]
    assert camera.building_id == camera_data["building_id"]

    # Get camera by name
    camera = get_camera_by_name(db, camera_data["name"])
    assert camera.name == camera_data["name"]
    assert camera.description == camera_data["description"]
    assert camera.building_id == camera_data["building_id"]

    # Get camera by building
    camera_list = get_camera_by_building(db, camera_data["building_id"])
    assert len(camera_list) == 1
    assert camera_list[0].name == camera_data["name"]
    assert camera_list[0].description == camera_data["description"]
    assert camera_list[0].building_id == camera_data["building_id"]

    # Get camera by analytics
    camera_list = get_camera_by_analytics(db, 1)
    assert len(camera_list) == 1
    assert camera_list[0].name == camera_data["name"]
    assert camera_list[0].description == camera_data["description"]
    assert camera_list[0].building_id == camera_data["building_id"]

    # Get all cameras
    camera_list = get_all_cameras(db)
    assert len(camera_list) == 1
    assert camera_list[0].name == camera_data["name"]
    assert camera_list[0].description == camera_data["description"]
    assert camera_list[0].building_id == camera_data["building_id"]

    # Update camera
    new_camera_data = {"description": "New Test Camera Description"}
    camera = update_camera(db, camera_data["name"], CamerasCreate(**new_camera_data))
    assert camera.name == camera_data["name"]
    assert camera.description == new_camera_data["description"]
    assert camera.building_id == camera_data["building_id"]

    # Delete camera
    camera = delete_camera(db, camera_data["name"])
    assert camera.name == camera_data["name"]
    assert camera.description == new_camera_data["description"]
    assert camera.building_id == camera_data["building_id"]