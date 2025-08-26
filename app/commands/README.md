# 自定义命令管理工具

这个工具允许你通过命令行执行自定义管理命令，类似于Django的manage.py。

## 环境配置

在使用命令之前，请确保正确配置了环境变量。可以通过创建 `.env` 文件来设置环境变量：

```bash
# 复制示例配置文件
cp .env.example .env

# 编辑 .env 文件以匹配你的环境配置
nano .env
```

## 使用方法

### 列出所有可用命令

```bash
python manage.py --list
```

### 执行命令

```bash
python manage.py <command_name> [options]
```

## 可用命令

### 1. reset_db - 重置数据库

重置数据库，删除所有表并重新创建它们。

```bash
# 交互式重置（会提示确认）
python manage.py reset_db

# 非交互式重置（不会提示确认）
python manage.py reset_db --no-input
```

命令说明：
- 该命令会删除所有数据库表并重新创建它们
- 会重新初始化所有数据（用户、角色、菜单、API等）
- 使用`--no-input`参数可以跳过确认提示

### 2. import_menu_api - 导入菜单API

从应用程序中导入新的菜单API。

```bash
# 导入菜单API
python manage.py import_menu_api

# 强制导入菜单API（即使已存在）
python manage.py import_menu_api --force
```

命令说明：
- 该命令会扫描应用程序中的所有API路由
- 自动创建新的API记录或更新现有记录
- 使用`--force`参数可以强制重新导入所有API

## 添加新命令

要添加新命令，请执行以下步骤：

1. 在 `app/commands/` 目录中创建一个新的命令文件（例如 `my_command.py`）
2. 创建一个继承自 `BaseCommand` 的类
3. 实现 `handle` 方法，这是命令的主逻辑
4. （可选）实现 `add_arguments` 方法来添加自定义参数
5. 在 `manage.py` 中注册命令

示例：

```python
# app/commands/my_command.py
from app.commands.base import BaseCommand

class MyCommand(BaseCommand):
    help = "Description of my command"

    def add_arguments(self, parser):
        parser.add_argument('--option', type=str, help='An option for the command')

    def handle(self, *args, **options):
        # Command logic here
        print("Executing my command")
        if options.get('option'):
            print(f"Option value: {options['option']}")
```

然后在 `manage.py` 中注册：

```python
# manage.py
from app.commands.my_command import MyCommand

# 在main函数中注册命令
command_manager.register("my_command", MyCommand)
```
