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

from dataclasses import dataclass
from typing import Dict, List
from metadata.core.domain.app import App, AppId
from metadata.core.domain.common import InternalError
from metadata.core.domain.event import AtomicParameter, Event, EventContext


@dataclass(frozen=True)
class EventsByApp:
    atomic_parameters: List[AtomicParameter]
    event_contexts: List[EventContext]
    non_embedded_event_contexts: List[EventContext]
    embedded_event_contexts: List[EventContext]
    events_by_app: Dict[AppId, List[Event]]
    apps_by_id: Dict[AppId, App]


    def __post_init__(self):
        for app_id in self.events_by_app:
            if app_id not in self.apps_by_id:
                raise InternalError(f'Got events for {app_id} but no app')

    def get_events(self, app_id: AppId) -> List[Event]:
        return self.events_by_app[app_id]

    def get_gdpr_context_parameter_names_by_context_name(self) -> Dict[str, List[str]]:
        gdpr_context_parameters = {}
        for context in self.embedded_event_contexts:
            for parameter in context.get_schema().parameters:
                if parameter.is_gdpr:
                    if context.get_schema().name not in gdpr_context_parameters:
                        gdpr_context_parameters[context.get_schema().name] = []
                    gdpr_context_parameters[context.get_schema().name].append(parameter.name)
        return gdpr_context_parameters

    def get_gdpr_event_parameter_names_by_event_name(self, app_id: AppId) -> Dict[str, List[str]]:
        gdpr_event_parameters = {}
        for event in self.events_by_app[app_id]:
            for parameter in event.get_schema().parameters:
                if parameter.is_gdpr:
                    if event.get_schema().name not in gdpr_event_parameters:
                        gdpr_event_parameters[event.get_schema().name] = []
                    gdpr_event_parameters[event.get_schema().name].append(parameter.name)
        return gdpr_event_parameters

    def get_gdpr_atomic_parameter_names(self) -> List[str]:
        return [a.name for a in self.atomic_parameters if a.is_gdpr]