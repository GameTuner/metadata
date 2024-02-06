from dataclasses import dataclass
from typing import Dict, List
from metadata.core.domain.schema import ParameterType
from metadata.core.domain.status import Status


@dataclass(frozen=True)
class PublicEventSystemParameterDTO:
    name: str
    alias: str
    description: str | None
    type: ParameterType
    is_gdpr: bool

@dataclass(frozen=True)
class PublicEventParameterDTO:
    name: str
    alias: str
    description: str | None
    type: ParameterType
    is_gdpr: bool
    introduced_at_version: int


@dataclass(frozen=True)
class PublicEventDTO:
    name: str
    alias: str
    datasource_id: str
    description: str | None
    status: Status
    is_common: bool
    parameters: List[PublicEventParameterDTO]


@dataclass(frozen=True)
class PublicEventViewDTO:
    name: str
    alias: str
    description: str | None
    datasource_id: str


@dataclass(frozen=True)
class PublicEventListDTO:
    events: List[PublicEventViewDTO]
    parameter_types: List[ParameterType]
    system_parameters: Dict[str, List[PublicEventSystemParameterDTO]]