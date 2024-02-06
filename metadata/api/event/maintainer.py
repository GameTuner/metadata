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

from typing import Callable, ContextManager, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from fastapi.logger import logger
from metadata.core.domain.app import App
from metadata.core.event_tables_creator import BigQueryEventTablesCreator
from metadata.core.gcs_iglu_uploader import GcsIgluUploader
from metadata.core.domain.event import AtomicParameter, Event, EventContext
from metadata.core.domain.status import Status
from metadata.core.database import utils


class EventMaintainer:
    def __init__(self, db_session: Callable[[], ContextManager[Session]], dry_run: bool):
        self.db_session = db_session
        self.dry_run = dry_run

    def process_non_success(self, gcp_schema_bucket: str, bigquery_region: str):

        with self.db_session() as session:
            utils.maintainer_lock(session)

            events: List[Event] = session.scalars(select(Event).where(Event.status != Status.SUCCESS)).unique().all()

            logger.info(f"Got {len(events)} events to process")
            if events:
                atomic_parameters = session.scalars(select(AtomicParameter)).all()
                event_contexts = session.scalars(select(EventContext).where(EventContext.embedded_in_event == True)).unique().all()

                for idx, event in enumerate(events):
                    event: Event
                    logger.info(f"Processing event {event.app_id}.{event.get_schema().name} [{idx + 1} / {len(events)}]")

                    if not self.dry_run:
                        iglu_uploader = GcsIgluUploader(gcp_schema_bucket)
                        event_tables_creator = BigQueryEventTablesCreator(bigquery_region)
                        event_tables_creator.maintain_event_table(event.app_id, event.get_schema(), event.get_schema().parameters, atomic_parameters, event_contexts)

                        for iglu_schema in event.to_iglu_schemas():
                            logger.info(f"Uploading event iglu schema {iglu_schema.path}")
                            iglu_uploader.upload(iglu_schema)

                    event.set_status(Status.SUCCESS)

                    # Mark app for update, so views in client gcp projects get updated when we add new event tables
                    app: App = session.scalars(select(App).where(App.id == event.app_id)).unique().one()
                    if app.status == Status.SUCCESS:
                        app.set_status(Status.NEEDS_UPDATE)
                    session.commit()


            logger.info("Processed events")


