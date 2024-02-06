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

from sqlalchemy import Column, Date, DateTime, ForeignKey, Index, Integer, MetaData, String, Table, Boolean, UniqueConstraint, ForeignKeyConstraint
from sqlalchemy.orm import registry, relationship, composite
from sqlalchemy.dialects.postgresql import ARRAY, JSON

from metadata.core.domain.app import App, AppId, AppsflyerCostETLIntegration, AppsflyerIntegration, GcpProjectPrincipal, Datasource, EventBackfillJob, Organization, Timezone, StoreGooglePlay, StoreITunes
from metadata.core.domain.event import AtomicParameter, CommonEvent, Event, EventContext
from metadata.core.domain.schema import ParameterType, RawSchema, Schema, SchemaParameter
from metadata.core.domain.status import Status
from metadata.core.domain.user_history import MaterializedColumn

metadata = MetaData()
mapper_registry = registry()


organization_table = Table(
    "organization",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("name", String, nullable=False),
    Column("gcp_project_id", String, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("status", String, nullable=False),
    Column("status_updated_at", DateTime(timezone=True), nullable=False),
)

app_table = Table(
    "app",
    metadata,
    Column("id", String, primary_key=True, nullable=False),
    Column("timezone", String, nullable=False),
    Column("api_key", String, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("status", String, nullable=False),
    Column("status_updated_at", DateTime(timezone=True), nullable=False),
    Column("organization_id", Integer, ForeignKey("organization.id"), nullable=False),
)

gcp_project_principal_table = Table(
    "gcp_project_principal",
    metadata,
    Column("organization_id", Integer, ForeignKey("organization.id"), primary_key=True),
    Column("principal", String, primary_key=True, comment='Supported formats: user:email@domain.com, domain:domain.com, group:group@domain.com'),
)

appsflyer_integration_table = Table(
    "appsflyer_integration",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("app_id", String, ForeignKey("app.id"), nullable=False),
    Column("reports", ARRAY(String), nullable=False),
    Column("home_folder", String, nullable=False),
    Column("app_ids", ARRAY(String), nullable=False),
    Column("external_bucket_name", String, nullable=False),
)
Index('idx_appsflyer_integration_app_id', appsflyer_integration_table.c.app_id, unique=True)

appsflyer_cost_etl_integration_table = Table(
    "appsflyer_cost_etl_integration",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("app_id", String, ForeignKey("app.id"), nullable=False),
    Column("bucket_name", String, nullable=False),
    Column("reports", ARRAY(String), nullable=False),
    Column("android_app_id", String, nullable=True),
    Column("ios_app_id", String, nullable=True)
)
Index('idx_appsflyer_cost_etl_integration_app_id', appsflyer_cost_etl_integration_table.c.app_id, unique=True)

event_backfill_job_table = Table(
    "event_backfill_job_table",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("app_id", String, ForeignKey("app.id"), nullable=False),
    Column("job_name", String, nullable=False),
    Column("start_date", Date, nullable=False),
    Column("end_date", Date, nullable=False),
    Column("events", Boolean, nullable=False),
    Column("facts", Boolean, nullable=False),
    Column("user_history", Boolean, nullable=False),
)
Index('idx_event_backfill_job_app_id_job_name', event_backfill_job_table.c.app_id, event_backfill_job_table.c.job_name, unique=True)

datasource_table = Table(
    "datasource",
    metadata,
    Column("id", String, primary_key=True),
    Column("app_id", String, ForeignKey("app.id"), primary_key=True),
    Column("has_data_from", Date, nullable=False),
    Column("has_data_up_to", Date, nullable=True),
)

raw_schema_table = Table(
    "raw_schema",
    metadata,
    Column("path", String, primary_key=True, nullable=False),
    Column("schema", JSON, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("status", String, nullable=False),
    Column("status_updated_at", DateTime(timezone=True), nullable=False),
)

schema_table = Table(
    "schema",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("vendor", String, nullable=False),
    Column("name", String, nullable=False),
    Column("alias", String, nullable=True),
    Column("description", String, nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),

    UniqueConstraint('vendor', 'name', name='uq_schema_vendor_name')
)

schema_parameter_table = Table(
    "schema_parameter",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("schema_id", Integer, ForeignKey("schema.id"), nullable=False),
    Column("name", String, nullable=False),
    Column("alias", String, nullable=True),
    Column("description", String, nullable=True),
    Column("type", String, nullable=False),
    Column("introduced_at_version", Integer, nullable=False),
    Column("is_gdpr", Boolean, nullable=False),
    Column("is_gdpr_updated_at", DateTime(timezone=True), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),

    UniqueConstraint('schema_id', 'name', name='uq_schema_parameter_schema_name')
)
Index('idx_schema_parameter_schema_id', schema_parameter_table.c.schema_id)

atomic_parameter_table = Table(
    "atomic_parameter",
    metadata,
    Column("name", String, primary_key=True, nullable=False),
    Column("description", String, nullable=True),
    Column("type", String, nullable=False),
    Column("is_gdpr", Boolean, nullable=False),
    Column("is_gdpr_updated_at", DateTime(timezone=True), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
)

event_context_table = Table(
    "event_context",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("schema_id", Integer, ForeignKey("schema.id"), unique=True, nullable=False),
    Column("embedded_in_event", Boolean, nullable=False),
    Column("status", String, nullable=False),
    Column("status_updated_at", DateTime(timezone=True), nullable=False),
)

common_event_table = Table(
    "common_event",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("schema_id", Integer, ForeignKey("schema.id"), unique=True, nullable=False),
)

event_table = Table(
    "event",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("app_id", String, ForeignKey("app.id"), nullable=False),
    Column("schema_id", Integer, ForeignKey("schema.id"), unique=True, nullable=False),
    Column("parent_common_event_id", Integer, ForeignKey("common_event.id"), nullable=True),
    Column("parent_common_event_version", Integer, nullable=True),
    Column("status", String, nullable=False),
    Column("status_updated_at", DateTime(timezone=True), nullable=False),

    UniqueConstraint('app_id', 'parent_common_event_id', name='uq_event_app_id_parent_common_event_id')
)
Index('idx_event_app_id_schema_id', event_table.c.app_id, event_table.c.schema_id, unique=True)

store_itunes_table = Table(
    "store_itunes",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("app_id", String, ForeignKey("app.id"), nullable=False),
    Column("apple_id", String, nullable=False),
    Column("issuer_id", String, nullable=False),
    Column("key_id", String, nullable=False),
    Column("key_value", String, nullable=False),
    Column("vendor_number", String, nullable=False),
    Column("app_sku_id", String, nullable=False),
)
Index('idx_store_itunes_apple_id', store_itunes_table.c.apple_id, unique=True)

store_google_play_table = Table(
    "store_google_play",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("app_id", String, ForeignKey("app.id"), nullable=False),
    Column("app_bundle_id", String, nullable=False),
    Column("service_account", String, nullable=False),
    Column("report_bucket_name", String, nullable=False),
)

user_history_materialized_column = Table(
    "user_history_materialized_column",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("column_name", String, nullable=False),
    Column("app_id", String, nullable=False),
    Column("datasource_id", nullable=False),
    Column("event_id", Integer, ForeignKey("event.id"), nullable=False),
    Column("select_expression", String, nullable=False),
    Column("data_type", String, nullable=False),
    Column("user_history_formula", String, nullable=True),
    Column("totals", Boolean, nullable=True, default=True),
    Column("can_filter", Boolean, nullable=True, default=True),
    Column("can_group_by", Boolean, nullable=True, default=False),
    Column("materialized_from", DateTime(timezone=True), nullable=False),
    Column("hidden", Boolean, nullable=True, default=False),
    Column("dataset", String, nullable=False),

    UniqueConstraint("column_name", "app_id", "datasource_id", name="uq_column_name_app_id_datasource_id"),
)
ForeignKeyConstraint(['datasource_id', 'app_id'], ['datasource.id', 'datasource.app_id'], table=user_history_materialized_column)


def init_orm_mappers():
    mapper_registry.map_imperatively(
        Organization,
        organization_table,

        properties={
            "_status": organization_table.c.status,
            "status": composite(Status, organization_table.c.status),
            "gcp_project_principals": relationship(GcpProjectPrincipal, lazy='joined'),
        },
    )

    mapper_registry.map_imperatively(
        App,
        app_table,

        properties={
            "_id": app_table.c.id,
            "id": composite(AppId, app_table.c.id),
            "_timezone": app_table.c.timezone,
            "timezone": composite(Timezone, app_table.c.timezone),
            "_status": app_table.c.status,
            "status": composite(Status, app_table.c.status),
            "organization": relationship(Organization, uselist=False, lazy='joined'),
            "appsflyer_integration": relationship(AppsflyerIntegration, uselist=False, lazy='joined'),
            "appsflyer_cost_etl_integration": relationship(AppsflyerCostETLIntegration, uselist=False, lazy='joined'),
            "event_backfill_jobs": relationship(EventBackfillJob, lazy='joined'),
            "datasources": relationship(Datasource, lazy='joined'),
            "store_itunes": relationship(StoreITunes, uselist=False, lazy='joined'),
            "store_google_play": relationship(StoreGooglePlay, uselist=False, lazy='joined'),
        },
    )

    mapper_registry.map_imperatively(
        AppsflyerIntegration,
        appsflyer_integration_table,
        properties={
            "_app_id": appsflyer_integration_table.c.app_id,
            "app_id": composite(AppId, appsflyer_integration_table.c.app_id),
        },
    )

    mapper_registry.map_imperatively(
        GcpProjectPrincipal,
        gcp_project_principal_table,
        properties={
            "organization": relationship(Organization, uselist=False, lazy='joined'),
        },
    )

    mapper_registry.map_imperatively(
        AppsflyerCostETLIntegration,
        appsflyer_cost_etl_integration_table,
        properties={
            "_app_id": appsflyer_cost_etl_integration_table.c.app_id,
            "app_id": composite(AppId, appsflyer_cost_etl_integration_table.c.app_id),
        },
    )

    mapper_registry.map_imperatively(
        EventBackfillJob,
        event_backfill_job_table,
        properties={
            "_app_id": event_backfill_job_table.c.app_id,
            "app_id": composite(AppId, event_backfill_job_table.c.app_id),
        },
    )

    mapper_registry.map_imperatively(
        Datasource,
        datasource_table,
        properties={
            "_app_id": datasource_table.c.app_id,
            "app_id": composite(AppId, datasource_table.c.app_id),
            "materialized_columns": relationship(MaterializedColumn, lazy='joined'),
        },
    )

    mapper_registry.map_imperatively(
        RawSchema,
        raw_schema_table,
        properties={
            "_status": raw_schema_table.c.status,
            "status": composite(Status, raw_schema_table.c.status),
        },
    )

    mapper_registry.map_imperatively(
        Schema,
        schema_table,
        properties={
            "parameters": relationship(SchemaParameter, order_by=schema_parameter_table.c.id, lazy='joined'),
        },
    )

    mapper_registry.map_imperatively(
        SchemaParameter,
        schema_parameter_table,
        properties = {
            "_type": schema_parameter_table.c.type,
            "type": composite(ParameterType, schema_parameter_table.c.type)
        },
    )

    mapper_registry.map_imperatively(
        AtomicParameter,
        atomic_parameter_table,
        properties = {
            "_type": atomic_parameter_table.c.type,
            "type": composite(ParameterType, atomic_parameter_table.c.type)
        },
    )

    mapper_registry.map_imperatively(
        EventContext,
        event_context_table,
        properties={
            "schema": relationship(Schema, lazy='joined'),
            "_status": event_context_table.c.status,
            "status": composite(Status, event_context_table.c.status),
        },
    )

    mapper_registry.map_imperatively(
        CommonEvent,
        common_event_table,
        properties={
            "schema": relationship(Schema, lazy='joined'),
        },
    )

    mapper_registry.map_imperatively(
        Event,
        event_table,
        properties={
            "_app_id": event_table.c.app_id,
            "app_id": composite(AppId, event_table.c.app_id),
            "schema": relationship(Schema, uselist=False, lazy='joined'),
            "parent_common_event_version": event_table.c.parent_common_event_version,
            "parent_common_event": relationship(CommonEvent, uselist=False, lazy='joined'),
            "_status": event_table.c.status,
            "status": composite(Status, event_table.c.status),
        },
    )

    mapper_registry.map_imperatively(
        StoreITunes,
        store_itunes_table,
        properties={
            "_app_id": store_itunes_table.c.app_id,
            "app_id": composite(AppId, store_itunes_table.c.app_id),
        },
    ),

    mapper_registry.map_imperatively(
        StoreGooglePlay,
        store_google_play_table,
        properties={
            "_app_id": store_google_play_table.c.app_id,
            "app_id": composite(AppId, store_google_play_table.c.app_id),
        },
    )

    mapper_registry.map_imperatively(
        MaterializedColumn,
        user_history_materialized_column,
        properties={
            "_app_id": user_history_materialized_column.c.app_id,
            "app_id": composite(AppId, user_history_materialized_column.c.app_id),
            "event": relationship(Event, uselist=False, lazy='joined'),
        },
    )

