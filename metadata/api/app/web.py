from datetime import date
from typing import List
from fastapi import APIRouter, Depends
from metadata.api.app.request import CreateAppDTO
from metadata.api.app.response import AllAppsConfigDTO, AppDTO
from metadata.core.domain.app import AppId
from metadata.api.app.service import AppService
from metadata.logging.router import LoggingRoute
from metadata import dependencies

router = APIRouter(route_class=LoggingRoute, tags=["app"])


@router.post("/api/v1/apps")
def register(request: CreateAppDTO, session_factory = Depends(dependencies.session_factory)):
    app = AppService(session_factory).register(request)
    return app.api_key


@router.get("/api/v1/apps")
def apps(session_factory = Depends(dependencies.session_factory)) -> List[AppDTO]:
    app_configs = AppService(session_factory).get_all_success()
    return [AppDTO.from_domain_model(app_config) for app_config in app_configs]


@router.get("/api/v1/apps/{app_id}")
def app_by_id(app_id: str, session_factory = Depends(dependencies.session_factory)):
    app_config = AppService(session_factory).get_by_app_id(AppId(app_id))
    return AppDTO.from_domain_model(app_config)


@router.get("/api/v1/apps-detailed")
def apps_detailed(session_factory = Depends(dependencies.session_factory)) -> AllAppsConfigDTO:
    events_by_app = AppService(session_factory).get_all_success_events_by_app()
    app_list = AppService(session_factory).get_all_success()
    return  AllAppsConfigDTO.from_domain_model(app_list, events_by_app)


@router.put("/api/v1/apps/{app_id}/datasource-freshness/{datasource_id}/{has_data_up_to_date}")
def update_datasource_freshness(app_id: str, datasource_id: str, has_data_up_to_date: date, session_factory = Depends(dependencies.session_factory)):
    AppService(session_factory).update_datasource_freshness(AppId(app_id), datasource_id, has_data_up_to_date)
    return "ok"