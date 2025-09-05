"""
Author        yongfa
Date          2025-08-26 17:43:36
LastEditTime  2025-08-28 18:12:10
LastEditors   yongfa
Description   初始化数据
"""

from tortoise.expressions import Q

from app.controllers.api import api_controller
from app.controllers.user import UserCreate, user_controller
from app.models.admin import Api, Menu, Role, Dept
from app.schemas.menus import MenuType
from app.log import logger
from app.settings import settings


async def init_superuser():
    """初始化超级用户"""
    user = await user_controller.model.exists()
    if not user:
        await user_controller.create_user(
            UserCreate(
                username="admin",
                email="admin@admin.com",
                password="123456",
                is_active=True,
                is_superuser=True,
            )
        )


async def init_menus():
    """初始化菜单"""
    menus_data = [
        {
            "menu_type": MenuType.CATALOG,
            "name": "系统管理",
            "path": "/system",
            "order": 1,
            "parent_id": 0,
            "icon": "carbon:gui-management",
            "is_hidden": False,
            "component": "Layout",
            "keepalive": False,
            "redirect": "/system/user",
            "children": [
                {
                    "menu_type": MenuType.MENU,
                    "name": "用户管理",
                    "path": "user",
                    "order": 1,
                    "parent_id": None,
                    "icon": "material-symbols:person-outline-rounded",
                    "is_hidden": False,
                    "component": "/system/user",
                    "keepalive": False,
                },
                {
                    "menu_type": MenuType.MENU,
                    "name": "角色管理",
                    "path": "role",
                    "order": 2,
                    "parent_id": None,
                    "icon": "carbon:user-role",
                    "is_hidden": False,
                    "component": "/system/role",
                    "keepalive": False,
                },
                {
                    "menu_type": MenuType.MENU,
                    "name": "菜单管理",
                    "path": "menu",
                    "order": 3,
                    "parent_id": None,
                    "icon": "material-symbols:list-alt-outline",
                    "is_hidden": False,
                    "component": "/system/menu",
                    "keepalive": False,
                },
                {
                    "menu_type": MenuType.MENU,
                    "name": "API管理",
                    "path": "api",
                    "order": 4,
                    "parent_id": None,
                    "icon": "ant-design:api-outlined",
                    "is_hidden": False,
                    "component": "/system/api",
                    "keepalive": False,
                },
                {
                    "menu_type": MenuType.MENU,
                    "name": "部门管理",
                    "path": "dept",
                    "order": 5,
                    "parent_id": None,
                    "icon": "mingcute:department-line",
                    "is_hidden": False,
                    "component": "/system/dept",
                    "keepalive": False,
                },
                {
                    "menu_type": MenuType.MENU,
                    "name": "审计日志",
                    "path": "auditlog",
                    "order": 6,
                    "parent_id": None,
                    "icon": "ph:clipboard-text-bold",
                    "is_hidden": False,
                    "component": "/system/auditlog",
                    "keepalive": False,
                },
            ],
        },
        {
            "menu_type": MenuType.MENU,
            "name": "一级菜单",
            "path": "/top-menu",
            "order": 2,
            "parent_id": 0,
            "icon": "material-symbols:featured-play-list-outline",
            "is_hidden": False,
            "component": "/top-menu",
            "keepalive": False,
            "redirect": "",
        },
        {
            "menu_type": MenuType.CATALOG,
            "name": "Gitalb集成",
            "path": "/gitlab",
            "order": 2,
            "parent_id": 0,
            "icon": "material-symbols:featured-play-list-outline",
            "is_hidden": False,
            "component": "/gitlab",
            "keepalive": False,
            "redirect": "",
            "children": [
                {
                    "menu_type": MenuType.MENU,
                    "name": "tags",
                    "path": "tags",
                    "order": 10,
                    "parent_id": None,
                    "icon": "material-symbols:featured-play-list-outline",
                    "is_hidden": False,
                    "component": "/gitlab/tags",
                    "keepalive": False,
                },
                {
                    "menu_type": MenuType.MENU,
                    "name": "projects",
                    "path": "projects",
                    "order": 9,
                    "parent_id": None,
                    "icon": "material-symbols:featured-play-list-outline",
                    "is_hidden": False,
                    "component": "/gitlab/projects",
                    "keepalive": False,
                },
                {
                    "menu_type": MenuType.MENU,
                    "name": "commits",
                    "path": "commits",
                    "order": 10,
                    "parent_id": None,
                    "icon": "material-symbols:featured-play-list-outline",
                    "is_hidden": False,
                    "component": "/gitlab/commits",
                    "keepalive": False,
                },
                {
                    "menu_type": MenuType.MENU,
                    "name": "pipelines",
                    "path": "pipelines",
                    "order": 10,
                    "parent_id": None,
                    "icon": "material-symbols:featured-play-list-outline",
                    "is_hidden": False,
                    "component": "/gitlab/pipelines",
                    "keepalive": False,
                },
            ],
        },
    ]

    async def handle_menus(menus_data):
        for menu in menus_data:
            children_menus_data = menu.pop("children", [])

            parent_menu, created = await Menu.update_or_create(defaults=menu, name=menu["name"], path=menu["path"])

            if created:
                logger.debug(f"Created new parent_menu: {parent_menu.name} ({parent_menu.path})")
            else:
                logger.debug(f"Updated existing parent_menu: {parent_menu.name} ({parent_menu.path})")

            for child_menu_data in children_menus_data:
                child_menu_data["parent_id"] = parent_menu.id
                child_menu, created = await Menu.update_or_create(
                    defaults=child_menu_data, name=child_menu_data["name"], path=child_menu_data["path"]
                )

                if created:
                    logger.debug(f"Created new child_menu: {child_menu.name} ({child_menu.path})")
                else:
                    logger.debug(f"Updated child_menu: {child_menu.name} ({child_menu.path})")

    roles = await Role.exists()
    if not roles:
        logger.debug("初始化首次菜单...")
        await handle_menus(menus_data)
    # if settings.DEBUG:
    #     logger.debug("初始化菜单...")
    #     await handle_menus(menus_data)


async def init_apis():
    """初始化api"""
    apis = await api_controller.model.exists()
    if not apis:
        await api_controller.refresh_api()


async def init_roles():
    """初始化角色"""
    roles = await Role.exists()
    if not roles:
        admin_role = await Role.create(
            name="管理员",
            desc="管理员角色",
        )
        user_role = await Role.create(
            name="普通用户",
            desc="普通用户角色",
        )

        # 分配所有API给管理员角色
        all_apis = await Api.all()
        await admin_role.apis.add(*all_apis)
        # 分配所有菜单给管理员和普通用户
        all_menus = await Menu.all()
        await admin_role.menus.add(*all_menus)
        await user_role.menus.add(*all_menus)

        # 为普通用户分配基本API
        basic_apis = await Api.filter(Q(method__in=["GET"]) | Q(tags="基础模块"))
        await user_role.apis.add(*basic_apis)


async def init_depts():
    """初始化部门"""
    parent_depts_data = [
        {
            "name": "Devops公司",
            "parent_id": 0,
            "order": 1,
            "children": [
                {
                    "name": "部门1",
                    "parent_id": 1,
                    "order": 2,
                },
                {
                    "name": "部门2",
                    "parent_id": 1,
                    "order": 3,
                },
            ],
        }
    ]

    for dept_data in parent_depts_data:
        children_depts_data = dept_data.pop("children", [])

        # 处理父部门 - 存在则更新，不存在则创建
        # 同时考虑软删除的情况，如果部门被软删除(is_deleted=True)，则恢复它
        parent_dept_obj = await Dept.filter(name=dept_data["name"]).first()
        if parent_dept_obj:
            # 更新已存在的部门
            parent_dept_obj.parent_id = dept_data["parent_id"]
            parent_dept_obj.order = dept_data["order"]
            parent_dept_obj.is_deleted = False  # 恢复软删除的部门
            await parent_dept_obj.save()
        else:
            # 创建新部门
            parent_dept_obj = await Dept.create(**dept_data)

        # 处理子部门 - 存在则更新，不存在则创建
        for child_dept_data in children_depts_data:
            child_dept_data["parent_id"] = parent_dept_obj.id
            child_dept_obj = await Dept.filter(name=child_dept_data["name"]).first()
            if child_dept_obj:
                # 更新已存在的子部门
                child_dept_obj.parent_id = child_dept_data["parent_id"]
                child_dept_obj.order = child_dept_data["order"]
                child_dept_obj.is_deleted = False  # 恢复软删除的部门
                await child_dept_obj.save()
            else:
                # 创建新子部门
                await Dept.create(**child_dept_data)
