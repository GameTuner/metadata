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

from dataclasses import InitVar, dataclass, field
from metadata.core.domain.common import BaseEntity, EntityError

@dataclass(frozen=True)
class AppId:
    value: str

    def __post_init__(self):
        if not self.value:
            raise EntityError('Must set app id')
        if not all(c.islower() for c in self.value):
            raise EntityError('App id must have all lowercase letters')

    def __composite_values__(self):
        return (self.value,)