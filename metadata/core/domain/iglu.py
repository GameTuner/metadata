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

from dataclasses import dataclass
import json
from typing import Dict, List
from metadata.core.domain.schema import Schema, SchemaParameter


def convert_simple_type(parameter_type: str) -> str:
    return {
        'integer': 'integer',
        'number': 'number',
        'boolean': 'boolean',
        'string': 'string',
        'date': 'string',
        'datetime': 'string',
    }[parameter_type]


@dataclass(frozen=True)
class IgluSchema:
    path: str
    schema: Dict[str, object]

    def schema_to_json_string(self):
        return json.dumps(self.schema)

    @classmethod
    def _build_property(cls, schema_parameter: SchemaParameter):
        if schema_parameter.type.startswith("map<"):
            return {
                "type": "array",
                "description": schema_parameter.description or "",
                "items": {
                    "type": "object",
                    "properties": {
                        "key": {"type": "string"},
                        "value": {"type": convert_simple_type(schema_parameter.type.value.split(",")[1][:-1])}
                    },
                    "required": ["key", "value"],
                    "additionalProperties": False,
                }
            }
        return {
            "type": convert_simple_type(schema_parameter.type.value),
            "description": schema_parameter.description or "",
        }

    @classmethod
    def from_schema(cls, schema: Schema, schema_parameters: List[SchemaParameter], version: int, override_url_schema_name: str = None) -> 'IgluSchema':
        properties_dict = {}
        for schema_parameter in schema_parameters:
            properties_dict[schema_parameter.name] = cls._build_property(schema_parameter)

        schema_name = override_url_schema_name if override_url_schema_name else schema.name
        return IgluSchema(
            path=f'{schema.vendor}/{schema_name}/jsonschema/1-0-{version}',
            schema={
                "$schema": "http://iglucentral.com/schemas/com.snowplowanalytics.self-desc/schema/jsonschema/1-0-0#",
                "description": schema.description or "",
                "self": {
                    "vendor": schema.vendor,
                    "name": schema_name,
                    "format": "jsonschema",
                    "version": f"1-0-{version}"
                },
                "type": "object",
                "properties": properties_dict,
                "additionalProperties": False,
            })
