from dataclasses import asdict, dataclass
from datetime import date
from typing import Dict, List
from metadata.api.app.internal.domain import EventsByApp
from metadata.core.domain.app import App, Datasource
from metadata.core.domain.schema import Schema, SchemaParameter


@dataclass(frozen=True)
class AppDTO:
    app_id: str
    api_key: str
    timezone: str
    created_at: date
    close_event_partitions_after_hours: int

    @classmethod
    def from_domain_model(cls, app: App) -> 'AppDTO':
        return AppDTO(
            app_id=app.id.value,
            api_key=app.api_key,
            timezone=app.timezone.name,
            created_at=app.created_at,
            close_event_partitions_after_hours=app.close_event_partitions_after_hours
        )

@dataclass(frozen=True)
class SchemaParameterDTO:
    name: str
    alias: str
    type: str
    description: str | None

@dataclass(frozen=True)
class SchemaDTO:
    vendor: str
    url: str # remove, only for diff
    type: str # remove, only for diff
    name: str
    alias: str
    version: str
    description: str | None
    parameters: List[SchemaParameterDTO]

    @classmethod
    def from_domain_model(cls, schema: Schema, schema_alias: str, parameters: List[SchemaParameter]):
        return SchemaDTO(
            vendor=schema.vendor,
            type="object",
            url=f"iglu:{schema.vendor}/{schema.name}/jsonschema/1-0-{schema.current_version}",
            name=schema.name,
            alias=schema_alias,
            version=f'1-0-{schema.current_version}',
            description=schema.description,
            parameters=[SchemaParameterDTO(
                name=p.name,
                alias=p.get_alias(),
                type=p.type.value,
                description=p.description
            ) for p in parameters],
        )


@dataclass(frozen=True)
class CommonConfigsDTO:
    atomic_fields: Dict[str, str]
    gdpr_event_parameters: List  # empty
    gdpr_context_parameters: Dict[str, List[str]]
    gdpr_atomic_parameters: List[str]
    close_event_partition_after_hours: int
    context_schemas: Dict[str, SchemaDTO]
    non_embedded_context_schemas: Dict[str, SchemaDTO]
    embedded_context_schemas: Dict[str, SchemaDTO]

    @classmethod
    def from_domain_model(cls, events_by_app: EventsByApp) -> 'CommonConfigsDTO':
        return CommonConfigsDTO(
            atomic_fields={p.name: p.type for p in events_by_app.atomic_parameters},
            gdpr_event_parameters=[],
            gdpr_context_parameters=events_by_app.get_gdpr_context_parameter_names_by_context_name(),
            gdpr_atomic_parameters=events_by_app.get_gdpr_atomic_parameter_names(),
            close_event_partition_after_hours=4,
            context_schemas={e.get_schema().name: SchemaDTO.from_domain_model(e.get_schema(), e.get_alias(), e.get_schema().parameters) for e in events_by_app.event_contexts},
            non_embedded_context_schemas={e.get_schema().name: SchemaDTO.from_domain_model(e.get_schema(), e.get_alias(), e.get_schema().parameters) for e in events_by_app.non_embedded_event_contexts},
            embedded_context_schemas={e.get_schema().name: SchemaDTO.from_domain_model(e.get_schema(), e.get_alias(), e.get_schema().parameters) for e in events_by_app.embedded_event_contexts}
        )


@dataclass(frozen=True)
class DatasourceDTO:
    id: str
    has_data_from: date
    has_data_up_to: date | None

    @classmethod
    def from_domain_model(cls, datasource: Datasource) -> 'DatasourceDTO':
        return cls(
            id=datasource.id,
            has_data_from=datasource.has_data_from,
            has_data_up_to=datasource.has_data_up_to
        )

@dataclass(frozen=True)
class AppConfigDTO:
    gdpr_event_parameters: Dict[str, List[str]]
    timezone: str
    created: date

    datasources: Dict[str, DatasourceDTO]

    event_schemas: Dict[str, SchemaDTO]
    external_services: List
    events_backfill_jobs: List

    @classmethod
    def from_domain_model(cls, app: App, events_by_app: EventsByApp) -> 'AppConfigDTO':
        external_services = []
        if app.appsflyer_integration:
            external_services.append({
                'service_name': 'apps_flyer',
                'service_params': asdict(app.appsflyer_integration) | {'app_id': app.appsflyer_integration.app_id.value}
            })
        if app.appsflyer_cost_etl_integration:
            external_services.append({
                'service_name': 'apps_flyer_cost_etl',
                'service_params': asdict(app.appsflyer_cost_etl_integration)| {'app_id': app.appsflyer_integration.app_id.value}
            })
        if app.store_itunes:
            external_services.append({
                'service_name': 'store_itunes',
                'service_params': asdict(app.store_itunes)| {'app_id': app.store_itunes.app_id.value}
            })
        if app.store_google_play:
            external_services.append({
                'service_name': 'store_google_play',
                'service_params': asdict(app.store_google_play)| {'app_id': app.store_google_play.app_id.value}
            })

        return AppConfigDTO(
            gdpr_event_parameters=events_by_app.get_gdpr_event_parameter_names_by_event_name(app.id),
            timezone=app.timezone.name,
            created=app.created_at.date(),
            datasources={ds.id: DatasourceDTO.from_domain_model(ds) for ds in app.datasources},
            event_schemas={e.get_schema().name: SchemaDTO.from_domain_model(e.get_schema(), e.schema.get_alias(), e.get_schema().parameters)
                            for e in events_by_app.get_events(app.id)},
            external_services=external_services,
            events_backfill_jobs=app.event_backfill_jobs,
        )


@dataclass(frozen=True)
class AllAppsConfigDTO:
    common_configs: CommonConfigsDTO
    app_id_configs: Dict[str, AppConfigDTO]

    @classmethod
    def from_domain_model(cls, app_list: List[App], events_by_app: EventsByApp) -> 'AllAppsConfigDTO':
        return cls(
            common_configs=CommonConfigsDTO.from_domain_model(events_by_app),
            app_id_configs={app.id.value: AppConfigDTO.from_domain_model(app, events_by_app) for app in app_list}
        )
