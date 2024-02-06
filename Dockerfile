FROM python:3.10-slim

RUN apt-get update && apt-get install -y libpq-dev gcc

COPY ./requirements.txt /app/requirements.txt
COPY ./alembic.ini /app/alembic.ini

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt
COPY ./metadata /app/metadata

ENV UVICORN_PORT=8080
ENV JSON_LOGS=1
ENV RUN_MAINTAINER=1
ENV CLOUD_SQL=1
ENV DB_DRIVER=postgresql+pg8000
ENV DATABASE_NAME=postgres
ENV DB_USER=postgres
ENV DB_PASSWORD=metadata

ENV SCHEMA_BUCKET_NAME=''
ENV BIGQUERY_REGION=''
ENV CLOUD_SQL_INSTANCE=''

WORKDIR /app
CMD alembic upgrade head && uvicorn metadata.main:app --host 0.0.0.0