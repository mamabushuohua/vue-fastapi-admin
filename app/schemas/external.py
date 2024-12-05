from pydantic import BaseModel, Field, RootModel
from typing import List


class GitlabProject(BaseModel):
    namespace: str = Field(..., description="The namespace of the item")
    name: str = Field(..., description="The name of the item")
    branch: str = Field(..., description="The branch of the item")


class GitlabCreateTag(BaseModel):
    projects: List[GitlabProject] = Field(..., description="The list of projects")
    tag: str = Field(..., description="The tag of the item")
    description: str = Field(..., description="The description of the tag")
