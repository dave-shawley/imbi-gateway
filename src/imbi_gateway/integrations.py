import datetime
import typing as t
import uuid

import fastapi
import pydantic
import slugify

from imbi_gateway import postgres

router = fastapi.APIRouter(prefix='/integrations')

type Name = t.Annotated[
    str, pydantic.StringConstraints(strip_whitespace=True, min_length=3)
]
type Slug = t.Annotated[
    str,
    pydantic.StringConstraints(
        strip_whitespace=True, pattern=r'[a-z][-_a-z0-9]+[a-z]'
    ),
]
type CELPattern = str


class Auditable(pydantic.BaseModel):
    created_by: Slug
    created_at: datetime.datetime
    updated_by: Slug | None = None
    updated_at: datetime.datetime | None = None


class IntegrationConfiguration(Auditable):
    name: Name
    slug: Slug


class CreateHookRequest(pydantic.BaseModel):
    name: Name
    slug: Slug
    identifier_pattern: CELPattern | None = None


class HookConfiguration(Auditable):
    hook_id: t.Annotated[
        uuid.UUID, pydantic.Field(description='Surrogate hook ID')
    ]
    name: Name
    slug: Slug
    integration: Slug
    identifier_pattern: CELPattern | None = None


class CreateIntegrationRequest(pydantic.BaseModel):
    name: Name


@router.post('/', operation_id='create-integration')
async def create_integration(
    *,
    request: CreateIntegrationRequest,
    conn: postgres.Connection,
) -> IntegrationConfiguration:
    async with postgres.model_cursor(conn, IntegrationConfiguration) as cursor:
        result = await cursor.execute(
            'INSERT INTO integrations(name, slug, created_by) '
            'VALUES (%(name)s, %(slug)s, %(created_by)s) '
            'RETURNING *',
            {
                'name': request.name,
                'slug': slugify.slugify(request.name),
                'created_by': 'todo',
            },
        )
        if row := await result.fetchone():
            return row
        raise fastapi.HTTPException(500)
