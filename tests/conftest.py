import alembic.config
import pytest
from metadata.core.database import orm
from metadata.core.database import connection
from metadata.core.domain.app import Organization

ORM_INITIATED = False

@pytest.fixture()
def setup_db():
    alembic.config.main(argv=['downgrade', 'base'])
    alembic.config.main(argv=['upgrade', 'head'])

    global ORM_INITIATED
    if not ORM_INITIATED:
        orm.init_orm_mappers()
        ORM_INITIATED = True


@pytest.fixture()
def session_factory(setup_db):
    return connection.get_db_session


@pytest.fixture()
def organization(session_factory):
    with session_factory() as session:
        org = Organization(
            name='org',
            gcp_project_id='gcp-project',
        )
        session.add(org)
        session.commit()
    return org
