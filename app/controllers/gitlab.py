import gitlab
from typing import List, Dict, Any, Optional
from app.settings.config import settings
from app.log import logger


class GitLabService:
    def __init__(self):
        # Initialize GitLab client
        self.gitlab_url = settings.GITLAB_URL
        self.gitlab_token = settings.GITLAB_TOKEN
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize GitLab client with error handling"""
        try:
            self.client = gitlab.Gitlab(url=self.gitlab_url, private_token=self.gitlab_token, keep_base_url=True)
            # Test connection
            self.client.auth()
            logger.info("GitLab client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize GitLab client: {str(e)}")
            self.client = None

    def _ensure_client(self):
        """Ensure GitLab client is initialized"""
        if not self.client:
            self._initialize_client()
        return self.client is not None

    def get_projects(self, page: int, page_size: int, search: str = "") -> List[Dict[str, Any]]:
        """Get all projects from GitLab"""
        if not self._ensure_client():
            raise Exception("GitLab client not initialized")

        try:
            if search:
                projects = self.client.projects.list(
                    page=page,
                    per_page=page_size,
                    search=search,
                )
                projects_count = len(self.client.projects.list(search=search))
            else:
                projects = self.client.projects.list(page=page, per_page=page_size)
                projects_count = len(self.client.projects.list(get_all=True))
            data = [
                {
                    "id": project.id,
                    "name": project.name,
                    "path": project.path_with_namespace,
                    "description": project.description,
                    "web_url": project.web_url,
                    "last_activity_at": project.last_activity_at,
                }
                for project in projects
            ]
            return projects_count, data
        except Exception as e:
            logger.error(f"Error fetching projects: {str(e)}")
            raise

    def get_project_tags(
        self,
        project_id: int,
    ) -> List[Dict[str, Any]]:
        """Get all tags for a specific project"""
        if not self._ensure_client():
            raise Exception("GitLab client not initialized")

        try:
            project = self.client.projects.get(project_id)
            tags = project.tags.list(all=True)
            return [
                {
                    "name": tag.name,
                    "message": tag.message,
                    "commit": (
                        {
                            "id": tag.commit["id"],
                            "short_id": tag.commit["short_id"],
                            "created_at": tag.commit["created_at"],
                        }
                        if tag.commit
                        else None
                    ),
                }
                for tag in tags
            ]
        except Exception as e:
            logger.error(f"Error fetching tags for project {project_id}: {str(e)}")
            raise

    def get_project_commits(
        self,
        project_id: int,
        page: int,
        page_size: int,
        ref_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Get commits for a specific project"""
        if not self._ensure_client():
            raise Exception("GitLab client not initialized")

        try:
            from datetime import datetime, timedelta

            since = (datetime.now() - timedelta(days=365)).isoformat()
            project = self.client.projects.get(project_id)
            commits = (
                project.commits.list(ref_name=ref_name, page=page, per_page=page_size, since=since)
                if ref_name
                else project.commits.list(page=page, per_page=page_size, since=since)
            )
            all_commits = (
                project.commits.list(
                    get_all=True,
                    since=since,
                    ref_name=ref_name,
                )
                if ref_name
                else project.commits.list(
                    get_all=True,
                    since=since,
                )
            )
            result = []
            for commit in commits:
                result.append(
                    {
                        "id": commit.id,
                        "short_id": commit.short_id,
                        "title": commit.title,
                        "message": commit.message,
                        "author_name": commit.author_name,
                        "author_email": commit.author_email,
                        "created_at": commit.created_at,
                    }
                )
            return len(all_commits), result
        except Exception as e:
            logger.error(f"Error fetching commits for project {project_id}: {str(e)}")
            raise

    def get_project_pipelines(self, project_id: int, page: int, page_size: int) -> List[Dict[str, Any]]:
        """Get pipelines for a specific project"""
        if not self._ensure_client():
            raise Exception("GitLab client not initialized")

        try:
            from datetime import datetime, timedelta

            since = datetime.now() - timedelta(days=365)
            project = self.client.projects.get(project_id)
            pipelines = project.pipelines.list(page=page, per_page=page_size, since=since.isoformat())
            all_pipelines = project.pipelines.list(get_all=True, since=since.isoformat())
            result = []
            for pipeline in pipelines:
                # if pipeline.status == "success":
                data = {
                    "id": pipeline.id,
                    "status": pipeline.status,
                    "ref": pipeline.ref,
                    "sha": pipeline.sha,
                    "web_url": pipeline.web_url,
                }
                result.append(data)
            return len(all_pipelines), result
        except Exception as e:
            logger.error(f"Error fetching pipelines for project {project_id}: {str(e)}")
            raise

    def get_project_details(self, project_id: int) -> Dict[str, Any]:
        """Get detailed information about a specific project"""
        if not self._ensure_client():
            raise Exception("GitLab client not initialized")

        try:
            project = self.client.projects.get(project_id)
            return {
                "id": project.id,
                "name": project.name,
                "path_with_namespace": project.path_with_namespace,
                "description": project.description,
                "web_url": project.web_url,
                "ssh_url_to_repo": project.ssh_url_to_repo,
                "http_url_to_repo": project.http_url_to_repo,
                "default_branch": project.default_branch,
                "created_at": project.created_at,
                "last_activity_at": project.last_activity_at,
            }
        except Exception as e:
            logger.error(f"Error fetching details for project {project_id}: {str(e)}")
            raise


# Create a singleton instance
gitlab_service = GitLabService()
