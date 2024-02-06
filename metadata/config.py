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

from pydantic import BaseSettings


class Settings(BaseSettings):
    DB_DRIVER: str = "postgresql+psycopg2"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "postgres"
    DB_HOST: str = "db"
    DB_PORT: str = 5432
    DATABASE_NAME: str = "metadata"

    SCHEMA_BUCKET_NAME: str = "<bucket-name-of-event-schemas>"

    BIGQUERY_REGION: str = "EU"

    CLOUD_SQL: str = "0"
    CLOUD_SQL_DRIVER: str = "pg8000"
    CLOUD_SQL_INSTANCE: str = ""

    JSON_LOGS: str = "0"
    RUN_MAINTAINER: str = "0"

    SQLALCHEMY_DATABASE_URL: str = f"{DB_DRIVER}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DATABASE_NAME}"

settings = Settings()
