from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr

config = ConfigDict(from_attributes=True)


# TODO: add pydantic field validator for strong password
class UserSchema(BaseModel):
    model_config = config
    email: EmailStr = Field(
        title="User’s email", description="User’s email", examples=["john@domain.com"]
    )
    first_name: str = Field(
        title="User’s first name", description="User’s first name", examples=["John"]
    )
    last_name: str = Field(
        title="User’s last name", description="User’s last name", examples=["Doe"]
    )
    password: SecretStr = Field(
        title="User’s password",
        description="User’s password",
        examples=["@SuperSecret123"],
    )


class UserResponse(BaseModel):
    id: UUID = Field(title="User’s id", description="User’s id")
    email: EmailStr = Field(title="User’s email", description="User’s email")
    first_name: str = Field(title="User’s first name", description="User’s first name")
    last_name: str = Field(title="User’s last name", description="User’s last name")
    access_token: str = Field(title="User’s token", description="User’s token")


class TokenResponse(BaseModel):
    access_token: str = Field(
        title="User’s access token", description="User’s access token"
    )
    token_type: str = Field(title="User’s token type", description="User’s token type")


class UserLogin(BaseModel):
    model_config = config
    email: EmailStr = Field(
        title="User’s email", description="User’s email", examples=["john@domain.com"]
    )
    password: SecretStr = Field(
        title="User’s password",
        description="User’s password",
        examples=["@SuperSecret123"],
    )
