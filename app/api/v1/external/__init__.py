from fastapi import APIRouter

from .external import router

external_router = APIRouter()
external_router.include_router(router, tags=["外部模板"])

__all__ = ["external_router"]
