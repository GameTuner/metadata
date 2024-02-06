from enum import Enum

class Status(str, Enum):
    NOT_READY = 'NOT_READY'
    SUCCESS = 'SUCCESS'
    NEEDS_UPDATE = 'NEEDS_UPDATE'

    def __composite_values__(self):
        return self.value,
