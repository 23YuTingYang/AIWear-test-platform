from __future__ import annotations

import logging
from datetime import datetime
from pathlib import Path


_LOGGERS: dict[str, logging.Logger] = {}


# 为指定日志级别创建按时间切分的文件处理器。
def _build_file_handler(log_dir: Path, level_name: str) -> logging.Handler:
    log_dir.mkdir(parents=True, exist_ok=True)
    file_name = f"{level_name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"
    handler = logging.FileHandler(log_dir / file_name, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(funcName)s | line=%(lineno)d | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    return handler


# 创建并缓存项目统一使用的日志对象。
def get_logger(name: str, root_dir: str | Path | None = None) -> logging.Logger:
    if name in _LOGGERS:
        return _LOGGERS[name]

    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False

    if not logger.handlers:
        project_root = Path(root_dir) if root_dir else Path(__file__).resolve().parents[1]
        logs_root = project_root / "logs"

        #把日志输出到控制台
        # console_handler = logging.StreamHandler()
        # console_handler.setLevel(logging.INFO)
        # console_handler.setFormatter(
        #     logging.Formatter(
        #         "%(asctime)s | %(levelname)s | %(name)s | %(funcName)s | line=%(lineno)d | %(message)s",
        #         "%H:%M:%S",
        #     )
        # )

        info_handler = _build_file_handler(logs_root / "info", "info")
        info_handler.setLevel(logging.INFO)

        error_handler = _build_file_handler(logs_root / "error", "error")
        error_handler.setLevel(logging.ERROR)

        # logger.addHandler(console_handler)
        logger.addHandler(info_handler)
        logger.addHandler(error_handler)

    _LOGGERS[name] = logger
    return logger
