from collections import defaultdict
from datetime import date
from typing import Callable, ContextManager, List
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy.exc import IntegrityError
from metadata.api.app.internal.domain import EventsByApp
from metadata.api.app.request import CreateAppDTO
from metadata.core.domain.app import App, AppId, Datasource, Organization
from metadata.core.domain.common import EntityError, EntityNotFound
from metadata.core.domain.event import AtomicParameter, Event, EventContext
from metadata.core.domain.status import Status



class AppService:
    def __init__(self, db_session: Callable[[], ContextManager[Session]]):
        self.db_session = db_session

    def register(self, request: CreateAppDTO) -> App:
        with self.db_session() as session:
            organization = session.scalars(select(Organization).where(Organization.name == request.organization)).unique().one()
            app = App(id=AppId(request.app_id), organization=organization, timezone=request.timezone, has_data_from=request.has_data_from)
            session.add(app)

            try:
                session.commit()
            except IntegrityError as exc:
                raise EntityError() from exc
        return app

    def get_all_success(self) -> List[App]:
        with self.db_session() as session:
            return session.scalars(select(App).where(App.status != Status.NOT_READY)).unique().all()

    def get_by_app_id(self, app_id: AppId) -> App:
        with self.db_session() as session:
            try:
                return session.scalars(select(App).where(App.id == app_id)).unique().one()
            except NoResultFound as exc:
                raise EntityNotFound() from exc

    def update_datasource_freshness(self, app_id: AppId, datasource_id: str, has_data_up_to: date) -> App:
        with self.db_session() as session:
            try:
                app: App = session.scalars(select(App).where(App.id == app_id)).unique().one()
            except NoResultFound as exc:
                raise EntityNotFound() from exc

            datasource = app.get_datasource(datasource_id)
            if not datasource:
                datasource = Datasource(id=datasource_id, app_id=app.id, has_data_from=has_data_up_to, has_data_up_to=has_data_up_to)
                app.add_datasource(datasource)
            else:
                datasource.update_data_freshness(has_data_up_to)
            session.commit()
        return app

    def get_all_success_events_by_app(self) -> EventsByApp:
        with self.db_session() as session:
            apps: List[App] = session.scalars(select(App).where(App.status == Status.SUCCESS)).unique().all()
            app_ids = {app.id: app for app in apps}
            events: List[Event] = [e for e in session.scalars(select(Event)\
                # filter by app ids to avoid race condition where some app became success in the mean time
                .where(Event.status != Status.NOT_READY)).unique().all() if e.app_id in app_ids]
            atomic_parameters: List[AtomicParameter] = session.scalars(select(AtomicParameter)).all()
            event_contexts: List[EventContext] = session.scalars(select(EventContext).where(EventContext.embedded_in_event == False)).unique().all()
            non_embedded_event_contexts: List[EventContext] = session.scalars(select(EventContext).where(EventContext.embedded_in_event == False)).unique().all()
            embedded_event_contexts: List[EventContext] = session.scalars(select(EventContext).where(EventContext.embedded_in_event == True)).unique().all()


        events_by_app_id = defaultdict(list)
        for event in events:
            events_by_app_id[event.app_id].append(event)

        return EventsByApp(
            atomic_parameters=atomic_parameters,
            event_contexts=event_contexts,
            non_embedded_event_contexts=non_embedded_event_contexts,
            embedded_event_contexts=embedded_event_contexts,
            events_by_app=events_by_app_id,
            apps_by_id=app_ids
        )
