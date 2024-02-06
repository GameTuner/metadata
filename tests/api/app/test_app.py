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

import pytest
from datetime import date

from sqlalchemy import select
from metadata.api.app.request import CreateAppDTO
from metadata.core.domain.app import App, AppId, Datasource, Timezone
from metadata.api.app.service import AppService
from metadata.core.domain.status import Status
from metadata.core.domain.common import EntityError


def test_registering_new_app_should_correctly_initialize_it(session_factory, organization):
    app_service = AppService(session_factory)
    app_id = AppId('newapp')
    timezone = Timezone(name='Europe/Belgrade')
    app_service.register(CreateAppDTO(app_id.value, organization.name, timezone, date(2023, 6, 12)))
    app = app_service.get_by_app_id(app_id)
    assert app.id == app_id
    assert app.timezone == timezone
    assert len(app.api_key) > 0
    assert app.status == Status.NOT_READY
    assert app.datasources == [Datasource(id='user_history', app_id=app_id, has_data_from=date(2023, 6, 12))]
    # TODO check common events


def test_get_all_success_apps_returns_only_sucess(session_factory, organization):
    app_service = AppService(session_factory)
    app_service.register(CreateAppDTO(AppId(value='appone').value, organization.name, Timezone(name='Europe/Belgrade'), date(2023, 6, 12)))
    app_service.register(CreateAppDTO(AppId(value='apptwo').value, organization.name, Timezone(name='Europe/Belgrade'), date(2023, 6, 12)))
    with session_factory() as session:
        app: App = session.scalars(select(App).where(App.id == AppId(value='appone'))).unique().one()
        app.set_status(Status.SUCCESS)
        session.commit()
    assert [app.id for app in app_service.get_all_success()] == [AppId(value='appone')]


def test_registering_duplicate_app_fails(session_factory, organization):
    app_service = AppService(session_factory)
    app_id = AppId('newapp')
    app_service.register(CreateAppDTO(app_id.value, organization.name))
    with pytest.raises(EntityError):
        app_service.register(CreateAppDTO(app_id.value, organization.name))


def test_updating_datasource_freshness_for_the_first_time_succeeds(session_factory, organization):
    app_id = AppId('newapp')
    app_service = AppService(session_factory)
    app_service.register(CreateAppDTO(app_id.value, organization.name, has_data_from=date(2023, 6, 12)))
    updated_app = app_service.update_datasource_freshness(app_id, 'new_ds', date(2023, 6, 14))
    fetched_app = app_service.get_by_app_id(app_id)

    assert updated_app.datasources == fetched_app.datasources
    assert fetched_app.get_datasource('new_ds') == Datasource(id='new_ds', app_id=app_id, has_data_from=date(2023, 6, 14), has_data_up_to=date(2023, 6, 14))


def test_updating_existing_datasource_succeeds(session_factory, organization):
    app_id = AppId('newapp')
    app_service = AppService(session_factory)
    app_service.register(CreateAppDTO(app_id.value, organization.name, has_data_from=date(2023, 6, 12)))
    updated_app = app_service.update_datasource_freshness(app_id, 'new_ds', date(2023, 6, 14))
    updated_app = app_service.update_datasource_freshness(app_id, 'new_ds', date(2023, 6, 15))
    fetched_app = app_service.get_by_app_id(app_id)

    assert updated_app.datasources == fetched_app.datasources
    assert fetched_app.get_datasource('new_ds') == Datasource(id='new_ds', app_id=app_id, has_data_from=date(2023, 6, 14), has_data_up_to=date(2023, 6, 15))
