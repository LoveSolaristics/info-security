from typing import Optional
from pydantic import Field, BaseModel, AnyHttpUrl


class DefaultErrorResponse(BaseModel):
    message: str = Field(description='error reason')
    info: Optional[str] = Field(description='addition information')


class RegisterRequest(BaseModel):
    token: str
    role: str = Field(default='user')


class RegisterResponse(BaseModel):
    message: str = 'registration-completed-successfully'


class AppOnlineResponse(BaseModel):
    message: str = "app-is-online"


class CreateProjectRequest(BaseModel):
    name: str


class CreateProjectResponse(BaseModel):
    project_id: int


class GetProjectRequest(BaseModel):
    project_name: str


class GetProjectResponse(BaseModel):
    name: str
    grant: bool
    read: bool
    write: bool


class UpdateProjectRequest(BaseModel):
    project_name: str
    new_name: str = Field(alias='name', default=None)


class UpdateProjectResponse(BaseModel):
    message: str = 'update-success'


class Rights(BaseModel):
    read: bool = Field(default='False')
    write: bool = Field(default='False')
    grant: bool = Field(default='False')
