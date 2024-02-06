from typing import Callable, ContextManager, List
import google
from google.cloud import bigquery
from sqlalchemy import and_, select
from sqlalchemy.orm import Session
from fastapi.logger import logger
from metadata.core.domain.app import App
from metadata.core.domain.event import AtomicParameter, CommonEvent, Event, EventContext
from metadata.core.domain.status import Status
from metadata.api.app.internal import bigquery_all_apps, bigquery_single_app
from metadata.core.event_tables_creator import BigQueryEventTablesCreator
from metadata.core.gcs_iglu_uploader import GcsIgluUploader
from metadata.core.database import utils


class AppMaintainer:
    def __init__(self, db_session: Callable[[], ContextManager[Session]], dry_run: bool):
        self.db_session = db_session
        self.dry_run = dry_run

    def process_non_success(self, gcp_schema_bucket: str, bigquery_region: str):

        with self.db_session() as session:
            utils.maintainer_lock(session)
            apps: List[App] = session.scalars(select(App).where(App.status != Status.SUCCESS)).unique().all()
            logger.info(f"Got {len(apps)} apps to process")
            if apps:
                if not self.dry_run:
                    event_tables_creator = BigQueryEventTablesCreator(bigquery_region)
                    iglu_uploader = GcsIgluUploader(gcp_schema_bucket)

                    credentials, _ = google.auth.default()
                    bigquery_client = bigquery.Client(credentials=credentials)
                    bigquery_all_apps.process(bigquery_client, bigquery_region)

                event_contexts: List[EventContext] = session.scalars(select(EventContext)).unique().all()
                atomic_parameters = session.scalars(select(AtomicParameter)).all()
                common_events: List[CommonEvent] = session.scalars(select(CommonEvent)).unique().all()
                for idx, app in enumerate(apps):
                    app: App
                    logger.info(f"Processing app {app.id} [{idx + 1} / {len(apps)}]")
                    self._add_missing_common_events(session, common_events, app)
                    if not self.dry_run:
                        bigquery_single_app.process(bigquery_client, bigquery_region, app)
                        self._process_event_contexts(event_tables_creator, iglu_uploader, event_contexts, atomic_parameters, app)
                    app.set_status(Status.SUCCESS)
                    session.commit()
            logger.info("Processed apps")

    def _process_event_contexts(self, event_tables_creator, iglu_uploader, event_contexts, atomic_parameters, app):
        for event_context in event_contexts:
            event_tables_creator.maintain_event_table(app.id, event_context.get_schema(), event_context.get_schema().parameters, atomic_parameters, [])

            for iglu_schema in event_context.to_iglu_schemas():
                iglu_uploader.upload(iglu_schema)

    def _add_missing_common_events(self, session: Session, common_events: List[CommonEvent], app: App):
        app_common_events = {e.parent_common_event.id for e in session.scalars(select(Event).where(and_(Event.app_id == app.id, Event.parent_common_event != None))).unique().all()}
        for common_event in common_events:
            if common_event.id in app_common_events:
                continue
            common_event: CommonEvent
            schema = common_event.get_app_schema(app)
            session.add(schema)
            event = Event(
                app_id=app.id,
                schema=schema,
                parent_common_event=common_event,
                parent_common_event_version=common_event.schema.current_version,
            )
            session.add(event)


