from contextlib import contextmanager
from google.cloud.sql.connector import Connector, IPTypes

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy_utils import create_database, database_exists

from metadata.config import settings

if settings.CLOUD_SQL == "0":
    engine = create_engine(settings.SQLALCHEMY_DATABASE_URL, pool_pre_ping=True, echo=True)
    if not database_exists(settings.SQLALCHEMY_DATABASE_URL):
        create_database(settings.SQLALCHEMY_DATABASE_URL)
else:
    connector = Connector()
    engine = create_engine(f"{settings.DB_DRIVER}://", creator=lambda: connector.connect(
        settings.CLOUD_SQL_INSTANCE,
        settings.CLOUD_SQL_DRIVER,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        db=settings.DATABASE_NAME,
        ip_type=IPTypes.PRIVATE
    ))
SessionFactory = sessionmaker(autocommit=False, autoflush=False, expire_on_commit=False, bind=engine)

@contextmanager
def get_db_session():
    db = SessionFactory()
    try:
        yield db
    finally:
        db.close()