"""Create tables

Revision ID: ba5f5e9cd8e2
Revises:
Create Date: 2024-01-11 08:00:00.630631

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'ba5f5e9cd8e2'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('organization',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('gcp_project_id', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('status_updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('gcp_project_principal',
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.Column('principal', sa.String(), nullable=False, comment='Supported formats: user:email@domain.com, domain:domain.com, group:group@domain.com'),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    sa.PrimaryKeyConstraint('organization_id', 'principal')
    )

    op.create_table('app',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('timezone', sa.String(), nullable=False),
    sa.Column('api_key', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('status_updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('organization_id', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.ForeignKeyConstraint(['organization_id'], ['organization.id'], ),
    )
    op.create_table('atomic_parameter',
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('is_gdpr', sa.Boolean(), nullable=False),
    sa.Column('is_gdpr_updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('name'),
    )
    op.create_table('schema',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('vendor', sa.String(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('alias', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('vendor', 'name', name='uq_schema_vendor_name')
    )
    op.create_table('common_event',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('schema_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['schema_id'], ['schema.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('schema_id')
    )
    op.create_table('event_context',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('schema_id', sa.Integer(), nullable=False),
    sa.Column('embedded_in_event', sa.Boolean(), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('status_updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['schema_id'], ['schema.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('schema_id')
    )
    op.create_table('schema_parameter',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('schema_id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('type', sa.String(), nullable=False),
    sa.Column('introduced_at_version', sa.Integer(), nullable=False),
    sa.Column('is_gdpr', sa.Boolean(), nullable=False),
    sa.Column('is_gdpr_updated_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('alias', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['schema_id'], ['schema.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('schema_id', 'name', name='uq_schema_parameter_schema_name')
    )
    op.create_index('idx_schema_parameter_schema_id', 'schema_parameter', ['schema_id'], unique=False)
    op.create_table('event',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('app_id', sa.String(), nullable=False),
    sa.Column('schema_id', sa.Integer(), nullable=False),
    sa.Column('parent_common_event_id', sa.Integer(), nullable=True),
    sa.Column('parent_common_event_version', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('status_updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.ForeignKeyConstraint(['app_id'], ['app.id'], ),
    sa.ForeignKeyConstraint(['parent_common_event_id'], ['common_event.id'], ),
    sa.ForeignKeyConstraint(['schema_id'], ['schema.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('schema_id'),
    sa.UniqueConstraint('app_id', 'parent_common_event_id', name='uq_event_app_id_parent_common_event_id')
    )
    op.create_index('idx_event_app_id_schema_id', 'event', ['app_id', 'schema_id'], unique=True)

    op.create_table('appsflyer_cost_etl_integration',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('app_id', sa.String(), nullable=False),
    sa.Column('bucket_name', sa.String(), nullable=False),
    sa.Column('reports', postgresql.ARRAY(sa.String()), nullable=False),
    sa.Column('app_ids', postgresql.ARRAY(sa.String()), nullable=False),
    sa.Column('android_app_id', sa.String(), nullable=True),
    sa.Column('ios_app_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['app_id'], ['app.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_appsflyer_cost_etl_integration_app_id', 'appsflyer_cost_etl_integration', ['app_id'], unique=True)
    op.create_table('appsflyer_integration',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('app_id', sa.String(), nullable=False),
    sa.Column('reports', postgresql.ARRAY(sa.String()), nullable=False),
    sa.Column('home_folder', sa.String(), nullable=False),
    sa.Column('app_ids', postgresql.ARRAY(sa.String()), nullable=False),
    sa.Column('external_bucket_name', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['app_id'], ['app.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_appsflyer_integration_app_id', 'appsflyer_integration', ['app_id'], unique=True)
    op.create_table('event_backfill_job_table',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('app_id', sa.String(), nullable=False),
    sa.Column('job_name', sa.String(), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=False),
    sa.Column('events', sa.Boolean(), nullable=False),
    sa.Column('facts', sa.Boolean(), nullable=False),
    sa.Column('user_history', sa.Boolean(), nullable=False),
    sa.ForeignKeyConstraint(['app_id'], ['app.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_event_backfill_job_app_id_job_name', 'event_backfill_job_table', ['app_id', 'job_name'], unique=True)

    op.create_table('raw_schema',
    sa.Column('path', sa.String(), nullable=False),
    sa.Column('schema', postgresql.JSON(astext_type=sa.Text()), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
    sa.Column('status', sa.String(), nullable=False),
    sa.Column('status_updated_at', sa.DateTime(timezone=True), nullable=False),
    sa.PrimaryKeyConstraint('path'),
    )

    op.create_table('datasource',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('app_id', sa.String(), nullable=False),
    sa.Column('has_data_from', sa.Date(), nullable=False),
    sa.Column('has_data_up_to', sa.Date(), nullable=True),
    sa.ForeignKeyConstraint(['app_id'], ['app.id'], ),
    sa.PrimaryKeyConstraint('id', 'app_id')
    )

    op.create_table('store_itunes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('app_id', sa.String(), autoincrement=False, nullable=False),
    sa.Column('apple_id', sa.String(), autoincrement=False, nullable=False),
    sa.Column('issuer_id', sa.String(), autoincrement=False, nullable=False),
    sa.Column('key_id', sa.String(), autoincrement=False, nullable=False),
    sa.Column('key_value', sa.String(), autoincrement=False, nullable=False),
    sa.Column('vendor_number', sa.String(), autoincrement=False, nullable=False),
    sa.Column('app_sku_id', sa.String(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['app_id'], ['app.id'], name='store_itunes_app_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='store_itunes_pkey'),
    sa.UniqueConstraint('apple_id', name='idx_store_itunes_apple_id')
    )

    op.create_table('store_google_play',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('app_id', sa.String(), autoincrement=False, nullable=False),
    sa.Column('app_bundle_id', sa.String(), autoincrement=False, nullable=False),
    sa.Column('report_bucket_name', sa.String(), autoincrement=False, nullable=False),
    sa.Column('service_account', sa.String(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['app_id'], ['app.id'], name='store_google_play_app_id_fkey'),
    sa.PrimaryKeyConstraint('id', name='store_google_play_pkey'),
    sa.UniqueConstraint('app_bundle_id', name='idx_store_google_play_app_bundle_id')
    )

    op.create_table('user_history_materialized_column',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('column_name', sa.String(), nullable=False),
    sa.Column('app_id', sa.String(), nullable=False),
    sa.Column('datasource_id', sa.String(), nullable=False),
    sa.Column('event_id', sa.Integer(), nullable=False),
    sa.Column('dataset', sa.String(), nullable=False),
    sa.Column('select_expression', sa.String(), nullable=False),
    sa.Column('data_type', sa.String(), nullable=False),
    sa.Column('user_history_formula', sa.String(), nullable=True),
    sa.Column('totals', sa.Boolean(), nullable=True),
    sa.Column('can_filter', sa.Boolean(), nullable=True),
    sa.Column('can_group_by', sa.Boolean(), nullable=True),
    sa.Column('materialized_from', sa.DateTime(timezone=True), nullable=False),
    sa.Column('hidden', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['datasource_id', 'app_id'], ['datasource.id', 'datasource.app_id'], ),
    sa.ForeignKeyConstraint(['event_id'], ['event.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('column_name', 'app_id', 'datasource_id', name='uq_column_name_app_id_datasource_id')
    )

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_history_materialized_column')
    op.drop_table('store_google_play')
    op.drop_table('store_itunes')
    op.drop_table('datasource')
    op.drop_table('raw_schema')

    op.drop_index('idx_event_backfill_job_app_id_job_name', table_name='event_backfill_job_table')
    op.drop_table('event_backfill_job_table')
    op.drop_index('idx_appsflyer_integration_app_id', table_name='appsflyer_integration')
    op.drop_table('appsflyer_integration')
    op.drop_index('idx_appsflyer_cost_etl_integration_app_id', table_name='appsflyer_cost_etl_integration')
    op.drop_table('appsflyer_cost_etl_integration')

    op.drop_table('event')
    op.drop_index('idx_schema_parameter_schema_id', table_name='schema_parameter')
    op.drop_table('schema_parameter')
    op.drop_table('event_context')
    op.drop_table('common_event')
    op.drop_table('schema')
    op.drop_table('atomic_parameter')

    op.drop_table('app')

    op.drop_table('gcp_project_principal')
    op.drop_table('organization')
    # ### end Alembic commands ###
