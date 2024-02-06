from google.cloud import bigquery
from google.cloud.bigquery import SchemaField
from fastapi.logger import logger
from metadata.api.app.internal import bigquery_ddl


def _create_monitoring_tables(bigquery_client: bigquery.Client, bigquery_region: str, monitoring_dataset_name: str):
    logger.info('Creating monitoring tables')
    enrich_bad_table_name = 'enrich_bad_events'
    monitoring_dataset = bigquery_ddl.create_dataset_if_not_exists(bigquery_client, bigquery_region, monitoring_dataset_name)
    monitoring_table = bigquery_ddl.get_table_if_exists(bigquery_client, monitoring_dataset, enrich_bad_table_name)
    if monitoring_table:
        logger.info(f'Monitoring table {enrich_bad_table_name} already exists, skipping')
    else:
        logger.info(f'Monitoring table {enrich_bad_table_name} does not exists, creating')
        monitoring_table = bigquery.Table(monitoring_dataset.table(enrich_bad_table_name))
        monitoring_table.schema = [
            SchemaField("load_tstamp", "TIMESTAMP", "REQUIRED"),
            SchemaField("schema", "STRING", "NULLABLE"),
            SchemaField("data", "STRING", "NULLABLE")
        ]
        monitoring_table.time_partitioning = bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY, field="load_tstamp", expiration_ms=None,
        )
        bigquery_client.create_table(monitoring_table)

    #create view
    enrich_bad_view_name = 'v_enrich_bad_events'
    enrich_bad_view_sql = f"""
        CREATE OR REPLACE VIEW `{monitoring_dataset.project}.{monitoring_dataset.dataset_id}.{enrich_bad_view_name}`
        (load_tstamp, schema, data, error_type, app_id, event_name, event_schema_version, collector_tstamp, error_messages, date_) AS (
            SELECT
                *,
                SPLIT(schema, '/')[OFFSET(1)] AS error_type,
                (SELECT JSON_VALUE(_parameters, '$.value') FROM UNNEST(JSON_EXTRACT_ARRAY(data, '$.payload.raw.parameters')) AS _parameters WHERE JSON_VALUE(_parameters, '$.name') = "aid") AS app_id,
                IF(STARTS_WITH(SPLIT(JSON_VALUE(data, '$.failure.messages[0].schemaKey'), '/')[OFFSET(0)],'iglu:com.algebraai.gametuner'),
                    CASE
                    WHEN SPLIT(JSON_VALUE(data, '$.failure.messages[0].schemaKey'), '/')[OFFSET(1)] LIKE '%payload_data%' THEN NULL
                    WHEN SPLIT(JSON_VALUE(data, '$.failure.messages[0].schemaKey'), '/')[OFFSET(1)] LIKE '%_context%' THEN NULL
                    ELSE SPLIT(JSON_VALUE(data, '$.failure.messages[0].schemaKey'), '/')[OFFSET(1)] END
                , NULL) AS event_name,
                SPLIT(JSON_VALUE(data, '$.failure.messages[0].schemaKey'), '/')[OFFSET(3)] event_schema_version,
                JSON_VALUE(data, '$.payload.raw.timestamp')  AS collector_tstamp,
                ARRAY(SELECT JSON_EXTRACT(dataReports, '$.message') FROM UNNEST(JSON_QUERY_ARRAY(data, '$.failure.messages[0].error.dataReports')) AS dataReports) AS error_messages,
                DATE(load_tstamp) AS date_
            FROM `{monitoring_dataset.project}.{monitoring_dataset.dataset_id}.{enrich_bad_table_name}`
            );
    """

    logger.info(f'Creating or replacing view: {enrich_bad_view_name}')
    query_job = bigquery_client.query(enrich_bad_view_sql)
    query_job.result()

def process(bigquery_client: bigquery.Client, bigquery_region: str):
    _create_monitoring_tables(bigquery_client, bigquery_region, 'gametuner_monitoring')
