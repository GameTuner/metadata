from abc import ABC, abstractmethod
from dataclasses import dataclass, field
import dataclasses
from datetime import datetime
from typing import List, Set, Tuple
from metadata.core.domain.app import App, AppId
from metadata.core.domain.common import BaseEntity
from metadata.core.domain.iglu import IgluSchema
from metadata.core.domain.schema import ParameterType, Schema, SchemaParameter
from metadata.core.domain.status import Status
from metadata.core.domain.common import EntityError


@dataclass(kw_only=True)
class AtomicParameter(BaseEntity):
    name: str
    type: ParameterType
    description: str | None = None
    is_gdpr: bool = False
    created_at: datetime = field(init=False)

    def __post_init__(self):
        self.created_at = datetime.utcnow()

    def _identity(self) -> Tuple | None:
        return (self.name,)

    def get_alias(self) -> str:
        return self.name.replace('_', ' ').title()


# TODO validation that parameters cant start with custom_
@dataclass(kw_only=True)
class CommonEvent(BaseEntity):
    id: int | None = field(init=False, default=None)
    schema: Schema

    def __post_init__(self):
        if self.schema.name.startswith('ctx_') or self.schema.name.endswith('_context'):
            raise EntityError(f"Event schema {self.schema.name} must not start with ctx_ or end with _context")

    def _identity(self) -> Tuple | None:
        return (self.id,)

    def get_app_schema(self, app: App) -> Schema:
        return Schema(parameters=[], vendor=app.event_vendor, name=self.schema.name,
                      description=self.schema.description)


class IgluSchemaGenerator(ABC):
    @abstractmethod
    def get_schema(self) -> Schema:
        pass

    @abstractmethod
    def override_url_schema_name(self):
        """
        Most schemas generate iglu url from vendor, name and version.
        Event contexts, for example, ctx_event_context use event_context instead of ctx_event_context so now we have to support that.
        """
        return None

    def versions(self) -> Set[int]:
        if self.get_schema().parameters:
            return {p.introduced_at_version for p in self.get_schema().parameters}
        return {0}

    def to_iglu_schemas(self) -> List[IgluSchema]:
        event_like_schema = self.get_schema()
        return [IgluSchema.from_schema(event_like_schema, event_like_schema.get_parameters_for_version(version),
                                       version, override_url_schema_name=self.override_url_schema_name())
                for version in self.versions()]


@dataclass(kw_only=True)
class EventContext(BaseEntity, IgluSchemaGenerator):
    id: int | None = field(init=False, default=None)
    schema: Schema
    embedded_in_event: bool
    status: Status = field(init=False)
    status_updated_at: datetime = field(init=False)

    def __post_init__(self):
        self.status = Status.NOT_READY
        self.status_updated_at = datetime.utcnow()
        if not self.schema.name.startswith('ctx_') or not self.schema.name.endswith('_context'):
            raise EntityError(f"Event schema {self.schema.name} must start with ctx_ and end with _context")

    def _identity(self) -> Tuple | None:
        return (self.id,)

    def override_url_schema_name(self):
        return self.schema.name[len("ctx_"):]

    def get_schema(self) -> Schema:
        return self.schema

    def get_alias(self) -> str:
        return self.override_url_schema_name().replace('_', ' ').title()


@dataclass(kw_only=True)
class Event(BaseEntity, IgluSchemaGenerator):
    id: int | None = field(init=False, default=None)
    app_id: AppId
    schema_id: int = field(init=False, default=None)
    schema: Schema
    parent_common_event: CommonEvent | None = None
    parent_common_event_version: int | None = None
    status: Status = field(init=False)
    status_updated_at: datetime = field(init=False)

    def __post_init__(self):
        self.status = Status.NOT_READY
        self.status_updated_at = datetime.utcnow()
        if self.schema.name.startswith('ctx_') or self.schema.name.endswith('_context'):
            raise EntityError(f"Event schema {self.schema.name} must not start with ctx_ or end with _context")

    def _identity(self) -> Tuple | None:
        return (self.id,)

    def override_url_schema_name(self):
        return None

    @classmethod
    def create_game_specific(cls, app_id: AppId, name: str, description: str | None = None, alias: str | None = None) -> 'Event':
        return cls(
            app_id=app_id,
            schema=Schema(
                parameters=[],
                vendor=f"com.algebraai.gametuner.gamespecific.{app_id.value}",
                name=name,
                alias=alias,
                description=description
            ),
        )

    def get_schema(self) -> Schema:
        parameters = []
        if self.is_common:
            parameters = []
            for parameter in self.parent_common_event.schema.parameters:
                if parameter.introduced_at_version <= self.parent_common_event_version:
                    parameters.append(dataclasses.replace(parameter, introduced_at_version = 0))
            parameters.extend(self.schema.parameters)
            return dataclasses.replace(self.schema, parameters=parameters)
        else:
            return self.schema

    def add_parameters(self, parameters: List[SchemaParameter]):
        if not parameters:
            return
        expected_version = self.schema.next_expected_version
        for parameter in parameters:
            if parameter.introduced_at_version != expected_version:
                raise EntityError(f'Invalid version {parameter.introduced_at_version}, expected {expected_version}')
            if self.is_common and not parameter.name.startswith('custom_'):
                raise EntityError('Parameters of common events must start with custom_ prefix')
        self.schema.add_parameters(parameters)

    def set_status(self, status: Status):
        self.status = status
        self.status_updated_at = datetime.utcnow()

    @property
    def is_common(self) -> bool:
        return self.parent_common_event is not None

    @property
    def datasource_id(self) -> bool:
        return f'events_{self.schema.name}'
