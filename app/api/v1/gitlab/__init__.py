from fastapi import APIRouter

from .gitlab import router

gitlab_router = APIRouter()
gitlab_router.include_router(router, tags=["GitLab模块"])

__all__ = ["gitlab_router"]