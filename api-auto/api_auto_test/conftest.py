from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any

import pytest

from common.assertion import assert_http_ok, assert_result_code
from common.redis_client import RedisClient
from common.request_client import RequestClient
from config.settings import settings


'''
1.先读配置
2.再建客户端
3.再拿账号和 token
4.再准备图片和记录前置
5.最后把这些对象交给测试方法使用
'''


# 提供全局配置对象，供 fixture 和测试用例统一读取。
@pytest.fixture(scope="session")
def app_settings():
    return settings


# 提供全局复用的 HTTP 请求客户端。
@pytest.fixture(scope="session")
def client(app_settings):
    return RequestClient(base_url=app_settings.base_url, timeout=app_settings.timeout)


# 提供全局复用的 Redis 客户端，不可用时直接跳过依赖它的测试。
@pytest.fixture(scope="session")
def redis_client(app_settings):
    client = RedisClient(
        host=app_settings.redis["host"],
        port=int(app_settings.redis["port"]),
        db=int(app_settings.redis.get("db", 0)),
        password=app_settings.redis.get("password"),
        socket_timeout=int(app_settings.redis.get("socket_timeout", 5)),
    )
    try:
        client.ping()
    except Exception as exc:
        pytest.skip(f"Redis 不可用: {exc}")
    yield client
    client.close()


# 返回配置文件中定义的测试账号集合。
@pytest.fixture(scope="session")
def accounts(app_settings):
    return app_settings.accounts


# 校验并返回测试素材图片路径映射。
@pytest.fixture(scope="session")
def image_paths(app_settings):
    paths = {key: Path(value) for key, value in app_settings.paths.items()}
    missing = [str(path) for path in paths.values() if not path.exists()]
    if missing:
        pytest.skip(f"测试素材不存在: {missing}")
    return paths


# 创建运行时临时文件，专门用于空文件和伪图片等异常场景。
@pytest.fixture(scope="session")
def runtime_files(tmp_path_factory):
    temp_dir = tmp_path_factory.mktemp("runtime_files")
    empty_file = temp_dir / "empty.jpg"
    empty_file.write_bytes(b"")
    fake_jpg = temp_dir / "fake.jpg"
    fake_jpg.write_text("this is not a real image", encoding="utf-8")
    return {
        "empty_file": empty_file,
        "fake_jpg": fake_jpg,
    }

'''
主要用来缓存：
1.上传后的 OSS URL
2.是否已准备过上传前置
3.是否已准备过记录前置

因为很多接口测试有前后依赖：
1.搜索需要先上传图片
2.编辑需要先有自己的图片 URL
3.合并需要先有人物图和服装图
4.记录需要先有 edit/merge 记录
'''
# 提供跨测试共享的上下文字典，用于缓存前置生成的数据。
@pytest.fixture(scope="session")
def api_context():
    # 用 session 级上下文缓存跨用例复用的数据，避免重复上传和重复编辑。
    return {}


# 通过账号密码登录并返回认证接口中的 data 字段。
def _password_login(client: RequestClient, account: str, password: str) -> dict[str, Any]:
    response = client.request(
        "POST",
        "/api/user/auth",
        json={"account": account, "password": password},
    )
    assert_http_ok(response)
    result = response.json()
    assert_result_code(result, 200)
    return result["data"]


# 按后端约定的 Redis key 规则读取用户 token。
def _get_token_from_redis(redis_client: RedisClient, user_id: int, key_prefix: str) -> str | None:
    return redis_client.get(f"{key_prefix}{user_id}")


# 解析指定账号的身份信息，并优先使用 Redis 中的最新 token。
def _resolve_user_identity(
    client: RequestClient,
    redis_client: RedisClient,
    key_prefix: str,
    account: str,
    password: str,
) -> dict[str, Any]:
    # 先走一次账号密码登录拿到 userId，再按后端真实 Redis key 规则取最新 token。
    auth_data = _password_login(client, account, password)
    token = _get_token_from_redis(redis_client, int(auth_data["userId"]), key_prefix)
    auth_data["token"] = token or auth_data["token"]
    return auth_data


# 为三个测试账号构建 userId、token 等身份信息映射。
@pytest.fixture(scope="session")
def user_identity_map(client, redis_client, accounts, app_settings, new_user_credentials):
    key_prefix = app_settings.redis["key_prefix"]
    yang = _resolve_user_identity(
        client,
        redis_client,
        key_prefix,
        accounts["yang"]["account"],
        accounts["yang"]["password"],
    )
    xiao = _resolve_user_identity(
        client,
        redis_client,
        key_prefix,
        accounts["xiao"]["account"],
        accounts["xiao"]["password"],
    )
    new_user = _resolve_user_identity(
        client,
        redis_client,
        key_prefix,
        new_user_credentials["account"],
        new_user_credentials["password"],
    )
    return {
        "yang": yang,
        "xiao": xiao,
        "new_user": new_user,
    }


# 动态生成一个不会与现有账号冲突的新用户账号密码。
@pytest.fixture(scope="session")
def new_user_credentials():
    suffix = uuid.uuid4().hex[:8]
    return {
        "account": f"NewUser_{suffix}",
        "password": "NewPass123",
    }


# 统一构造各种 Authorization 请求头场景。
def get_auth_headers(token: str | None = None, mode: str = "valid") -> dict[str, str]:
    # 统一在这里构造各种鉴权头，测试代码里只关心场景，不重复拼 Authorization。
    if mode == "none":
        return {}
    if mode == "empty":
        return {"Authorization": ""}
    if mode == "invalid_format":
        return {"Authorization": "token-x"}
    if mode == "fake_jwt":
        return {"Authorization": "Bearer abc.def.ghi"}
    if mode == "old_token":
        return {"Authorization": "Bearer old-token"}
    if mode == "revoked_token":
        return {"Authorization": "Bearer __REVOKED_TOKEN__"}
    if mode == "bearer_blank":
        return {"Authorization": "Bearer "}
    if token is None:
        raise ValueError("valid 模式下必须提供 token")
    return {"Authorization": f"Bearer {token}"}


# 汇总三个测试账号的 token，便于用 auth 标识直接取用。
@pytest.fixture(scope="session")
def token_map(user_identity_map):
    return {
        "yang": user_identity_map["yang"]["token"],
        "xiao": user_identity_map["xiao"]["token"],
        "new_user": user_identity_map["new_user"]["token"],
    }


# 执行一次上传图片接口调用，并返回上传成功后的 data。
def upload_file(client: RequestClient, token: str, file_path: Path, content_type: str | None = None) -> dict[str, Any]:
    with file_path.open("rb") as fp:
        files = {
            "file": (
                file_path.name,
                fp,
                content_type or "image/jpeg",
            )
        }
        response = client.request(
            "POST",
            "/api/file/upload/image",
            headers=get_auth_headers(token),
            files=files,
        )
    assert_http_ok(response)
    result = response.json()
    assert_result_code(result, 200)
    return result["data"]


# 预先上传后续搜索、编辑、合并都会依赖的基础图片。
@pytest.fixture(scope="session")
def prepared_uploads(client, token_map, image_paths, api_context):
    if api_context.get("prepared_uploads"):
        return api_context

    # 先准备后续搜索、编辑、合并都会依赖的基础图片 URL。
    yang_person = upload_file(client, token_map["yang"], image_paths["person_female"])
    yang_cloth_blue = upload_file(client, token_map["yang"], image_paths["cloth_blue"], content_type="image/png")
    yang_cloth_red = upload_file(client, token_map["yang"], image_paths["cloth_red"])
    xiao_person = upload_file(client, token_map["xiao"], image_paths["person_male"])

    api_context.update(
        {
            "yang_person_url": yang_person["url"],
            "yang_cloth_blue_url": yang_cloth_blue["url"],
            "yang_cloth_red_url": yang_cloth_red["url"],
            "xiao_person_url": xiao_person["url"],
            "prepared_uploads": True,
        }
    )
    return api_context


# 预先制造编辑和合并记录，供记录接口正向场景复用。
@pytest.fixture(scope="session")
def prepared_records(client, token_map, prepared_uploads, api_context):
    if api_context.get("prepared_records"):
        return api_context

    # 记录接口的正向校验依赖 edit/merge 先落库，这里集中做一次前置准备。
    edit_response = client.request(
        "POST",
        "/api/file/edit",
        headers=get_auth_headers(token_map["yang"]),
        json={
            "image": prepared_uploads["yang_person_url"],
            "instruction": "把上衣改成蓝色短袖",
        },
    )
    merge_response = client.request(
        "POST",
        "/api/file/merge",
        headers=get_auth_headers(token_map["yang"]),
            json={
            "image1": prepared_uploads["yang_person_url"],
            "image2": prepared_uploads["yang_cloth_blue_url"],
            "instruction": "把第二张衣服穿到第一张人物身上",
        },
    )
    edit_result = edit_response.json()
    merge_result = merge_response.json()
    if edit_result.get("code") != 200 or merge_result.get("code") != 200:
        pytest.skip("编辑/合并前置数据准备失败，跳过记录正向校验")

    api_context["prepared_records"] = True
    return api_context
