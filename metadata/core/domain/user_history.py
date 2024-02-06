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

from dataclasses import dataclass, field
from typing import List, Tuple
from datetime import datetime
from metadata.core.domain.common import BaseEntity
from metadata.core.domain.app_id import AppId
from metadata.core.domain.event import Event

@dataclass(kw_only=True)
class MaterializedColumn(BaseEntity):
    id: int | None = field(init=False, default=None)
    column_name: str
    app_id: AppId
    datasource_id: str
    event: Event
    select_expression: str
    data_type: str
    user_history_formula: str | None = None
    totals: bool = True
    can_filter: bool = True
    can_group_by: bool = False
    materialized_from: datetime = field(init=False)
    hidden: bool = False
    dataset: str | None = None

    def _identity(self) -> Tuple | None:
        return (self.id,)

    def __post_init__(self):
        self.materialized_from = datetime.utcnow()




