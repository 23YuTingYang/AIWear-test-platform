from __future__ import annotations

import pytest

from common.assertion import assert_has_keys, assert_http_ok, assert_message, assert_result_code, assert_schema
from common.yaml_utils import load_yaml
from config.settings import settings
from conftest import get_auth_headers


USER_DATA = load_yaml(settings.project_root / "data" / "user.yaml")
COMMON_SCHEMA = settings.project_root / "schema" / "common_result.json"
USER_SCHEMA = settings.project_root / "schema" / "user_schema.json"


# 根据 YAML 场景生成 pytest 标记
def _marks(case):
    marks = [getattr(pytest.mark, marker) for marker in case.get("markers", [])]
    return marks


@pytest.mark.order(1)
class TestSendCode:
    @pytest.mark.parametrize(
        "case",
        [pytest.param(case, id=case["id"], marks=_marks(case)) for case in USER_DATA["send_code"]],
    )
    # 执行发送验证码接口，并校验邮箱参数和重复发送场景。
    def test_send_code(self, client, case, redis_client):
        if case["id"] == "send_code_success":
            # 先清理旧验证码，避免“验证码仍有效”影响首次发送成功场景。
            email = case["payload"]["email"]
            redis_client.delete(f"verification:code:{email}")

        response = client.request("POST", "/api/user/send-code", json=case.get("payload", {}))
        assert_http_ok(response)
        result = response.json()
        assert_schema(result, COMMON_SCHEMA)
        assert_schema(result, USER_SCHEMA)
        assert_result_code(result, case["expect_code"])
        assert_message(result, case.get("expect_message"))
        #如果成功，就继续检查 data 里关键字段是否都在。
        if case["expect_code"] == 200:
            assert_has_keys(result["data"], case["expect_keys"])


@pytest.mark.order(2)
class TestAuth:
    @pytest.mark.parametrize(
        "case",
        [pytest.param(case, id=case["id"], marks=_marks(case)) for case in USER_DATA["auth"]],
    )
    # 执行认证接口，并覆盖账号密码、邮箱验证码和新账号自动注册场景。
    def test_auth(self, client, case, accounts, redis_client, new_user_credentials):
        #如果是账号密码登录
        if case.get("login_mode") == "password":
            account_ref = accounts[case["account_ref"]]
            payload = {"account": account_ref["account"], "password": account_ref["password"]}
        else:
            #邮箱验证码登录 错误验证码 空验证码 新用户自动注册等
            payload = dict(case.get("payload", {}))

        #新用户自动注册
        if payload.get("account") == "__RANDOM_NEW_ACCOUNT__":
            payload["account"] = new_user_credentials["account"]
            payload["password"] = new_user_credentials["password"]

        #邮箱验证码登录成功场景 验证码要到redis中拿
        if case["id"] == "auth_email_success_manual":
            # 邮箱验证码成功场景不手工抄码，直接从 Redis 读取 Java 服务刚写入的验证码。
            verification_code = redis_client.get_verification_code(payload["account"])
            assert verification_code, f"Redis 中未读取到验证码: {payload['account']}"
            payload["verificationCode"] = verification_code

        response = client.request("POST", "/api/user/auth", json=payload)
        assert_http_ok(response)
        result = response.json()
        assert_schema(result, COMMON_SCHEMA)
        assert_schema(result, USER_SCHEMA)
        assert_result_code(result, case["expect_code"])
        assert_message(result, case.get("expect_message"))
        if case["expect_code"] == 200:
            assert_has_keys(result["data"], case["expect_keys"])

'''
从 user.yaml 取一条 logout 场景数据
1.读取 header_mode
2.如果是 valid / repeat_logout / revoked_token，就先登录拿真实 token
3.如果是 repeat_logout / revoked_token，再先登出一次制造失效状态
4.如果是其它异常 header 场景，就直接调用 get_auth_headers(mode=...) 构造请求头
5.调 /api/user/logout
6.最后统一校验 HTTP、schema、业务码、message，以及必要时的 data
'''
@pytest.mark.order(9)
class TestLogout:
    @pytest.mark.parametrize(
        "case",
        [pytest.param(case, id=case["id"], marks=_marks(case)) for case in USER_DATA["logout"]],
    )
    # 执行退出登录接口，并校验重复登出、失效 token 和异常请求头场景。
    def test_logout(self, client, case, accounts):
        # from conftest import get_auth_headers

        # if case.get("skip"):
        #     pytest.skip(case["skip_reason"])

        mode = case["header_mode"]
        if mode == "repeat_logout":
            # 重复登出场景需要先完成一次成功登出，再复用同一个 token 发第二次请求。
            #登录
            login_resp = client.request(
                "POST",
                "/api/user/auth",
                json={"account": accounts["yang"]["account"], "password": accounts["yang"]["password"]},
            )
            #取出 token
            token = login_resp.json()["data"]["token"]
            #第一次登出
            first_resp = client.request("POST", "/api/user/logout", headers=get_auth_headers(token))
            assert_http_ok(first_resp)
            assert_result_code(first_resp.json(), 200)
            #第二次登出
            response = client.request("POST", "/api/user/logout", headers=get_auth_headers(token))
        elif mode == "valid":
            # 先登录
            login_resp = client.request(
                "POST",
                "/api/user/auth",
                json={"account": accounts["yang"]["account"], "password": accounts["yang"]["password"]},
            )
            token = login_resp.json()["data"]["token"]
            #登出
            response = client.request("POST", "/api/user/logout", headers=get_auth_headers(token))
        elif mode == "revoked_token":
            # 先登录再主动登出一次，构造“已失效旧 token”而不是伪造字符串。
            login_resp = client.request(
                "POST",
                "/api/user/auth",
                json={"account": accounts["yang"]["account"], "password": accounts["yang"]["password"]},
            )
            token = login_resp.json()["data"]["token"]
            #再登出一次使它失效
            first_resp = client.request("POST", "/api/user/logout", headers=get_auth_headers(token))
            assert_http_ok(first_resp)
            assert_result_code(first_resp.json(), 200)
            #再拿这个失效 token 去调 logout
            response = client.request("POST", "/api/user/logout", headers=get_auth_headers(token))
        else:
            # 其它异常 header 模式，就直接用 get_auth_headers(mode=...) 构造请求头。
            headers = get_auth_headers(mode=mode)
            response = client.request("POST", "/api/user/logout", headers=headers)

        assert_http_ok(response)
        result = response.json()
        assert_schema(result, COMMON_SCHEMA)
        assert_schema(result, USER_SCHEMA)
        assert_result_code(result, case["expect_code"])
        assert_message(result, case.get("expect_message"))
        if "expected_data" in case:
            assert result["data"] == case["expected_data"]
