from dataclasses import dataclass
from datetime import date
from metadata.core.domain.app import Timezone


@dataclass(frozen=True)
class CreateAppDTO:
    app_id: str
    organization: str
    timezone: Timezone = Timezone("UTC")
    has_data_from: date = None