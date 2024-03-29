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
from metadata.core.domain.iglu import IgluSchema

from metadata.core.domain.schema import RawSchema
from metadata.core.domain.status import Status
from metadata.core.gcs_iglu_uploader import GcsIgluUploader
from metadata.core.database import utils


class RawSchemaMaintainer:
    def __init__(self, db_session: Callable[[], ContextManager[Session]], dry_run: bool):
        self.db_session = db_session
        self.dry_run = dry_run

    def process_non_success(self, gcp_schema_bucket: str):
        with self.db_session() as session:
            utils.maintainer_lock(session)

            raw_schemas: List[RawSchema] = session.scalars(select(RawSchema).filter(RawSchema.status != Status.SUCCESS)).all()
            if raw_schemas:
                logger.info(f"Got {len(raw_schemas)} raw schemas to process")
                for idx, raw_schema in enumerate(raw_schemas):
                    raw_schema: RawSchema
                    if not self.dry_run:
                        iglu_uploader = GcsIgluUploader(gcp_schema_bucket)
                        iglu_uploader.upload(IgluSchema(
                            path=raw_schema.path,
                            schema=raw_schema.schema
                        ))
                    logger.info(f"Processing raw schema {raw_schema.path} [{idx + 1} / {len(raw_schemas)}]")
                    raw_schema.set_status(Status.SUCCESS)
                    session.commit()

            logger.info("Processed raw schemas")