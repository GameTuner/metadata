# gametuner-metadata
Various metadata about gametuner apps

### Run locally
Easiest way is to use vscode and dev containers extension.
TODO: Try building from local folder.
Tested with `Dev Containers: Clone repository in Container Volume...` command (ctrl + shift + P)
Run migrations before running the service.

### Create ssh tunnel to production
Run to print current metadata VM

```gcloud compute instances list | grep metadata```

Run to create tunnel

```gcloud compute ssh --zone "europe-west1-c" "gametuner-metadata-xxxx" --tunnel-through-iap --project "gametuner-infra-production" -- -NL 8002:localhost:8080```

Metadata service is available on http://localhost:8002

### Common commands
- Apply all migrations: `alembic upgrade head`
- Revert migrations: `alembic downgrade base`
- Add new migration: `alembic revision --autogenerate -m 'Description'`
- Connect to database: `psql -U postgres -d metadata -h db`


### Common operations
- Add a new client (organization):
    - Add gcp project in terraform metadata client_projects parameter
    - Insert organization into organization table in metadata database
    - Add/remove client gcp project permissions: Modify gcp_project_principal table and update organization to 'NEEDS_UPDATE'
- Add a new game:
    - Check "/api/v1/apps/{app_id}" POST route. Insert organization into organization table if its a new client.
- Add new event/event version: Use REST api
- Add new common event: Create a migration that inserts event into common_event, schema and schema_parameters (check some existing common event for examples). After deploy, set status for all apps to NEEDS_UPDATE and monitor if events are created.