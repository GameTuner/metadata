from google.cloud import bigquery
from google.cloud.bigquery import Dataset, Table
from google.api_core import exceptions


def get_table_if_exists(bigquery_client: bigquery.Client, dataset: Dataset, table_name: str) -> Table:
    table = dataset.table(table_name)
    try:
        return bigquery_client.get_table(table)
    except exceptions.NotFound:
        return None


def create_dataset_if_not_exists(bigquery_client: bigquery.Client, bigquery_region: str, dataset_name: str, project: str = None) -> Dataset:
    if not project:
        project = bigquery_client.project
    dataset = bigquery.Dataset(f'{project}.{dataset_name}')
    dataset.location = bigquery_region
    return bigquery_client.create_dataset(dataset, exists_ok=True)
