from __future__ import annotations

from pathlib import Path
from typing import Any
import unicodedata

from jsonschema import validate

from common.yaml_utils import load_yaml


# 断言 HTTP 层状态码符合统一预期。
def assert_http_ok(response) -> None:
    assert response.status_code == 200, f"http status={response.status_code}, body={response.text}"


# 断言业务返回体中的 code 字段符合预期。
def assert_result_code(result: dict[str, Any], expected_code: int) -> None:
    assert result["code"] == expected_code, f"expected code={expected_code}, actual={result}"


# 断言业务返回体中的 message 与预期完全一致。
def assert_message(result: dict[str, Any], expected_message: str | None = None) -> None:
    if expected_message is not None:
        actual_message = _normalize_text(result["message"])
        normalized_expected = _normalize_text(expected_message)
        assert actual_message == normalized_expected, f"expected message={expected_message}, actual={result}"


# 断言目标字典包含当前场景要求的关键字段。
def assert_has_keys(target: dict[str, Any], expected_keys: list[str]) -> None:
    missing = [key for key in expected_keys if key not in target]
    assert not missing, f"missing keys={missing}, target={target}"  #断言 missing 应该为空 ,如果不为空，就报错


# 按 schema 校验返回结构是否合法，支持 YAML 和 JSON 两种格式。
def assert_schema(result: dict[str, Any], schema_path: str | Path) -> None:
    schema = load_yaml(schema_path) if str(schema_path).endswith((".yaml", ".yml")) else _load_json(schema_path)
    validate(instance=result, schema=schema)


# 从本地 JSON 文件中读取 schema 定义。
def _load_json(path: str | Path) -> dict[str, Any]:
    import json

    with Path(path).open("r", encoding="utf-8") as file:
        return json.load(file)


# 统一做文本规范化，避免兼容字符导致断言误差。
def _normalize_text(text: str) -> str:
    return unicodedata.normalize("NFKC", text)
