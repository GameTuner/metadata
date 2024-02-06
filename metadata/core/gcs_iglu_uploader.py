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

from google.cloud import storage
from metadata.core.domain.iglu import IgluSchema


class GcsIgluUploader:
    def __init__(self, gcp_schema_bucket: str) -> None:
        self._storage_client = storage.Client()
        self._bucket = self._storage_client.bucket(gcp_schema_bucket)

    def upload(self, iglu_schema: IgluSchema):
        blob = self._bucket.blob(f'schemas/{iglu_schema.path}')
        blob.upload_from_string(iglu_schema.schema_to_json_string())
