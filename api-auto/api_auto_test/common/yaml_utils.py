from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


# 从 YAML 文件中读取测试数据或配置。
def load_yaml(path: str | Path) -> Any:
    with Path(path).open("r", encoding="utf-8") as file:
        return yaml.safe_load(file)


# 把数据写回 YAML 文件，供配置或数据维护使用。
def dump_yaml(path: str | Path, data: Any) -> None:
    with Path(path).open("w", encoding="utf-8") as file:
        yaml.safe_dump(data, file, allow_unicode=True, sort_keys=False)
