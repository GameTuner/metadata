from typing import Callable, ContextManager, List
from sqlalchemy.exc import IntegrityError, NoResultFound
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session
from metadata.api.event.request import CreateOrUpdateEventDTO
from metadata.api.event.response import PublicEventDTO, PublicEventListDTO, PublicEventParameterDTO, PublicEventSystemParameterDTO, PublicEventViewDTO
from metadata.core.domain.app import AppId
from metadata.core.domain.common import EntityError, EntityNotFound
from metadata.core.domain.event import AtomicParameter, Event, EventContext
from metadata.core.domain.schema import ParameterType, Schema, SchemaParameter
from metadata.core.domain.status import Status
from hashlib import md5



class EventService:
    def __init__(self, db_session: Callable[[], ContextManager[Session]]):
        self.db_session = db_session

    def create_or_update_event(self, app_id: AppId, create_event_request: CreateOrUpdateEventDTO) -> Event:
        with self.db_session() as session:
            # avoid concurrent updates
            # pg_try_advisory_xact_lock needs 32 bit integer
            db_lock = self.get_hash_int32(f"{app_id}.{create_event_request.name}")
            session.execute(select([func.pg_try_advisory_xact_lock(db_lock)]))

            event: Event = session.scalars(
                select(Event).where(and_(
                    Event.app_id == app_id,
                    Event.schema_id.in_(select(Schema.id).where(Schema.name == create_event_request.name))
                ))).unique().one_or_none()

            if event:
                schema = event.get_schema()
                schema.description = create_event_request.description
                for parameter in create_event_request.existing_parameters:
                    existing_parameter = schema.get_parameter_by_name(parameter.name)
                    existing_parameter.description = parameter.description
                    existing_parameter.alias = parameter.alias
                    existing_parameter.is_gdpr = parameter.is_gdpr
            else:
                event = Event.create_game_specific(app_id=app_id, name=create_event_request.name, description=create_event_request.description, alias=create_event_request.alias)
                session.add(event)

            atomic_parameters={atomic.name for atomic in session.scalars(select(AtomicParameter)).all()}
            if create_event_request.new_parameters:
                for parameter in create_event_request.new_parameters:
                    if parameter.name in atomic_parameters:
                        raise EntityError('Event parameter must not be equal to any current atomic parameter')
                event.add_parameters([SchemaParameter(
                    name=parameter.name,
                    type=parameter.type,
                    introduced_at_version=parameter.introduced_at_version,
                    description=parameter.description,
                    alias=parameter.alias,
                    is_gdpr=parameter.is_gdpr,
                ) for parameter in create_event_request.new_parameters])

                if event.status == Status.SUCCESS:
                    event.set_status(Status.NEEDS_UPDATE)

            try:
                session.commit()
            except IntegrityError as exc:
                raise EntityError() from exc
            return event

    def get_event_by_name(self, app_id: AppId, event_name: str) -> PublicEventDTO:
        with self.db_session() as session:
            try:
                event: Event = session.scalars(
                    select(Event).where(and_(
                        Event.app_id == app_id,
                        Event.schema_id.in_(select(Schema.id).where(Schema.name == event_name)))
                )).unique().one()

                schema = event.get_schema()
                return PublicEventDTO(
                    name=schema.name,
                    alias=schema.get_alias(),
                    datasource_id=event.datasource_id,
                    description=schema.description,
                    status=event.status,
                    is_common=event.is_common,
                    parameters=[PublicEventParameterDTO(
                        name=param.name,
                        alias=param.get_alias(),
                        description=param.description,
                        type=param.type,
                        is_gdpr=param.is_gdpr,
                        introduced_at_version=param.introduced_at_version
                    ) for param in schema.parameters]
                )
            except NoResultFound as exc:
                raise EntityNotFound() from exc

    def get_all_event_views(self, app_id: AppId) -> PublicEventListDTO:
        with self.db_session() as session:
            events = session.scalars(select(Event).where(Event.app_id == app_id)).unique().all()
            atomic_parameters: List[AtomicParameter] = session.scalars(select(AtomicParameter)).all()
            event_contexts: List[EventContext] = session.scalars(select(EventContext).where(EventContext.embedded_in_event == True)).unique().all()

            system_parameters = {
                'Atomic': [PublicEventSystemParameterDTO(
                    name=a.name,
                    alias=a.get_alias(),
                    description=a.description,
                    type=a.type,
                    is_gdpr=a.is_gdpr) for a in atomic_parameters]
            }
            for event_context in event_contexts:
                system_parameters[event_context.get_alias()] = [PublicEventSystemParameterDTO(
                    name=param.name,
                    alias=param.get_alias(),
                    description=param.description,
                    type=param.type,
                    is_gdpr=param.is_gdpr) for param in event_context.schema.parameters
                ]

            return PublicEventListDTO(
                events=[PublicEventViewDTO(e.schema.name, e.schema.get_alias(), e.schema.description, e.datasource_id) for e in events],
                parameter_types=list(ParameterType),
                system_parameters=system_parameters
            )

    def get_hash_int32(self, string_to_hash: str) -> int:
        hash_obj = md5(string_to_hash.encode())
        # Get the first 4 bytes of the hash as an integer
        hash_bytes = hash_obj.digest()[:4]
        hash_int32 = int.from_bytes(hash_bytes, byteorder='big', signed=False)
        # Reduce the hash value to a smaller range using the modulo operator
        hash_int32 = hash_int32 % 2147483647
        # Convert the hash value to a signed 32-bit integer
        if hash_int32 > 0x7fffffff:
            hash_int32 -= 0x100000000

        return hash_int32



