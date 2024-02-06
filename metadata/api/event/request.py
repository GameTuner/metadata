from dataclasses import dataclass, field
from typing import List
from metadata.core.domain.schema import ParameterType


@dataclass(frozen=True)
class CreateParameterDTO:
    name: str
    type: ParameterType
    introduced_at_version: int
    alias: str = None
    description: str = None
    is_gdpr: bool = False


@dataclass(frozen=True)
class UpdateParameterDTO:
    name: str
    is_gdpr: bool
    alias: str = None
    description: str = None


@dataclass(frozen=True)
class CreateOrUpdateEventDTO:
    name: str
    alias: str = None
    description: str = None
    existing_parameters: List[UpdateParameterDTO] = field(default_factory=list)
    new_parameters: List[CreateParameterDTO] = field(default_factory=list)