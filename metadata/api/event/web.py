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

from fastapi import APIRouter, Depends
from metadata.api.app.service import AppService
from metadata.api.event.request import CreateOrUpdateEventDTO
from metadata.api.event.service import EventService
from metadata.core.domain.app import AppId
from metadata.logging.router import LoggingRoute
from metadata import dependencies

router = APIRouter(route_class=LoggingRoute, tags=["event"])


@router.get("/api/v1/apps/{app_id}/events")
def get_events(app_id: str, session_factory = Depends(dependencies.session_factory)):
    app = AppService(session_factory).get_by_app_id(AppId(app_id))
    return EventService(session_factory).get_all_event_views(app.id)


@router.get("/api/v1/apps/{app_id}/events/{event_name}")
def get_event(app_id: str, event_name: str, session_factory = Depends(dependencies.session_factory)):
    app = AppService(session_factory).get_by_app_id(AppId(app_id))
    return EventService(session_factory).get_event_by_name(app.id, event_name)


@router.post("/api/v1/apps/{app_id}/events")
def create_or_update_event(app_id: str, request: CreateOrUpdateEventDTO, session_factory = Depends(dependencies.session_factory)):
    app = AppService(session_factory).get_by_app_id(AppId(app_id))
    EventService(session_factory).create_or_update_event(app.id, request)
    return "ok"
