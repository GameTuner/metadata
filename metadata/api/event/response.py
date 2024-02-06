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