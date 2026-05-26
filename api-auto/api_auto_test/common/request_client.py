from __future__ import annotations

from typing import Any

import requests

from common.logger import get_logger


class RequestClient:
    # 初始化统一请求客户端，复用 Session 和日志能力。
    def __init__(self, base_url: str, timeout: int = 30) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.trust_env = False
        self.logger = get_logger(self.__class__.__name__)

    # 发送一次 HTTP 请求并记录请求/响应日志。
    def request(
        self,
        method: str,
        path: str,
        *,
        headers: dict[str, str] | None = None,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
        files: Any = None,
        data: dict[str, Any] | None = None,
        expected_http_status: int = 200,
        timeout: int | None = None,
    ) -> requests.Response:
        url = f"{self.base_url}{path}"
        self.logger.info("request %s %s", method.upper(), url)
        response = self.session.request(
            method=method.upper(),
            url=url,
            headers=headers,
            params=params,
            json=json,
            files=files,
            data=data,
            timeout=timeout or self.timeout,
        )
        self.logger.info("response %s %s", response.status_code, url)
        if response.status_code != expected_http_status:
            self.logger.error("unexpected http status: %s, body: %s", response.status_code, response.text)
        return response
