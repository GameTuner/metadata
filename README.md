# GameTuner MetaData

## Overview

GameTuner MetaData is service that manage various configurations about GameTuner apps (games). With it you can access and manage organisations, apps, events and event schemas. It is written in Python and uses FastAPI framework.

All configurations are stored in PostgreSQL database. Service uses [Alembic][alembic] for database migrations.

## Installation

### Run locally

#### Pre-requisites

In order to run this service you need to have the following installed:

- VSCode
- [Dev Containers extension][dev-containers]
- Python 3.10+
- Docker

#### Run Dev Container

Easiest way to run service locally is to use Visual Studio Code and Dev containers extension. To mount dev container, open the project in VSCode and run `Dev Containers: Clone repository in Container Volume...` command (ctrl + shift + P). This will create a new container with all the necessary dependencies installed.

#### Setup database

Before first run you need to setup the database. Using next command you can apply all necessary migrations:

```bash
alembic upgrade head
```

Also, you can use other common [alembic][alembic] commands to manage database migrations:

- Revert migrations: `alembic downgrade base`
- Add new migration: `alembic revision --autogenerate -m 'Description'`
- Connect to database: `psql -U postgres -d metadata -h db`

#### Run service

To run the service, use the following command:

```bash
export GOOGLE_CLOUD_PROJECT=<gcp-project-id>
uvicorn metadata.main:app --host 0.0.0.0 --port 8002
```

Also, launch configuration is provided in `.vscode/launch.json` file. You can use it to run the service from VSCode.

Metadata service is available on http://localhost:8002

### Running on GCP

For deploying the application on GCP, you should first build the application by running google cloud build `gcloud builds submit --config=cloudbuild.yaml .`. Script submits docker image to GCP artifact registry. Once the image is submitted, you should deploy the application on GCP. You can do that by running terraform script in [GameTuner terraform][gametuner-terraform] project.

#### Create ssh tunnel to production VM

In order to access production service, you need to create ssh tunnel to production VM. First, you need to find the name of the VM:

```bash
gcloud compute instances list | grep metadata
```

Once you have the name and zone of the VM, you can create ssh tunnel using the following command:

```bash
gcloud compute ssh --zone "zone-id" "gametuner-metadata-xxxx" --tunnel-through-iap --project "<gcp-project-id>" -- -NL 8002:localhost:8080
```

Metadata service is available on http://localhost:8002

## Usage

### Add new organisation

Every organisation have separate GCP project and it is managed by the service. To add new organisation, you need to add new GCP project in [GameTuner terraform][gametuner-terraform] metadata client_projects parameter. After that, you need to insert organisation into `organisation` table in metadata database. Currently, API endpoint is not provided so you need to add record direclty into the database. For status field, use `'NOT_READY'` value.

 Also, you need to add client GCP project permissions by modifying `gcp_project_principal` table and update organisation status to `'NEEDS_UPDATE'`.

### API

Service provides REST API for managing organisations, apps, events and event schemas. You can find the full API documentation on http://localhost:8002/docs

### Database

Service uses PostgreSQL database for storing all configurations. You can connect to the database using the following command:

```bash
psql -U postgres -d metadata -h localhost
```

For connecting to production database, there is provided bastion VM and ssh tunnel. In GCP console, you can find the name of the bastion VM (cloudsql-bastion-gametuner-metadata) and use it to create ssh tunnel to the production database. Once you have the tunnel, you can connect to the database using the following command:

```bash
connect_to_db.sh
```

## Licence

The GameTuner MetaData is copyright 2022-2024 AlgebraAI.

GameTuner MetaData is released under the [Apache 2.0 License][license].



[alembic]:https://alembic.sqlalchemy.org/en/latest/
[dev-containers]:https://code.visualstudio.com/docs/devcontainers/containers
[gametuner-terraform]:https://github.com/GameTuner/gametuner-terraform-gcp.git
[license]: https://www.apache.org/licenses/LICENSE-2.0