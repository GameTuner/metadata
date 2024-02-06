"""Insert atomic parameters

Revision ID: 7dab3181a14a
Revises: ba5f5e9cd8e2
Create Date: 2024-01-11 08:01:00.000000

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = '7dab3181a14a'
down_revision = 'ba5f5e9cd8e2'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('''
INSERT INTO atomic_parameter (name, type, is_gdpr, created_at)
VALUES
  ('app_id', 'string', FALSE, now()),
  ('platform', 'string', FALSE, now()),
  ('enricher_tstamp', 'datetime', FALSE, now()),
  ('collector_tstamp', 'datetime', FALSE, now()),
  ('dvce_created_tstamp', 'datetime', FALSE, now()),
  ('event', 'string', FALSE, now()),
  ('event_id', 'string', FALSE, now()),
  ('name_tracker', 'string', FALSE, now()),
  ('v_tracker', 'string', FALSE, now()),
  ('v_collector', 'string', FALSE, now()),
  ('v_etl', 'string', FALSE, now()),
  ('user_id', 'string', FALSE, now()),
  ('installation_id', 'string', FALSE, now()),
  ('unique_id', 'string', FALSE, now()),
  ('user_ipaddress', 'string', TRUE, now()),
  ('network_userid', 'string', FALSE, now()),
  ('geo_country', 'string', FALSE, now()),
  ('geo_country_name', 'string', FALSE, now()),
  ('geo_region', 'string', FALSE, now()),
  ('geo_city', 'string', FALSE, now()),
  ('geo_zipcode', 'string', FALSE, now()),
  ('geo_latitude', 'number', FALSE, now()),
  ('geo_longitude', 'number', FALSE, now()),
  ('geo_region_name', 'string', FALSE, now()),
  ('mkt_medium', 'string', FALSE, now()),
  ('mkt_source', 'string', FALSE, now()),
  ('mkt_term', 'string', FALSE, now()),
  ('mkt_content', 'string', FALSE, now()),
  ('mkt_campaign', 'string', FALSE, now()),
  ('useragent', 'string', FALSE, now()),
  ('geo_timezone', 'string', FALSE, now()),
  ('etl_tags', 'string', FALSE, now()),
  ('dvce_sent_tstamp', 'datetime', FALSE, now()),
  ('derived_tstamp', 'datetime', FALSE, now()),
  ('event_vendor', 'string', FALSE, now()),
  ('event_name', 'string', FALSE, now()),
  ('event_format', 'string', FALSE, now()),
  ('event_version', 'string', FALSE, now()),
  ('event_fingerprint', 'string', FALSE, now()),
  ('true_tstamp', 'datetime', FALSE, now()),
  ('load_tstamp', 'datetime', FALSE, now()),
  ('event_tstamp', 'datetime', FALSE, now()),
  ('event_quality', 'integer', FALSE, now()),
  ('sandbox_mode', 'boolean', FALSE, now()),
  ('backfill_mode', 'boolean', FALSE, now()),
  ('date_', 'date', FALSE, now())
    ''')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute('DELETE FROM atomic_parameter')
    # ### end Alembic commands ###