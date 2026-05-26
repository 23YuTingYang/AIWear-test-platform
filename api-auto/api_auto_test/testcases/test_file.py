from __future__ import annotations

from pathlib import Path

import pytest

from common.assertion import assert_has_keys, assert_http_ok, assert_message, assert_result_code, assert_schema
from common.yaml_utils import load_yaml
from config.settings import settings
from conftest import get_auth_headers

FILE_DATA = load_yaml(settings.project_root / "data" / "file.yaml")
COMMON_SCHEMA = settings.project_root / "schema" / "common_result.json"
FILE_SCHEMA = settings.project_root / "schema" / "file_schema.json"


# 根据 YAML 场景生成 pytest 标记
def _marks(case):
    marks = [getattr(pytest.mark, marker) for marker in case.get("markers", [])]
    return marks


# 根据用例里的 auth 标识取出对应账号的 token。
def _token_for_case(case, token_map):
    #先看当前 case 有没有 auth 有的话，取它的值 没有的话，默认用 "yang"
    return token_map.get(case.get("auth", "yang"))


# 按场景生成当前请求要使用的 Authorization 请求头。
def _headers_for_case(case, token_map):

    # 优先按用例显式指定的异常鉴权模式构造请求头，否则按账号取正常 token。
    mode = case.get("auth_mode")
    if mode:
        return get_auth_headers(mode=mode)
    return get_auth_headers(_token_for_case(case, token_map))


# 解析当前用例实际应该使用的文件路径，兼容真实素材和运行时临时文件。
def _resolve_file(file_key, image_paths, runtime_files) -> Path:
    if file_key in runtime_files:
        return runtime_files[file_key]
    return image_paths[file_key]


@pytest.mark.order(3)
class TestUploadImage:
    @pytest.mark.parametrize(
        "case",
        [pytest.param(case, id=case["id"], marks=_marks(case)) for case in FILE_DATA["upload_image"]],
    )
    # 执行上传图片接口的正反向场景校验。
    def test_upload_image(self, client, case, token_map, image_paths, runtime_files):
        headers = _headers_for_case(case, token_map)
        if case.get("repeat_upload"):
            # 重复上传场景先做一次同图上传，再执行当前断言请求。
            file_path = _resolve_file(case["file_key"], image_paths, runtime_files)
            #重复上传”场景，先上传一次
            with file_path.open("rb") as fp:
                client.request(
                    "POST",
                    "/api/file/upload/image",
                    headers=headers,
                    files={"file": (file_path.name, fp, case.get("content_type", "image/jpeg"))},
                )

        files = None
        #文件不为空的 才构造文件参数
        if case.get("send_file", True):
            #根据 file_key 找真实文件
            file_path = _resolve_file(case["file_key"], image_paths, runtime_files)
            #打开文件句柄
            fp = file_path.open("rb")
            #构造成 requests 上传文件所需的 files 格式
            files = {"file": (file_path.name, fp, case.get("content_type", "image/jpeg"))}
        try:
            response = client.request("POST", "/api/file/upload/image", headers=headers, files=files)
        finally:
            if files:
                files["file"][1].close()

        assert_http_ok(response)
        result = response.json()
        assert_schema(result, COMMON_SCHEMA)
        assert_schema(result, FILE_SCHEMA)
        assert_result_code(result, case["expect_code"])
        assert_message(result, case.get("expect_message"))
        if case["expect_code"] == 200:
            assert_has_keys(result["data"], case["expect_keys"])


@pytest.mark.order(4)
class TestMyImages:
    @pytest.mark.parametrize(
        "case",
        [pytest.param(case, id=case["id"], marks=_marks(case)) for case in FILE_DATA["my_images"]],
    )
    # 执行我的图片列表接口，并校验用户隔离与空列表场景。
    def test_my_images(self, client, case, token_map, prepared_uploads):
        # 这里显式依赖 prepared_uploads，保证图片列表、隔离校验基于真实已上传数据。
        headers = _headers_for_case(case, token_map)
        response = client.request("GET", "/api/file/my-images", headers=headers)
        assert_http_ok(response)
        result = response.json()
        assert_schema(result, COMMON_SCHEMA)
        assert_schema(result, FILE_SCHEMA)
        assert_result_code(result, case["expect_code"])
        assert_message(result, case.get("expect_message"))
        #只有业务成功时，才继续检查 data。
        if result["code"] == 200:
            data = result["data"]
            #新用户场景
            if case.get("expect_empty"):
                assert data == []
            elif case["auth"] == "yang" and data:
                #prepared_uploads 里缓存的是之前真实上传成功后的 URL
                assert prepared_uploads["yang_person_url"] in [item.get("ossUrl") for item in data]
                assert prepared_uploads["xiao_person_url"] not in [item.get("ossUrl") for item in data]
            elif case["auth"] == "xiao" and data:
                assert prepared_uploads["xiao_person_url"] in [item.get("ossUrl") for item in data]
                assert prepared_uploads["yang_person_url"] not in [item.get("ossUrl") for item in data]


@pytest.mark.order(5)
class TestSearch:
    @pytest.mark.parametrize(
        "case",
        [pytest.param(case, id=case["id"], marks=_marks(case)) for case in FILE_DATA["search"]],
    )
    # 执行图片搜索接口，覆盖文搜图、图搜图和鉴权异常场景。
    def test_search(self, client, case, token_map, image_paths, runtime_files, prepared_uploads):
        headers = _headers_for_case(case, token_map)
        data = None  #文本搜索
        files = None  #图搜图
        mode = case["mode"]
        if mode == "query":
            data = {"query": case["query"]}
        elif mode == "file":
            file_path = _resolve_file(case["file_key"], image_paths, runtime_files)
            fp = file_path.open("rb")
            files = {"file": (file_path.name, fp, "image/jpeg")}
        try:
            response = client.request("POST", "/api/file/search", headers=headers, data=data, files=files)
        finally:
            if files:
                files["file"][1].close()

        assert_http_ok(response)
        result = response.json()
        assert_schema(result, COMMON_SCHEMA)
        assert_schema(result, FILE_SCHEMA)
        assert_result_code(result, case["expect_code"])
        assert_message(result, case.get("expect_message"))
        #只有业务成功时，才继续检查 data。
        if result["code"] == 200:
            data_list = result["data"]
            if case.get("expect_empty"):
                assert data_list == []
            if case.get("expect_not_contains_context_key"):
                # 用户隔离场景下，结果里不应出现上下文中另一位用户上传的目标图片。
                target = prepared_uploads[case["expect_not_contains_context_key"]]
                assert target not in [item.get("filePath") for item in data_list]


@pytest.mark.order(6)
class TestEdit:
    @pytest.mark.parametrize(
        "case",
        [pytest.param(case, id=case["id"], marks=_marks(case)) for case in FILE_DATA["edit"]],
    )
    # 执行图片编辑接口，并校验参数、权限和成功返回结果。
    def test_edit(self, client, case, token_map, prepared_uploads):
        headers = _headers_for_case(case, token_map)
        payload = {}
        if not case.get("omit_image"):
            if "image" in case:
                payload["image"] = case["image"]
            else:
                payload["image"] = prepared_uploads.get(case.get("image_ref"))
        if not case.get("omit_instruction"):
            payload["instruction"] = case.get("instruction")
        response = client.request("POST", "/api/file/edit", headers=headers, json=payload)
        assert_http_ok(response)
        result = response.json()
        assert_schema(result, COMMON_SCHEMA)
        assert_schema(result, FILE_SCHEMA)
        assert_result_code(result, case["expect_code"])
        assert_message(result, case.get("expect_message"))
        #只有业务成功时，才继续检查返回 data
        if result["code"] == 200:
            assert_has_keys(result["data"], case["expect_keys"])


@pytest.mark.order(7)
class TestMerge:
    @pytest.mark.parametrize(
        "case",
        [pytest.param(case, id=case["id"], marks=_marks(case)) for case in FILE_DATA["merge"]],
    )
    # 执行图片合并接口，并校验参数、权限和成功返回结果。
    def test_merge(self, client, case, token_map, prepared_uploads):
        headers = _headers_for_case(case, token_map)
        payload = {}
        if not case.get("omit_image1"):
            if "image1" in case:
                payload["image1"] = case["image1"]
            else:
                payload["image1"] = prepared_uploads.get(case.get("image1_ref"))
        if not case.get("omit_image2"):
            if "image2" in case:
                payload["image2"] = case["image2"]
            else:
                payload["image2"] = prepared_uploads.get(case.get("image2_ref"))
        if not case.get("omit_instruction"):
            payload["instruction"] = case.get("instruction")
        response = client.request("POST", "/api/file/merge", headers=headers, json=payload, timeout=settings.merge_timeout)
        assert_http_ok(response)
        result = response.json()
        assert_schema(result, COMMON_SCHEMA)
        assert_schema(result, FILE_SCHEMA)
        assert_result_code(result, case["expect_code"])
        assert_message(result, case.get("expect_message"))
        #只有业务成功时，才继续检查返回 data
        if result["code"] == 200:
            assert_has_keys(result["data"], case["expect_keys"])
