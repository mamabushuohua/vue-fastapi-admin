import re
from datetime import datetime
import json

from fastapi import FastAPI
from fastapi.responses import Response, JSONResponse
from fastapi.routing import APIRoute
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.types import ASGIApp, Receive, Scope, Send

from app.core.dependency import AuthControl
from app.models.admin import AuditLog, User

from .bgtask import BgTasks
from app.log import logger
from app.utils.generate_hash import sanitize_data


class SimpleBaseMiddleware:
    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)

        response = await self.before_request(request) or self.app
        await response(request.scope, request.receive, send)
        await self.after_request(request)

    async def before_request(self, request: Request):
        return self.app

    async def after_request(self, request: Request):
        return None


class BackGroundTaskMiddleware(SimpleBaseMiddleware):
    async def before_request(self, request):
        await BgTasks.init_bg_tasks_obj()

    async def after_request(self, request):
        await BgTasks.execute_tasks()


class HttpAuditLogMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, methods: list, exclude_paths: list):
        super().__init__(app)
        self.methods = methods
        self.exclude_paths = exclude_paths

    async def get_request_log(self, request: Request, response: Response) -> dict:
        """
        根据request和response对象获取对应的日志记录数据
        """
        data: dict = {"path": request.url.path, "status": response.status_code, "method": request.method}
        # 路由信息
        app: FastAPI = request.app
        for route in app.routes:
            if (
                isinstance(route, APIRoute)
                and route.path_regex.match(request.url.path)
                and request.method in route.methods
            ):
                data["module"] = ",".join(route.tags)
                data["summary"] = route.summary
        # 获取用户信息
        try:
            token = request.headers.get("token")
            user_obj = None
            if token:
                user_obj: User = await AuthControl.is_authed(token)
            data["user_id"] = user_obj.id if user_obj else 0
            data["username"] = user_obj.username if user_obj else ""
        except Exception:
            data["user_id"] = 0
            data["username"] = ""
        return data

    async def before_request(self, request: Request):
        pass

    async def after_request(self, request: Request, response: Response, process_time: int, params: str, body: str):
        if request.method in self.methods:  # 请求方法为配置的记录方法
            for path in self.exclude_paths:
                if re.search(path, request.url.path, re.I) is not None:
                    return
            data: dict = await self.get_request_log(request=request, response=response)
            data["response_time"] = process_time  # 响应时间
            data["params"] = params  # 请求参数
            data["body"] = body  # 返回体
            logger.debug(
                f"Request: {request.method} {request.url.path}\
                - Status Code: {response.status_code} \
                - Process Time: {process_time} ms \
                - Query Params: {params}\
                - Response Body: {body}\
                "
            )
            await AuditLog.create(**data)

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        start_time: datetime = datetime.now()
        params = None
        if request.method == "GET":
            params = await sanitize_data(dict(request.query_params))
            logger.debug(f"Request: {request.method} {request.url.path} - Query Params: {params}")
        else:
            _body = await request.json()
            params = await sanitize_data(_body)
            logger.debug(f"Request: {request.method} {request.url.path} - Body: {params}")

        await self.before_request(request)
        response: Response = await call_next(request)
        end_time: datetime = datetime.now()
        process_time = int((end_time.timestamp() - start_time.timestamp()) * 1000)

        # 返回体 // TODO 可能有bug 当返回体是文件流的时候呢？
        response_content = None
        # for path in self.exclude_paths:
        #     if re.search(path, request.url.path, re.I) is None:
        #         response_body = [section async for section in response.body_iterator]
        #         response.body_iterator = iter(response_body)  # 重置响应体迭代器
        #         response_content = b"".join(response_body).decode("utf-8")
        # return Response(content=response_content, status_code=response.status_code, headers=dict(response.headers))

        await self.after_request(request, response, process_time, params, response_content)
        return response
