from datetime import date
import pytest

from sqlalchemy import select
from metadata.api.app.request import CreateAppDTO
from metadata.api.app.service import AppService
from metadata.api.event.request import CreateOrUpdateEventDTO, CreateParameterDTO, UpdateParameterDTO
from metadata.api.event.service import EventService
from metadata.core.domain.app import AppId, Timezone
from metadata.core.domain.event import Event
from metadata.core.domain.schema import ParameterType
from metadata.core.domain.common import EntityError

@pytest.fixture
def app(session_factory, organization):
    app_service = AppService(session_factory)
    app_id = AppId('newapp')
    timezone = Timezone(name='Europe/Belgrade')
    return app_service.register(CreateAppDTO(app_id.value, organization.name, timezone, date(2023, 6, 12)))


def test_creating_new_event(session_factory, app):
    event_service = EventService(session_factory)
    event = event_service.create_or_update_event(app.id, CreateOrUpdateEventDTO(
        name='event',
        new_parameters=[CreateParameterDTO(
            name='param',
            type=ParameterType.STRING,
            is_gdpr=False,
            introduced_at_version=0
        )]
    ))
    with session_factory() as session:
        db_event: Event = session.scalars(select(Event).where(Event.id == event.id)).unique().one()
    assert len(db_event.get_schema().parameters) == 1
    assert db_event.get_schema().parameters[0].name == 'param'
    assert db_event.get_schema().parameters[0].type == ParameterType.STRING
    assert db_event.get_schema().parameters[0].is_gdpr is False
    assert db_event.get_schema().parameters[0].introduced_at_version == 0

def test_creating_new_event_version(session_factory, app):
    event_service = EventService(session_factory)
    event = event_service.create_or_update_event(app.id, CreateOrUpdateEventDTO(
        name='event',
        new_parameters=[CreateParameterDTO(
            name='param',
            type=ParameterType.STRING,
            is_gdpr=False,
            introduced_at_version=0
        )]
    ))
    event_service.create_or_update_event(app.id, CreateOrUpdateEventDTO(
        name='event',
        new_parameters=[CreateParameterDTO(
            name='param1',
            type=ParameterType.BOOLEAN,
            is_gdpr=True,
            introduced_at_version=1
        )]
    ))

    with session_factory() as session:
        db_event: Event = session.scalars(select(Event).where(Event.id == event.id)).unique().one()
    assert len(db_event.get_schema().parameters) == 2
    assert db_event.get_schema().parameters[0].name == 'param'
    assert db_event.get_schema().parameters[0].type == ParameterType.STRING
    assert db_event.get_schema().parameters[0].is_gdpr is False
    assert db_event.get_schema().parameters[0].introduced_at_version == 0
    assert db_event.get_schema().parameters[1].name == 'param1'
    assert db_event.get_schema().parameters[1].type == ParameterType.BOOLEAN
    assert db_event.get_schema().parameters[1].is_gdpr is True
    assert db_event.get_schema().parameters[1].introduced_at_version == 1


def test_creating_new_event_with_atomic_param_name_fails(session_factory, app):
    event_service = EventService(session_factory)
    with pytest.raises(EntityError):
        event_service.create_or_update_event(app.id, CreateOrUpdateEventDTO(
            name='event',
            new_parameters=[CreateParameterDTO(
                name='sandbox_mode',
                type=ParameterType.STRING,
                is_gdpr=False,
                introduced_at_version=0
            )]
        ))


def test_updating_event_metadata(session_factory, app):
    event_service = EventService(session_factory)
    event = event_service.create_or_update_event(app.id, CreateOrUpdateEventDTO(
        name='event',
        new_parameters=[CreateParameterDTO(
            name='param',
            type=ParameterType.STRING,
            is_gdpr=False,
            introduced_at_version=0
        )]
    ))
    event_service.create_or_update_event(app.id, CreateOrUpdateEventDTO(
        name='event',
        description='desc_event',
        existing_parameters=[UpdateParameterDTO(
            name='param',
            is_gdpr=True,
            description='desc_param'
        )]
    ))
    with session_factory() as session:
        db_event: Event = session.scalars(select(Event).where(Event.id == event.id)).unique().one()
    assert len(db_event.get_schema().parameters) == 1
    assert db_event.get_schema().description == 'desc_event'
    assert db_event.get_schema().parameters[0].name == 'param'
    assert db_event.get_schema().parameters[0].type == ParameterType.STRING
    assert db_event.get_schema().parameters[0].is_gdpr is True
    assert db_event.get_schema().parameters[0].description == 'desc_param'
    assert db_event.get_schema().parameters[0].introduced_at_version == 0