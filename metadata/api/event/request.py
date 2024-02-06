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