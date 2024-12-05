"""
Author        yongfa
Date          2024-12-03 19:41:37
LastEditTime  2024-12-05 14:44:18
LastEditors   yongfa
Description   外部模板
"""

from fastapi import APIRouter, Request


from app.schemas import Success, Fail
from app.controllers.external import external_controller
from app.log import logger
from app.schemas.external import GitlabCreateTag


router = APIRouter()


@router.get("/", summary="外部接口")
async def external():
    return Success()


@router.post("/merge_request", summary="合并请求")
async def external_merge_request(request: Request):
    try:
        payload = await request.json()
    except Exception as e:
        return Fail(msg=f"Error parsing request body: {str(e)}")
    # 检查事件类型和合并请求状态
    if payload.get("object_attributes", {}).get("state") == "closed":
        # mr_id = payload["object_attributes"]["id"]
        project_id = payload["project"]["id"]
        pipeline_id = payload.get("object_attributes").get("head_pipeline_id")

        # 调用 GitLab API 关闭流水线
        try:
            await external_controller.cancel_pipeline(project_id, pipeline_id)
            return Success(msg=f"Pipeline {pipeline_id} cancelled successfully.")
        except Exception as e:
            return Fail(msg=f"Error cancelling pipeline: {str(e)}")

    return Fail(msg="Not a closed merge request.")


@router.post("/create_tag", summary="创建tag")
async def external_create_tag(items: GitlabCreateTag):
    try:
        await external_controller.create_tag(items)
    except Exception as e:
        logger.error(f"Error creating tag: {str(e)}")
        return Fail(msg=f"Error creating tag: {str(e)}")
    return Success()
