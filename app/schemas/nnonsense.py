from uuid import UUID

from pydantic import BaseModel, Field


class NonsenseSchema(BaseModel):
    name: str = Field(
        title="",
        description="",
    )
    description: str = Field(
        title="",
        description="",
    )

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "name": "Name for Some Nonsense",
                "description": "Some Nonsense Description",
            }
        }


class NonsenseResponse(BaseModel):
    id: UUID = Field(
        title="Id",
        description="",
    )
    name: str = Field(
        title="",
        description="",
    )
    description: str = Field(
        title="",
        description="",
    )

    class Config:
        orm_mode = True
        schema_extra = {
            "example": {
                "config_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "name": "Name for Some Nonsense",
                "description": "Some Nonsense Description",
            }
        }
