from __future__ import annotations

from pathlib import Path
from typing import Any

from common.yaml_utils import load_yaml

# 得到 D:\codes\ChangeClothes\api_auto_test
PROJECT_ROOT = Path(__file__).resolve().parents[1]

# 得到 D:\codes\ChangeClothes
WORKSPACE_ROOT = PROJECT_ROOT.parent


'''
目的是把：
路径
环境配置
账号配置
都集中到一个对象里
'''
class Settings:
    # 初始化项目配置对象并加载环境配置和账号配置。
    def __init__(self) -> None:
        self.project_root = PROJECT_ROOT
        self.workspace_root = WORKSPACE_ROOT
        self.env: dict[str, Any] = load_yaml(PROJECT_ROOT / "config" / "env.yaml")
        self.accounts: dict[str, Any] = load_yaml(PROJECT_ROOT / "config" / "accounts.yaml")

    # 返回当前测试环境的接口基础地址。
    @property
    def base_url(self) -> str:
        return self.env["base_url"]

    # 返回统一请求超时时间。
    @property
    def timeout(self) -> int:
        return int(self.env.get("timeout", 30))

    @property
    def merge_timeout(self) -> int:
        return int(self.env.get("merge_timeout", self.timeout))

    # 返回测试素材路径配置。
    @property
    def paths(self) -> dict[str, str]:
        paths = self.env.get("paths", {})
        resolved_paths = {}
        for key, value in paths.items():
            path = Path(value)
            resolved_paths[key] = str(path if path.is_absolute() else self.project_root / path)
        return resolved_paths

    # 返回 Redis 相关配置。
    @property
    def redis(self) -> dict[str, Any]:
        return self.env.get("redis", {})


settings = Settings()
