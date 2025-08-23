from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

config = ConfigDict(from_attributes=True)


class RandomStuff(BaseModel):
    chaos: dict[str, Any] = Field(
        ..., description="Pretty chaotic JSON data can be added here..."
    )


class StuffSchema(BaseModel):
    name: str = Field(
        title="",
        description="",
    )
    description: str = Field(
        title="",
        description="",
    )

    # class Config:
    #     from_attributes = True
    #     json_schema_extra = {
    #         "example": {
    #             "name": "Name for Some Stuff",
    #             "description": "Some Stuff Description",
    #         }
    #     }


class StuffResponse(BaseModel):
    model_config = config
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

    # class Config:
    #     from_attributes = True
    #     json_schema_extra = {
    #         "example": {
    #             "config_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
    #             "name": "Name for Some Stuff",
    #             "description": "Some Stuff Description",
    #         }
    #     }
