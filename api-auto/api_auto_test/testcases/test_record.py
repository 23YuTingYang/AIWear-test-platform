from __future__ import annotations

import pytest

from common.assertion import assert_http_ok, assert_message, assert_result_code, assert_schema
from common.yaml_utils import load_yaml
from config.settings import settings
from conftest import get_auth_headers

RECORD_DATA = load_yaml(settings.project_root / "data" / "record.yaml")
COMMON_SCHEMA = settings.project_root / "schema" / "common_result.json"
RECORD_SCHEMA = settings.project_root / "schema" / "record_schema.json"


# 按场景生成记录接口请求头，兼容正常和异常鉴权模式。
def _headers_for_case(case, token_map):

    mode = case.get("auth_mode")
    #如果 case 指定了异常鉴权模式  生成异常请求头
    if mode:
        return get_auth_headers(mode=mode)

    # 取指定用户的真实 token 生成正常请求头
    return get_auth_headers(token_map[case["auth"]])


@pytest.mark.order(8)
class TestRecord:
    @pytest.mark.parametrize(
        "case",
        [pytest.param(case, id=case["id"]) for case in RECORD_DATA["my_record"]],
    )
    # 执行我的记录接口，并校验筛选条件和用户隔离行为。
    def test_my_record(self, client, case, token_map, prepared_uploads, request):
        if case["expect_code"] == 200 and case.get("auth") == "yang":
            # Yang 的正向记录查询依赖前面先产生 edit/merge 记录，这里按需触发前置。
            #在方法执行过程中 需要的时候，主动去执行 prepared_records 这个 fixture 并确保它完成前置记录准备
            request.getfixturevalue("prepared_records")

        headers = _headers_for_case(case, token_map)
        response = client.request(
            "GET",
            "/api/record/my",
            headers=headers,
            params=case.get("params"),
        )
        assert_http_ok(response)
        result = response.json()
        assert_schema(result, COMMON_SCHEMA)
        assert_schema(result, RECORD_SCHEMA)
        assert_result_code(result, case["expect_code"])
        assert_message(result, case.get("expect_message"))
        #只有在成功场景下，才去验证返回记录列表是不是符合业务预期
        if result["code"] == 200:
            data = result["data"]
            #record_unknown_action
            if case.get("expect_empty"):
                assert data == []
            if case.get("expect_action"):
                assert all(item.get("action") == case["expect_action"] for item in data)
            #用户隔离校验 到xiao的这一条记录的时候 才会执行到这里
            if case.get("expect_not_contains_context_key"):
                target = prepared_uploads[case["expect_not_contains_context_key"]]
                assert all(target not in str(item) for item in data)



