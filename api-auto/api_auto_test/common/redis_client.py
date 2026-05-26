from __future__ import annotations

from typing import Any

import redis

from common.logger import get_logger


class RedisClient:
    # 初始化 Redis 客户端连接参数并创建底层连接对象。
    def __init__(
        self,
        *,
        host: str,
        port: int,
        db: int = 0,
        password: str | None = None,
        socket_timeout: int = 5,
    ) -> None:
        self.logger = get_logger(self.__class__.__name__)
        self.client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            socket_timeout=socket_timeout,
            decode_responses=True,
        )

    # 读取指定 key 对应的字符串值。
    def get(self, key: str) -> str | None:
        self.logger.info("redis get %s", key)
        return self.client.get(key)

    # 删除指定 key，用于清理验证码或临时状态。
    def delete(self, key: str) -> int:
        self.logger.info("redis delete %s", key)
        return int(self.client.delete(key))

    # 按项目约定的 key 规则读取邮箱验证码。
    def get_verification_code(self, email: str) -> str | None:
        return self.get(f"verification:code:{email}")

    # 检查 Redis 当前是否可连通。
    def ping(self) -> bool:
        return bool(self.client.ping())

    # 关闭当前 Redis 连接，释放资源。
    def close(self) -> None:
        self.client.close()
