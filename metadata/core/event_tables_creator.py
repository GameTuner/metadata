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

from typing import List
import google
from google.api_core import exceptions
from google.cloud import bigquery
from fastapi.logger import logger
from google.cloud.bigquery import SchemaField, Dataset, Table
from metadata.core.domain.app import AppId
from metadata.core.domain.event import AtomicParameter, EventContext
from metadata.core.domain.schema import ParameterType, Schema, SchemaParameter


def convert_type(parameter_type: str) -> str:
    return {
        'integer': 'integer',
        'number': 'float',
        'boolean': 'boolean',
        'string': 'string',
        'date': 'date',
        'datetime': 'timestamp',
        'map<string,integer>': 'record',
        'map<string,number>': 'record',
        'map<string,boolean>': 'record',
        'map<string,string>': 'record',
        'map<string,date>': 'record',
        'map<string,datetime>': 'record'
    }[parameter_type]


LOAD_DATASET_PARTITION_EXPIRATION_MS = 30 * 24 * 60 * 60 * 1000  # 30 days


class BigQueryEventTablesCreator:
    def __init__(self, bigquery_region: str) -> None:
        credentials, _ = google.auth.default()
        self._bigquery_region = bigquery_region
        self._bigquery_client = bigquery.Client(credentials=credentials)

    def _get_table_if_exists(self, dataset: Dataset, table_name: str) -> Table:
        table = dataset.table(table_name)
        try:
            return self._bigquery_client.get_table(table)
        except exceptions.NotFound:
            return None

    def _get_mode_by_type(self, type: str) -> str:
        return 'REPEATED' if type.startswith('map') else 'NULLABLE'

    def _get_schema_fields_by_type(self, type: str):
        if type.startswith('map<string,'):
            logger.info(f"Type is {type}")
            iglu_schema_params = [
                SchemaParameter(name='key', type=ParameterType.STRING, description='Key of map object', introduced_at_version=0),
                SchemaParameter(name='value', type=ParameterType(type[11:-1]), description='Value of map object', introduced_at_version=0)
            ]
            params_schema = [SchemaField(param_schema.name, convert_type(param_schema.type.value), 'NULLABLE', None, param_schema.description, ())
                            for param_schema in iglu_schema_params]
            return params_schema
        else:
            return ()

    def _build_params_schema_field(self, parameters: List[SchemaParameter]):
        if parameters:
            params_schema = [SchemaField(param_schema.name, convert_type(param_schema.type.value), self._get_mode_by_type(param_schema.type.value),
                                          None, param_schema.description, self._get_schema_fields_by_type(param_schema.type))
                            for param_schema in parameters]
            return SchemaField('params', 'RECORD', 'NULLABLE', None, None, params_schema)
        return None

    def _build_event_schema(self, schema_parameters: List[SchemaParameter], embedded_schemas: List[Schema],
                       atomic_parameters: List[AtomicParameter]) -> List[SchemaField]:

        atomic_fields = [SchemaField(a.name, convert_type(a.type)) for a in atomic_parameters]

        embedded_contexts = []
        for embedded_context_schema in embedded_schemas:
            params_schema = self._build_params_schema_field(embedded_context_schema.parameters).fields
            embedded_contexts.append(SchemaField(embedded_context_schema.name, 'RECORD', 'NULLABLE', None, None, params_schema))

        return atomic_fields + [x for x in [self._build_params_schema_field(schema_parameters)] if x] + embedded_contexts


    def _has_schema_diff(self, table: Table, new_schema: List[SchemaField]):
        diff = set([str(s) for s in new_schema]) - set([str(s) for s in table.schema])
        if table.schema and diff:
            logger.info(f'Updating table {table.full_table_id}, changed fields: {diff}')
            return True
        return False

    def _process_event_table(self, schema: Schema, schema_parameters: List[SchemaParameter], embedded_schemas: List[Schema], dataset: Dataset,
                             atomic_parameters: List[AtomicParameter], partition_expiration_ms = None):
        table_def = dataset.table(schema.name)
        table = self._get_table_if_exists(dataset, schema.name)
        new_schema = self._build_event_schema(schema_parameters, embedded_schemas, atomic_parameters)

        if table:
            if self._has_schema_diff(table, new_schema):
                table.schema = new_schema
                self._bigquery_client.update_table(table, ["schema"])
        else:
            logger.info(f'Table {table_def.dataset_id}.{table_def.table_id} does not exists, creating')
            table = bigquery.Table(table_def)
            table.schema = new_schema
            table.time_partitioning = bigquery.TimePartitioning(
                type_=bigquery.TimePartitioningType.DAY, field="date_", expiration_ms=partition_expiration_ms,
            )
            self._bigquery_client.create_table(table)


    def _process_event_view(self, table_dataset: str, view_dataset: str, schema: Schema, schema_parameters: List[SchemaParameter], embedded_schemas: List[Schema], atomic_parameters: List[AtomicParameter]):
        def clean_up_context_name(context_name: str) -> str:
            prefix = 'ctx_'
            suffix = '_context'
            if context_name.startswith(prefix):
                context_name = context_name[len(prefix):]
            if context_name.endswith(suffix):
                context_name = context_name[:-len(suffix)]
            return f'{context_name}_'
        def clean_up_atomic_name(atomic_name: str) -> str:
            if not atomic_name.endswith('_'):
                return f'{atomic_name}_'
            else:
                return atomic_name

        important_atomic_parameters = ['app_id', 'date_', 'event_tstamp', 'user_id', 'event_name']

        important_atomic_parameters_token = ','.join([f'`{a}` AS `{clean_up_atomic_name(a)}`' for a in important_atomic_parameters])  + ','
        params_token = (','.join([f'params.{s.name} AS `{s.name}`' for s in schema_parameters]) + ',') if schema_parameters else ''
        non_important_atomic_parameters_token = ','.join([f'`{a.name}` AS `{clean_up_atomic_name(a.name)}`' for a in atomic_parameters if a.name not in important_atomic_parameters]) + ','
        contexts_token = ','.join([f'`{e.name}` AS `{clean_up_context_name(e.name)}`' for e in embedded_schemas])  if embedded_schemas else ''
        sql = f'''
        CREATE OR REPLACE VIEW `{self._bigquery_client.project}.{view_dataset}.{schema.name}` AS
            SELECT
              {important_atomic_parameters_token}
              {params_token}
              {non_important_atomic_parameters_token}
              {contexts_token}
            FROM `{self._bigquery_client.project}.{table_dataset}.{schema.name}`
        '''
        logger.info(f'Creating view: {sql}')
        query_job = self._bigquery_client.query(sql)
        query_job.result()

    def maintain_event_table(self, app_id: AppId, schema: Schema, schema_parameters: List[SchemaParameter], atomic_parameters: List[AtomicParameter], embedded_event_contexts: List[EventContext]):
        embedded_schemas = [e.get_schema() for e in embedded_event_contexts]
        self._process_event_table(schema, schema_parameters, embedded_schemas,
                                   bigquery.Dataset(f'{self._bigquery_client.project}.{app_id.value}_load'),
                                   atomic_parameters, LOAD_DATASET_PARTITION_EXPIRATION_MS)
        self._process_event_table(schema, schema_parameters, embedded_schemas,
                                   bigquery.Dataset(f'{self._bigquery_client.project}.{app_id.value}_raw'),
                                   atomic_parameters)
        self._process_event_table(schema, schema_parameters, embedded_schemas,
                                   bigquery.Dataset(f'{self._bigquery_client.project}.{app_id.value}_backfill'),
                                   atomic_parameters)
        self._process_event_view(f'{app_id.value}_load', f'{app_id.value}_v_load', schema, schema_parameters, embedded_schemas, atomic_parameters)
        self._process_event_view(f'{app_id.value}_raw', f'{app_id.value}_v_raw', schema, schema_parameters, embedded_schemas, atomic_parameters)
