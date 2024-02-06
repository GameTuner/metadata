# Copyright (c) 2024 AlgebraAI All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
