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

from threading import Thread
import time
from fastapi.logger import logger
from metadata.api.app.maintainer import AppMaintainer
from metadata.api.event.maintainer import EventMaintainer
from metadata.api.organization.maintainer import OrganizationMaintainer
from metadata.api.raw_schema.maintainer import RawSchemaMaintainer
from metadata import monitoring


maintainer_errors_counter = monitoring.meter.create_counter(
    name="maintainer_errors",
    description="Number of maintainer errors",
    unit="1")


def _run_maintainer(session_factory, gcp_schema_bucket: str, bigquery_region: str, dry_run: bool):
    while True:
        try:
            RawSchemaMaintainer(session_factory, dry_run).process_non_success(gcp_schema_bucket)
            OrganizationMaintainer(session_factory, dry_run).process_non_success()
            AppMaintainer(session_factory, dry_run).process_non_success(gcp_schema_bucket, bigquery_region)
            EventMaintainer(session_factory, dry_run).process_non_success(gcp_schema_bucket, bigquery_region)
        except:
            maintainer_errors_counter.add(1)
            logger.exception("Maintainer failed")
        time.sleep(60)


def start(session_factory, gcp_schema_bucket: str, bigquery_region: str, dry_run: bool):
    _maintainer_thread = Thread(target=_run_maintainer, args=(session_factory, gcp_schema_bucket, bigquery_region, dry_run))
    _maintainer_thread.daemon = True
    _maintainer_thread.start()