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
from google.cloud import bigquery
from google.cloud.bigquery import Dataset
from metadata.api.app.internal import bigquery_ddl, bigquery_iam
from metadata.core.domain.app import App, AppId


@dataclass
class DatasetConfig:
    name: str
    mirror_dataset: bool
    mirror_tables: bool


def _create_fix_tables(bigquery_client: bigquery.Client, fix_dataset: Dataset):
    excluded_unique_ids_table_name = 'excluded_unique_ids'
    table_def = bigquery_ddl.get_table_if_exists(bigquery_client, fix_dataset, excluded_unique_ids_table_name)
    if not table_def:
        # Define the table schema
        bq_table = bigquery.Table(fix_dataset.table(excluded_unique_ids_table_name))
        bq_table.schema = [
            bigquery.SchemaField("unique_id", "STRING"),
            bigquery.SchemaField("inserted_at", "TIMESTAMP", mode="NULLABLE", default_value_expression="CURRENT_TIMESTAMP()"),
            bigquery.SchemaField("reason", "STRING", mode="NULLABLE"),
        ]
        bigquery_client.create_table(bq_table)

def _create_gdpr_delete_request_log(bigquery_client: bigquery.Client, gdpr_dataset: Dataset):
    gdpr_delete_request_log_table_name = 'gdpr_delete_request_log'
    table_def = bigquery_ddl.get_table_if_exists(bigquery_client, gdpr_dataset, gdpr_delete_request_log_table_name)
    if not table_def:
        # Define the table schema
        bq_table = bigquery.Table(gdpr_dataset.table(gdpr_delete_request_log_table_name))
        bq_table.schema = [
            bigquery.SchemaField("unique_id", "STRING"),
            bigquery.SchemaField("deleted_at", "TIMESTAMP", mode="NULLABLE", default_value_expression="CURRENT_TIMESTAMP()"),
            bigquery.SchemaField("requested_at", "TIMESTAMP", mode="NULLABLE"),
            bigquery.SchemaField("reason", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("email", "STRING", mode="NULLABLE"),
            bigquery.SchemaField("is_email_sent", "BOOLEAN", mode="NULLABLE", default_value_expression="FALSE"),
        ]
        bigquery_client.create_table(bq_table)


def process(bigquery_client: bigquery.Client, bigquery_region: str, app: App):
    dataset_configs = [
        DatasetConfig('gametuner_common', True, True),
        DatasetConfig('gametuner_monitoring', True, False),
        DatasetConfig(f'{app.id.value}_load', True, True),
        DatasetConfig(f'{app.id.value}_raw', True, True),
        DatasetConfig(f'{app.id.value}_v_load', True, True),
        DatasetConfig(f'{app.id.value}_v_raw', True, True),
        DatasetConfig(f'{app.id.value}_external', True, True),
        DatasetConfig(f'{app.id.value}_backfill', False, False),
        DatasetConfig(f'{app.id.value}_gdpr', True, True),
        DatasetConfig(f'{app.id.value}_main', True, True),
    ]

    fix_dataset = f'{app.id.value}_fix'
    gdpr_dataset = f'{app.id.value}_gdpr'
    bigquery_ddl.create_dataset_if_not_exists(bigquery_client, bigquery_region, fix_dataset)
    _create_fix_tables(bigquery_client, bigquery.Dataset(f'{bigquery_client.project}.{fix_dataset}'))

    for dataset_config in dataset_configs:
        bigquery_ddl.create_dataset_if_not_exists(bigquery_client, bigquery_region, dataset_config.name)
        if dataset_config.mirror_dataset:
            bigquery_ddl.create_dataset_if_not_exists(bigquery_client, bigquery_region, dataset_config.name, app.organization.gcp_project_id)
            if dataset_config.mirror_tables:
                bigquery_iam.create_authorized_views(bigquery_client, dataset_config.name, app)

    bigquery_iam.create_common_authorized_views(bigquery_client, app)
    _create_gdpr_delete_request_log(bigquery_client, bigquery.Dataset(f'{bigquery_client.project}.{gdpr_dataset}'))

