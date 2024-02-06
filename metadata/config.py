from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_DRIVER: str = "postgresql+psycopg2"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "db"
    DB_PORT: str = 5432
    DATABASE_NAME: str = "metadata"

    SCHEMA_BUCKET_NAME: str = "gametuner-korhner-test-metadata"

    BIGQUERY_REGION: str = "EU"

    CLOUD_SQL: str = "0"
    CLOUD_SQL_DRIVER: str = "pg8000"
    CLOUD_SQL_INSTANCE: str = ""

    JSON_LOGS: str = "0"
    RUN_MAINTAINER: str = "0"

    SQLALCHEMY_DATABASE_URL: str = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DATABASE_NAME}"

settings = Settings()
