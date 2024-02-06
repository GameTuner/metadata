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

from google.cloud import bigquery
from metadata.core.domain.app import App
from metadata.api.app.internal import bigquery_ddl


def create_authorized_views(bigquery_client: bigquery.Client, dataset_name: str, app: App):
    source_dataset = bigquery_client.get_dataset(f'{bigquery_client.project}.{dataset_name}')
    client_dataset = bigquery.Dataset(f'{app.organization.gcp_project_id}.{dataset_name}')

    source_tables = {t for t in bigquery_client.list_tables(f'{bigquery_client.project}.{dataset_name}')}
    client_table_ids = {t.table_id for t in bigquery_client.list_tables(f'{app.organization.gcp_project_id}.{dataset_name}')}

    access_entries = source_dataset.access_entries

    for source_table in source_tables:
        bigquery_client.query(f"""CREATE OR REPLACE VIEW `{app.organization.gcp_project_id}.{dataset_name}.{source_table.table_id}` AS
                                  SELECT * FROM `{bigquery_client.project}.{dataset_name}.{source_table.table_id}`""").result()
        if source_table.table_id not in client_table_ids:
            view = bigquery.Table(client_dataset.table(source_table.table_id))
            access_entries.append(bigquery.AccessEntry(None, "view", view.reference.to_api_repr()))

    source_dataset.access_entries = access_entries
    source_dataset = bigquery_client.update_dataset(source_dataset, ["access_entries"])

def create_common_authorized_views(bigquery_client: bigquery.Client, app: App):
    source_dataset = bigquery_client.get_dataset(f'{bigquery_client.project}.gametuner_monitoring')
    client_dataset = bigquery.Dataset(f'{app.organization.gcp_project_id}.gametuner_monitoring')
    access_entries = source_dataset.access_entries

    bad_events_table_name = f'v_enrich_bad_events_{app.id.value}'
    bad_events_table = bigquery_ddl.get_table_if_exists(bigquery_client, client_dataset, bad_events_table_name)

    if not bad_events_table:
        bigquery_client.query(f"""CREATE OR REPLACE VIEW `{app.organization.gcp_project_id}.gametuner_monitoring.{bad_events_table_name}` AS
                                    SELECT * FROM `{bigquery_client.project}.gametuner_monitoring.v_enrich_bad_events`
                                    WHERE app_id = '{app.id.value}'""").result()
        view = bigquery.Table(client_dataset.table(bad_events_table_name))
        access_entries.append(bigquery.AccessEntry(None, "view", view.reference.to_api_repr()))

        source_dataset.access_entries = access_entries
        source_dataset = bigquery_client.update_dataset(source_dataset, ["access_entries"])


