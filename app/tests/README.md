# 测试说明

## 运行测试

### 安装测试依赖

```bash
pip install pytest pytest-asyncio httpx
```

### 运行所有测试

```bash
python -m pytest tests/ -v
```

### 运行特定测试文件

```bash
# 运行base模块测试
python -m pytest tests/test_base.py -v

# 运行依赖项测试
python -m pytest tests/test_dependency.py -v

# 运行token工具测试
python -m pytest tests/test_token_utils.py -v
```

## 测试结构

```
tests/
├── conftest.py          # 测试配置和fixtures
├── test_base.py         # base模块测试
├── test_dependency.py   # 依赖项测试
```

## 测试内容

### test_base.py

- JWTOut schema测试

### test_dependency.py

- AuthControl.is_authed() 方法测试
- AuthControl.is_refresh_token_valid() 方法测试
- 各种认证场景测试（dev token, 无效token, 过期token等）

## 注意事项

1. 测试使用mock来避免真实的数据库和Redis连接
2. 部分测试可能需要Redis服务器运行才能完全验证功能
3. 测试使用pytest-asyncio来支持异步测试
