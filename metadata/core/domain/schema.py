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
from datetime import datetime
from enum import Enum
import re
from typing import List, Tuple
from metadata.core.domain.common import BaseEntity, EntityError

from metadata.core.domain.status import Status


class ParameterType(str, Enum):
    NUMBER = 'number'
    BOOLEAN = 'boolean'
    INTEGER = 'integer'
    DATE = 'date'
    DATETIME = 'datetime'
    STRING = 'string'

    MAP_NUMBER = 'map<string,number>'
    MAP_BOOLEAN = 'map<string,boolean>'
    MAP_INTEGER = 'map<string,integer>'
    MAP_DATE = 'map<string,date>'
    MAP_DATETIME = 'map<string,datetime>'
    MAP_STRING = 'map<string,string>'

    def __composite_values__(self):
        return (self.value,)


@dataclass(kw_only=True)
class RawSchema(BaseEntity):
    path: str
    schema: str
    status: Status = field(init=False)
    created_at: datetime = field(init=False)
    status_updated_at: datetime = field(init=False)

    def __post_init__(self):
        self.status = Status.NOT_READY
        self.created_at = datetime.utcnow()
        self.status_updated_at = datetime.utcnow()

    def _identity(self) -> Tuple | None:
        return (self.path,)

    def set_status(self, status: Status):
        self.status = status
        self.status_updated_at = datetime.utcnow()


@dataclass(kw_only=True)
class SchemaParameter(BaseEntity):
    id: int | None = field(init=False, default=None)
    name: str
    type: ParameterType
    introduced_at_version: int
    alias: str | None = None
    description: str | None = None
    is_gdpr: bool = False
    is_gdpr_updated_at: datetime = field(init=False)
    created_at: datetime = field(init=False)

    def _valid_name(self, name: str):
        if not re.match(r'^[a-z][a-z0-9]+(_[a-z0-9]+)*$', name):
            return False
        if len(name) > 50:
            return False
        return True

    def __post_init__(self):
        self.is_gdpr_updated_at = datetime.utcnow()
        self.created_at = datetime.utcnow()
        if not self._valid_name(self.name):
            raise EntityError(f'Invalid event name {self.name}')

    def _identity(self) -> Tuple | None:
        return (self.id,)

    def get_alias(self) -> str:
        if self.alias:
            return self.alias
        return self.name.replace('_', ' ').title()


@dataclass(kw_only=True)
class Schema(BaseEntity):
    id: int | None = field(init=False, default=None)
    parameters: List[SchemaParameter]
    vendor: str
    name: str
    alias: str | None = None
    description: str | None = None
    created_at: datetime = field(init=False)

    def _valid_name(self, name: str):
        if not re.match(r'^[a-z][a-z0-9]+(_[a-z0-9]+)*$', name):
            return False
        if len(name) > 50:
            return False
        return True

    def __post_init__(self):
        self.created_at = datetime.utcnow()
        if not self._valid_name(self.name):
            raise EntityError(f'Invalid schema name {self.name}')

    def _identity(self) -> Tuple | None:
        return (self.id,)

    def add_parameters(self, parameters: List[SchemaParameter]):
        for parameter in parameters:
            if any(p for p in self.parameters if p.name == parameter.name):
                raise EntityError(f'Cannot add parameter name {parameter.name} for schema {self.name} as it already exists!')
            self.parameters.append(parameter)

    def get_parameter_by_name(self, name: str) -> SchemaParameter:
        try:
            return next(p for p in self.parameters if p.name == name)
        except StopIteration:
            raise EntityError(f'Parameter name {name} for schema {self.name} does not exist!')

    def get_parameters_for_version(self, version: int) -> List[SchemaParameter]:
        return [p for p in self.parameters if p.introduced_at_version <= version]

    @property
    def current_version(self) -> int:
        if len(self.parameters) == 0:
            return 0
        return max(self.parameters, key=lambda x: x.introduced_at_version).introduced_at_version

    @property
    def next_expected_version(self):
        if not self.id:
            return 0
        return self.current_version + 1

    def get_alias(self) -> str:
        if self.alias:
            return self.alias
        return self.name.replace('_', ' ').title()

