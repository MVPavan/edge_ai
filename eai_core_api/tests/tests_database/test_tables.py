from eai_core_api.imports import (
    select, MetaData, SQLModel
)

from eai_core_api.backend.database.tables import (
    Organizations, Buildings, Cameras,
    AICategories, AIAnalytics, AIJobs
)
from eai_core_api.backend.database.manage import (
    create_db, engine, get_pgdb_session
)

# Create_db is necessary - github actions pytests fail otherwise
create_db() 

def delete_table(table_model):
    with get_pgdb_session().__next__() as session:
        session.query(table_model).delete()
        session.commit()

def delete_all_tables():
    for table_model in [AIJobs, AIAnalytics, AICategories, Cameras, Buildings, Organizations]:
        delete_table(table_model)

def test_delete_all_tables():
    delete_all_tables()

################################ Check Table Names ################################
metadata = MetaData()
metadata.reflect(bind=engine)
# Get the table names
table_names_db = metadata.tables.keys()
def test_table_names():
    for model_name, table_name in zip(
        [Organizations, Buildings, Cameras, AICategories, AIAnalytics, AIJobs],
        ['organizations', 'buildings', 'cameras', 'aicategories', 'aianalytics', 'aijobs']
    ):
        assert model_name.__tablename__ == table_name and \
        table_name in table_names_db


#################################### Insert Table rows #########################################################
def create_organizations_table():
    with get_pgdb_session().__next__() as session:
        org_a = Organizations(name='org_a', description='org_a description',)
        org_b = Organizations(name='org_b', description='org_b description',)
        org_c = Organizations(name='org_c', description='org_c description',)
        session.add_all([org_a, org_b, org_c])
        session.commit()

def create_buildings_table():
    with get_pgdb_session().__next__() as session:
        building_a = Buildings(name='building_a', description='building_a description', organization_name='org_a')
        building_b = Buildings(name='building_b', description='building_b description', organization_name='org_b')
        building_c = Buildings(name='building_c', description='building_c description', organization_name='org_c')

        building_d = Buildings(name='building_d', description='building_d description', organization_name='org_a')
        building_e = Buildings(name='building_e', description='building_e description')
        building_e.organization = Organizations(name='org_e', description='org_e description')
        session.add_all([building_a, building_b, building_c, building_d, building_e])
        session.commit()

def create_cameras_table():
    with get_pgdb_session().__next__() as session:
        camera_a = Cameras(name='camera_a', cam_url='http://camera_a.com', description='camera_a description', building_name='building_a')
        camera_b = Cameras(name='camera_b', cam_url='http://camera_b.com', description='camera_b description', building_name='building_b')
        camera_c = Cameras(name='camera_c', cam_url='http://camera_c.com', description='camera_c description', building_name='building_c')

        camera_d = Cameras(name='camera_d', cam_url='http://camera_d.com', description='camera_d description', building_name='building_a')
        camera_e = Cameras(name='camera_e', cam_url='http://camera_e.com', description='camera_e description')
        camera_e.building = Buildings(name='building_f', description='building_f description', organization_name='org_b')
        session.add_all([camera_a, camera_b, camera_c, camera_d, camera_e])
        session.commit()

def create_aicategories_table():
    with get_pgdb_session().__next__() as session:
        aicategory_a = AICategories(name='aicategory_a', description='aicategory_a description')
        aicategory_b = AICategories(name='aicategory_b', description='aicategory_b description')
        session.add_all([aicategory_a, aicategory_b])
        session.commit()


def create_aianalytics_table():
    with get_pgdb_session().__next__() as session:
        aianalytics_a = AIAnalytics(name='aianalytics_a', description='aianalytics_a description', ai_category_name="aicategory_a")
        aianalytics_b = AIAnalytics(name='aianalytics_b', description='aianalytics_b description', ai_category_name="aicategory_a")
        session.add_all([aianalytics_a, aianalytics_b])
        session.commit()

def create_aijobs_table():
    with get_pgdb_session().__next__() as session:
        analytics_id = session.execute(select(AIAnalytics).where(AIAnalytics.name == 'aianalytics_a')).first()[0].analytics_id
        cam_id = session.execute(select(Cameras).where(Cameras.name == 'camera_a')).first()[0].cam_id
        aijob_a = AIJobs(analytics_id=analytics_id, cam_id=cam_id, name='aijob_a', description='aijob_a description')
        
        analytics_id = session.execute(select(AIAnalytics).where(AIAnalytics.name == 'aianalytics_b')).first()[0].analytics_id
        cam_id = session.execute(select(Cameras).where(Cameras.name == 'camera_b')).first()[0].cam_id
        aijob_b = AIJobs(analytics_id=analytics_id, cam_id=cam_id, name='aijob_b', description='aijob_b description')
        session.add_all([aijob_a, aijob_b])
        session.commit()


###################################### Delete Table rows #########################################################

def delete_table_rows(table_model, row_names:list=['*']):
    with get_pgdb_session().__next__() as session:
        if row_names[0] == '*':
            session.query(table_model).delete()
            session.commit()
        else:
            statement = select(table_model).where(table_model.name.in_(row_names))
            results = session.execute(statement).all()
            for result in results:
                session.delete(result[0])
            session.commit()


def delete_organizations_table():
    delete_table_rows(Organizations, ['org_a', 'org_b', 'org_c', 'org_d', 'org_e', 'org_f'])

def delete_buildings_table():
    delete_table_rows(Buildings, ['building_a', 'building_b', 'building_c', 'building_d', 'building_e', 'building_f'])

def delete_cameras_table():
    delete_table_rows(Cameras, ['camera_a', 'camera_b', 'camera_c', 'camera_d', 'camera_e', 'camera_f', 'camera_g'])

def delete_aicategories_table():
    delete_table_rows(AICategories, ['aicategory_a', 'aicategory_b', 'aicategory_c'])

def delete_aianalytics_table():
    delete_table_rows(AIAnalytics, ['aianalytics_a', 'aianalytics_b', 'aianalytics_c', 'aianalytics_d'])

def delete_aijobs_table():
    delete_table_rows(AIJobs, ['aijob_a', 'aijob_b', 'aijob_c', 'aijob_d'])



################################# Test Insert Table rows ##########################################

def check_table_rows(table_model, row_names:list):
    with get_pgdb_session().__next__() as session:
        statement = select(table_model).where(table_model.name.in_(row_names))
        results = session.execute(statement).all()
        assert len(results) == len(row_names)
        for result in results:
            assert result[0].name in row_names


def test_create_organizations_table():
    delete_organizations_table()
    create_organizations_table()
    check_table_rows(Organizations, ['org_a', 'org_b', 'org_c'])

def test_create_buildings_table():
    delete_buildings_table()
    create_buildings_table()
    check_table_rows(Buildings, ['building_a', 'building_b', 'building_c', 'building_d', 'building_e'])

def test_create_cameras_table():
    delete_cameras_table()
    create_cameras_table()
    check_table_rows(Cameras, ['camera_a', 'camera_b', 'camera_c', 'camera_d', 'camera_e'])

def test_create_aicategories_table():
    delete_aicategories_table()
    create_aicategories_table()
    check_table_rows(AICategories, ['aicategory_a', 'aicategory_b'])

def test_create_aianalytics_table():
    delete_aianalytics_table()
    create_aianalytics_table()
    check_table_rows(AIAnalytics, ['aianalytics_a', 'aianalytics_b'])

def test_create_aijobs_table():
    delete_aijobs_table()
    create_aijobs_table()
    check_table_rows(AIJobs, ['aijob_a', 'aijob_b'])


########################### Test Delete Table rows ##########################################

def check_table_rows_delete(table_model):
    with get_pgdb_session().__next__() as session:
        results = session.query(table_model).all()
        assert len(results) == 0

def test_delete_aijobs_table():
    delete_aijobs_table()
    check_table_rows_delete(AIJobs)

def test_delete_aianalytics_table():
    delete_aianalytics_table()
    check_table_rows_delete(AIAnalytics)

def test_delete_aicategories_table():
    delete_aicategories_table()
    check_table_rows_delete(AICategories)

def test_delete_cameras_table():
    delete_cameras_table()
    check_table_rows_delete(Cameras)

def test_delete_buildings_table():
    delete_buildings_table()
    check_table_rows_delete(Buildings)

def test_delete_organizations_table():
    delete_organizations_table()
    check_table_rows_delete(Organizations)


