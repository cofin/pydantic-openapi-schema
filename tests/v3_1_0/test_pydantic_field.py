from typing import Union

from pydantic import BaseModel, Field
from pydantic.schema import schema
from typing_extensions import Literal

from pydantic_openapi_schema.utils.utils import (
    OpenAPI310PydanticSchema,
    construct_open_api_with_schema_class,
)
from pydantic_openapi_schema.v3_1_0 import (
    Discriminator,
    Info,
    MediaType,
    OpenAPI,
    Operation,
    PathItem,
    Reference,
    RequestBody,
    Response,
    Schema,
)


def test_pydantic_discriminator_schema_generation() -> None:
    """https://github.com/kuimono/openapi-schema-pydantic/issues/8."""

    json_schema = schema([RequestModel])
    assert json_schema == {
        "definitions": {
            "DataAModel": {
                "properties": {"kind": {"enum": ["a"], "title": "Kind", "type": "string"}},
                "required": ["kind"],
                "title": "DataAModel",
                "type": "object",
            },
            "DataBModel": {
                "properties": {"kind": {"enum": ["b"], "title": "Kind", "type": "string"}},
                "required": ["kind"],
                "title": "DataBModel",
                "type": "object",
            },
            "RequestModel": {
                "properties": {
                    "data": {
                        "anyOf": [{"$ref": "#/definitions/DataAModel"}, {"$ref": "#/definitions/DataBModel"}],
                        "discriminator": {
                            "mapping": {"a": "#/definitions/DataAModel", "b": "#/definitions/DataBModel"},
                            "propertyName": "kind",
                        },
                        "title": "Data",
                    }
                },
                "required": ["data"],
                "title": "RequestModel",
                "type": "object",
            },
        }
    }


def test_pydantic_discriminator_openapi_generation() -> None:
    """https://github.com/kuimono/openapi-schema-pydantic/issues/8."""

    open_api = construct_open_api_with_schema_class(construct_base_open_api())
    json_schema = open_api.components.schemas["RequestModel"]  # type: ignore
    assert json_schema.properties == {
        "data": Schema(
            anyOf=[
                Reference(ref="#/components/schemas/DataAModel", summary=None, description=None),
                Reference(ref="#/components/schemas/DataBModel", summary=None, description=None),
            ],
            title="Data",
            discriminator=Discriminator(
                propertyName="kind",
                mapping={"a": "#/components/schemas/DataAModel", "b": "#/components/schemas/DataBModel"},
            ),
        )
    }


def construct_base_open_api() -> OpenAPI:
    return OpenAPI(
        info=Info(
            title="My own API",
            version="v0.0.1",
        ),
        paths={
            "/ping": PathItem(
                post=Operation(
                    requestBody=RequestBody(
                        content={
                            "application/json": MediaType(
                                media_type_schema=OpenAPI310PydanticSchema(schema_class=RequestModel)
                            )
                        }
                    ),
                    responses={"200": Response(description="pong")},
                )
            )
        },
    )


class DataAModel(BaseModel):
    kind: Literal["a"]


class DataBModel(BaseModel):
    kind: Literal["b"]


class RequestModel(BaseModel):
    data: Union[DataAModel, DataBModel] = Field(discriminator="kind")
