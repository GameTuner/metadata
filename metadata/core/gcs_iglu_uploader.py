from google.cloud import storage
from metadata.core.domain.iglu import IgluSchema


class GcsIgluUploader:
    def __init__(self, gcp_schema_bucket: str) -> None:
        self._storage_client = storage.Client()
        self._bucket = self._storage_client.bucket(gcp_schema_bucket)

    def upload(self, iglu_schema: IgluSchema):
        blob = self._bucket.blob(f'schemas/{iglu_schema.path}')
        blob.upload_from_string(iglu_schema.schema_to_json_string())
