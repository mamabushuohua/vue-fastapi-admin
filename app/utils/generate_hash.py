import hashlib


def generate_hash(input_string, algorithm="sha256"):
    # 选择哈希算法
    if algorithm == "sha256":
        hash_object = hashlib.sha256()
    elif algorithm == "md5":
        hash_object = hashlib.md5()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    # 更新哈希对象
    hash_object.update(input_string.encode("utf-8"))

    # 返回十六进制哈希值
    return hash_object.hexdigest()


# 定义敏感信息字段
SENSITIVE_FIELDS = ["password", "ssn", "credit_card", "access_token"]


async def sanitize_data(data):
    """去敏处理函数"""
    if isinstance(data, dict):
        return {k: ("***" if k in SENSITIVE_FIELDS else v) for k, v in data.items()}
    if isinstance(data, list):
        return [
            "***" if isinstance(item, dict) and any(field in item for field in SENSITIVE_FIELDS) else item
            for item in data
        ]
    return data


if __name__ == "__main__":
    input_string = "hello, world!"  # 替换为您要哈希的字符串
    sha256_hash = generate_hash(input_string, "sha256")
    md5_hash = generate_hash(input_string, "md5")

    print(f"SHA-256 Hash: {sha256_hash}")
    print(f"MD5 Hash: {md5_hash}")
