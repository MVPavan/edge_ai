from imports import (
    select, MetaData,
)

from backend.database.tables import (
    Organizations, Buildings, Cameras
)
from backend.database.manage import (
    create_db, engine, get_session
)

create_db()

metadata = MetaData()
metadata.reflect(bind=engine)

# Get the table names
table_names_db = metadata.tables.keys()

def test_table_names():
    for model_name, table_name in zip(
        [Organizations, Buildings, Cameras],
        ['organizations', 'buildings', 'cameras']
    ):
        assert model_name.__tablename__ == table_name and \
        table_name in table_names_db

def create_organizations_table():
    with get_session().__next__() as session:
        org_a = Organizations(name='org_a', description='org_a description',)
        org_b = Organizations(name='org_b', description='org_b description',)
        org_c = Organizations(name='org_c', description='org_c description',)
        session.add_all([org_a, org_b, org_c])
        session.commit()

def create_buildings_table():
    with get_session().__next__() as session:
        building_a = Buildings(name='building_a', description='building_a description', organization_name='org_a')
        building_b = Buildings(name='building_b', description='building_b description', organization_name='org_b')
        building_c = Buildings(name='building_c', description='building_c description', organization_name='org_c')

        building_d = Buildings(name='building_d', description='building_d description', organization_name='org_a')
        building_e = Buildings(name='building_e', description='building_e description')
        building_e.organization = Organizations(name='org_e', description='org_e description')
        session.add_all([building_a, building_b, building_c, building_d, building_e])
        session.commit()

def create_cameras_table():
    with get_session().__next__() as session:
        camera_a = Cameras(name='camera_a', cam_url='http://camera_a.com', description='camera_a description', building_name='building_a')
        camera_b = Cameras(name='camera_b', cam_url='http://camera_b.com', description='camera_b description', building_name='building_b')
        camera_c = Cameras(name='camera_c', cam_url='http://camera_c.com', description='camera_c description', building_name='building_c')

        camera_d = Cameras(name='camera_d', cam_url='http://camera_d.com', description='camera_d description', building_name='building_a')
        camera_e = Cameras(name='camera_e', cam_url='http://camera_e.com', description='camera_e description')
        camera_e.building = Buildings(name='building_f', description='building_f description', organization_name='org_b')
        session.add_all([camera_a, camera_b, camera_c, camera_d, camera_e])
        session.commit()


def delete_organizations_table():
    with get_session().__next__() as session:
        statement = select(Organizations).where(
            Organizations.name.in_(['org_a', 'org_b', 'org_c', 'org_d', 'org_e', 'org_f'])
        )
        results = session.execute(statement).all()
        for result in results:
            session.delete(result[0])
        session.commit()

def delete_buildings_table():
    with get_session().__next__() as session:
        statement = select(Buildings).where(
            Buildings.name.in_(['building_a', 'building_b', 'building_c', 'building_d', 'building_e', 'building_f'])
        )
        results = session.execute(statement).all()
        for result in results:
            session.delete(result[0])
        session.commit()

def delete_cameras_table():
    with get_session().__next__() as session:
        statement = select(Cameras).where(
            Cameras.name.in_(['camera_a', 'camera_b', 'camera_c', 'camera_d', 'camera_e', 'camera_f'])
        )
        results = session.execute(statement).all()
        for result in results:
            session.delete(result[0])
        session.commit()

def test_create_organizations_table():
    delete_organizations_table()
    create_organizations_table()
    with get_session().__next__() as session:
        statement = select(Organizations).where(
            Organizations.name.in_(['org_a', 'org_b', 'org_c'])
        )
        orgs = session.execute(statement).all()
        assert len(orgs) == 3
        assert orgs[0][0].name == 'org_a'
        assert orgs[1][0].name == 'org_b'
        assert orgs[2][0].name == 'org_c'

def test_create_buildings_table():
    delete_buildings_table()
    create_buildings_table()
    with get_session().__next__() as session:
        statement = select(Buildings).where(
            Buildings.name.in_(['building_a', 'building_b', 'building_c', 'building_d', 'building_e'])
        )
        buildings = session.execute(statement).all()
        assert len(buildings) == 5
        assert buildings[0][0].name == 'building_a'
        assert buildings[1][0].name == 'building_b'
        assert buildings[2][0].name == 'building_c'
        assert buildings[3][0].name == 'building_d'
        assert buildings[4][0].name == 'building_e'

def test_create_cameras_table():
    delete_cameras_table()
    create_cameras_table()
    with get_session().__next__() as session:
        statement = select(Cameras).where(
            Cameras.name.in_(['camera_a', 'camera_b', 'camera_c', 'camera_d', 'camera_e'])
        )
        cameras = session.execute(statement).all()
        assert len(cameras) == 5
        assert cameras[0][0].name == 'camera_a'
        assert cameras[1][0].name == 'camera_b'
        assert cameras[2][0].name == 'camera_c'
        assert cameras[3][0].name == 'camera_d'
        assert cameras[4][0].name == 'camera_e'

def test_delete_cameras_table():
    delete_cameras_table()
    with get_session().__next__() as session:
        cameras = session.query(Cameras).all()
        assert len(cameras) == 0

def test_delete_buildings_table():
    delete_buildings_table()
    with get_session().__next__() as session:
        buildings = session.query(Buildings).all()
        assert len(buildings) == 0

def test_delete_organizations_table():
    delete_organizations_table()
    with get_session().__next__() as session:
        orgs = session.query(Organizations).all()
        assert len(orgs) == 0