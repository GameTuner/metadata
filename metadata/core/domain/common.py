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

from abc import ABC, abstractmethod
from typing import Tuple

class EntityNotFound(Exception):
    pass

class EntityError(Exception):
    pass

class InternalError(Exception):
    pass

class BaseEntity(ABC):
    @abstractmethod
    def _identity(self) -> Tuple | None:
        """
        Return a tuple of values that represent primary key of entity.
        Returns None if entity does not have a primary key yet.
        """

    def __eq__(self, other) -> bool:
        if type(other) is type(self) and self._identity() and other._identity:
            return self._identity() == other._identity()
        else:
            return False

    def __hash__(self):
        if not self._identity():
            raise ValueError('Cannot hash entity without identity')
        return hash(self._identity())
