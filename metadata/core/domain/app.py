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
from datetime import date, datetime
import random
import string
from typing import List, Tuple
import pytz
from metadata.core.domain.app_id import AppId
from metadata.core.domain.common import BaseEntity, EntityError
from metadata.core.domain.status import Status
from metadata.core.domain.user_history import MaterializedColumn

@dataclass(kw_only=True)
class AppsflyerIntegration(BaseEntity):
    id: int | None = field(init=False, default=None)
    app_id: AppId
    reports: List[str]
    home_folder: str
    app_ids: List[str]
    external_bucket_name: str

    def _identity(self) -> Tuple | None:
        return (self.id,)


@dataclass(kw_only=True)
class GcpProjectPrincipal(BaseEntity):
    organization: 'Organization'
    principal: str

    def _identity(self) -> Tuple | None:
        return (self.organization, self.principal)


@dataclass(kw_only=True)
class AppsflyerCostETLIntegration(BaseEntity):
    id: int | None = field(init=False, default=None)
    app_id: AppId
    bucket_name: str
    reports: List[str]
    android_app_id: str
    ios_app_id: str

    def _identity(self) -> Tuple | None:
        return (self.id,)

@dataclass(kw_only=True)
class StoreITunes(BaseEntity):
    id: int | None = field(init=False, default=None)
    app_id: AppId
    app_sku_id: str
    apple_id: str
    issuer_id: str
    key_id: str
    key_value: str
    vendor_number: str

    def _identity(self) -> Tuple | None:
        return (self.id,)

@dataclass(kw_only=True)
class StoreGooglePlay(BaseEntity):
    id: int | None = field(init=False, default=None)
    app_id: AppId
    app_bundle_id: str
    service_account: str
    report_bucket_name: str

    def _identity(self) -> Tuple | None:
        return (self.id,)

@dataclass(kw_only=True)
class EventBackfillJob(BaseEntity):
    id: int | None = field(init=False, default=None)
    app_id: AppId
    job_name: str
    start_date: date
    end_date: date
    events: bool
    facts: bool
    user_history: bool

    def _identity(self) -> Tuple | None:
        return (self.id,)

@dataclass(kw_only=True)
class Datasource(BaseEntity):
    id: str
    app_id: AppId
    has_data_from: date
    has_data_up_to: date | None = field(default=None)
    materialized_columns: List[MaterializedColumn] = field(init=False, default=None)

    def _identity(self) -> Tuple | None:
        return (self.id,)

    def update_data_freshness(self, has_data_up_to: date):
        if self.has_data_up_to and self.has_data_up_to > has_data_up_to:
            return
        self.has_data_up_to = has_data_up_to


@dataclass(frozen=True)
class Timezone:
    name: str

    def __post_init__(self):
        if self.name not in pytz.all_timezones_set:
            raise EntityError(f'Invalid timezone: {self.name}')

    def __composite_values__(self):
        return (self.name,)


@dataclass(kw_only=True)
class Organization(BaseEntity):
    id: int | None = field(init=False, default=None)
    name: str
    gcp_project_id: str
    created_at: datetime = field(init=False)
    status: Status = field(init=False)
    status_updated_at: datetime = field(init=False)
    gcp_project_principals: List[GcpProjectPrincipal] = field(init=False)

    def _identity(self) -> Tuple | None:
        return (self.id,)

    def __post_init__(self):
        self.status = Status.NOT_READY
        self.created_at = datetime.utcnow()
        self.status_updated_at = datetime.utcnow()
        self.gcp_project_principals = []

    def set_status(self, status: Status):
        self.status = status
        self.status_updated_at = datetime.utcnow()


@dataclass(kw_only=True)
class App(BaseEntity):
    id: AppId
    timezone: Timezone
    organization: Organization
    has_data_from: InitVar[date | None] = field(default=None)
    api_key: str = field(init=False)
    created_at: datetime = field(init=False)
    status: Status = field(init=False)
    status_updated_at: datetime = field(init=False)

    event_backfill_jobs: List[EventBackfillJob] = field(init=False)
    appsflyer_integration: AppsflyerIntegration | None = field(init=False, default=None)
    appsflyer_cost_etl_integration: AppsflyerCostETLIntegration | None = field(init=False, default=None)
    datasources: List[Datasource] = field(init=False)
    store_itunes: StoreITunes | None = field(init=False, default=None)
    store_google_play: StoreGooglePlay | None = field(init=False, default=None)

    def __post_init__(self, has_data_from: date | None):
        self.api_key = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(16))
        self.status = Status.NOT_READY
        self.created_at = datetime.utcnow()
        self.status_updated_at = datetime.utcnow()
        self.event_backfill_jobs = []
        self.datasources = []
        self.bigquery_permissions = []

        if not has_data_from:
            has_data_from = self.created_at.date()
        self.add_datasource(Datasource(id='user_history', app_id=self.id, has_data_from=has_data_from))

    def _identity(self) -> Tuple | None:
        return (self.id,)

    def set_status(self, status: Status):
        self.status = status
        self.status_updated_at = datetime.utcnow()

    def get_datasource(self, datasource_id: str) -> Datasource | None:
        return next((ds for ds in self.datasources if ds.id == datasource_id), None)

    def add_datasource(self, datasource: Datasource):
        if datasource in self.datasources:
            raise EntityError("Datasource already exists!")
        self.datasources.append(datasource)

    @property
    def event_vendor(self):
        return f'com.algebraai.gametuner.gamespecific.{self.id.value}'

    @property
    def close_event_partitions_after_hours(self) -> int:
        return 4

