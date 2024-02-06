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
