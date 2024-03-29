"""Insert contexts

Revision ID: 87a03c3a240d
Revises: d34233af6279
Create Date: 2024-01-11 08:03:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '87a03c3a240d'
down_revision = 'd34233af6279'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###

    op.execute('''
WITH schema_insert AS (
  INSERT INTO schema (vendor, name, description, created_at) VALUES
  ('com.algebraai.gametuner.context', 'ctx_event_context', 'Event context that is added to every triggered event', now())
  returning id
)

,schema_parameter AS (
  INSERT INTO schema_parameter (schema_id, name, description, type, introduced_at_version, is_gdpr, is_gdpr_updated_at, created_at)

  SELECT
    schema_insert.id,
    'event_index',
    '',
    'integer',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

UNION ALL
  SELECT
    schema_insert.id,
    'previous_event',
    '',
    'string',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

UNION ALL
  SELECT
    schema_insert.id,
    'sandbox_mode',
    '',
    'boolean',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

UNION ALL
  SELECT
    schema_insert.id,
    'event_bundle_id',
    '',
    'integer',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

UNION ALL
  SELECT
    schema_insert.id,
    'is_online',
    '',
    'boolean',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

)

INSERT INTO event_context (schema_id, embedded_in_event, status, status_updated_at)
SELECT
 schema_insert.id,
 FALSE,
 'NOT_READY', now()
FROM schema_insert
''')


    op.execute('''
WITH schema_insert AS (
  INSERT INTO schema (vendor, name, description, created_at) VALUES
  ('com.algebraai.gametuner.embedded_context', 'ctx_device_context', 'Device context', now())
  returning id
)

,schema_parameter AS (
  INSERT INTO schema_parameter (schema_id, name, description, type, introduced_at_version, is_gdpr, is_gdpr_updated_at, created_at)

  SELECT
    schema_insert.id,
    'device_category',
    '',
    'string',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

UNION ALL
  SELECT
    schema_insert.id,
    'device_manufacturer',
    '',
    'string',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

UNION ALL
  SELECT
    schema_insert.id,
    'model',
    '',
    'string',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

UNION ALL
  SELECT
    schema_insert.id,
    'os_version',
    '',
    'string',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

UNION ALL
  SELECT
    schema_insert.id,
    'cpu_type',
    '',
    'string',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

UNION ALL
  SELECT
    schema_insert.id,
    'gpu',
    '',
    'string',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

UNION ALL
  SELECT
    schema_insert.id,
    'ram_size',
    '',
    'integer',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

UNION ALL
  SELECT
    schema_insert.id,
    'screen_resolution',
    '',
    'string',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

UNION ALL
  SELECT
    schema_insert.id,
    'device_language',
    '',
    'string',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

UNION ALL
  SELECT
    schema_insert.id,
    'device_timezone',
    '',
    'string',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

UNION ALL
  SELECT
    schema_insert.id,
    'source',
    '',
    'string',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

UNION ALL
  SELECT
    schema_insert.id,
    'medium',
    '',
    'string',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

UNION ALL
  SELECT
    schema_insert.id,
    'campaign',
    '',
    'string',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

UNION ALL
  SELECT
    schema_insert.id,
    'build_version',
    '',
    'string',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

UNION ALL
  SELECT
    schema_insert.id,
    'device_id',
    '',
    'string',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

UNION ALL
  SELECT
    schema_insert.id,
    'advertising_id',
    '',
    'string',
    0,
    TRUE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

UNION ALL
  SELECT
    schema_insert.id,
    'is_hacked',
    '',
    'string',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

UNION ALL
  SELECT
    schema_insert.id,
    'idfa',
    '',
    'string',
    0,
    TRUE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

UNION ALL
  SELECT
    schema_insert.id,
    'idfv',
    '',
    'string',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

UNION ALL
  SELECT
    schema_insert.id,
    'store',
    '',
    'string',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

)

INSERT INTO event_context (schema_id, embedded_in_event, status, status_updated_at)
SELECT
 schema_insert.id,
 TRUE,
 'NOT_READY', now()
FROM schema_insert
''')


    op.execute('''
WITH schema_insert AS (
  INSERT INTO schema (vendor, name, description, created_at) VALUES
  ('com.algebraai.gametuner.embedded_context', 'ctx_session_context', 'Event context that is added to every triggered event', now())
  returning id
)

,schema_parameter AS (
  INSERT INTO schema_parameter (schema_id, name, description, type, introduced_at_version, is_gdpr, is_gdpr_updated_at, created_at)

  SELECT
    schema_insert.id,
    'session_id',
    '',
    'string',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

UNION ALL
  SELECT
    schema_insert.id,
    'session_index',
    '',
    'integer',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

UNION ALL
  SELECT
    schema_insert.id,
    'session_time',
    '',
    'number',
    0,
    FALSE,
    NULL::timestamp with time zone,
    now()
  FROM schema_insert

)

INSERT INTO event_context (schema_id, embedded_in_event, status, status_updated_at)
SELECT
 schema_insert.id,
 TRUE,
 'NOT_READY', now()
FROM schema_insert
''')

    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('DELETE FROM event_context')
    op.execute("DELETE FROM schema_parameter WHERE schema_id IN (SELECT id FROM schema WHERE name LIKE 'ctx_%')")
    op.execute("DELETE FROM schema WHERE name LIKE 'ctx_%'")
    # ### end Alembic commands ###
