from fastapi import APIRouter, Query, HTTPException
from typing import Optional

from app.controllers.gitlab import gitlab_service
from app.schemas import SuccessExtra, Success
from app.core.dependency import DependPermission

router = APIRouter()


@router.get("/projects", summary="获取所有GitLab项目")
async def get_gitlab_projects(
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
    name: str = Query(None, description="项目名称搜索"),
):
    try:
        total, projects = gitlab_service.get_projects(page, page_size, name)

        return SuccessExtra(data=projects, total=total, page=page, page_size=page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目失败: {str(e)}")


@router.get("/projects/{project_id}/tags", summary="获取项目的所有标签")
async def get_project_tags(
    project_id: int,
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
):
    try:
        tags = gitlab_service.get_project_tags(project_id)
        return SuccessExtra(data=tags, total=len(tags), page=1, page_size=len(tags))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取标签失败: {str(e)}")


@router.get("/projects/{project_id}/commits", summary="获取项目的所有提交")
async def get_project_commits(
    project_id: int,
    ref_name: Optional[str] = Query(None, description="分支或标签名"),
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
):
    try:
        total, commits = gitlab_service.get_project_commits(project_id, page, page_size, ref_name)
        return SuccessExtra(data=commits, total=total, page=page, page_size=page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取提交失败: {str(e)}")


@router.get("/projects/{project_id}/pipelines", summary="获取项目的所有流水线")
async def get_project_pipelines(
    project_id: int,
    page: int = Query(1, description="页码"),
    page_size: int = Query(10, description="每页数量"),
):
    try:
        total, pipelines = gitlab_service.get_project_pipelines(project_id, page, page_size)

        return SuccessExtra(data=pipelines, total=total, page=page, page_size=page_size)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取流水线失败: {str(e)}")


@router.get("/projects/{project_id}", summary="获取项目详情")
async def get_project_details(project_id: int):
    try:
        project_details = gitlab_service.get_project_details(project_id)
        return Success(data=project_details)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取项目详情失败: {str(e)}")
