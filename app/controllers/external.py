import httpx
import gitlab

from app.settings import settings
from app.log import logger


class ExternalController:

    # 关闭流水线的函数
    async def cancel_pipeline(project_id: int, pipeline_id: int):
        async with httpx.AsyncClient() as client:

            # GitLab API 请求 headers
            headers = {"Authorization": f"Bearer {settings.GITLAB_PRIVATE_TOKEN}", "Content-Type": "application/json"}
            url = f"{settings.GITLAB_API_URL}/projects/{project_id}/pipelines/{pipeline_id}/cancel"
            response = await client.post(url, headers=headers)
            # print(response)
            if response.status_code == 200:
                return True
            else:
                return Exception(f"Failed to cancel pipeline: {response.text}")

    # 创建标签
    async def create_tag(self, tag_info: dict):
        logger.info(f"create_tag: {tag_info.tag}, description: {tag_info.description}")
        for item in tag_info.projects:
            logger.debug(f"create_tag: {item}")
            gitlab_helper.create_tag(item.namespace, item.name, tag_info.tag, tag_info.description)


class GitlabHelper:

    def __init__(self):
        self.gl = gitlab.Gitlab(settings.GITLAB_API_URL, private_token=settings.GITLAB_PRIVATE_TOKEN)

    def create_tag(self, namespace, name, tag, description):
        try:
            project = self.gl.projects.get(namespace + "/" + name)
            logger.debug(f"project info: {project}")
        except Exception as e:
            logger.error(f"Failed to get project: {e}")
            raise e


external_controller = ExternalController()
gitlab_helper = GitlabHelper()
