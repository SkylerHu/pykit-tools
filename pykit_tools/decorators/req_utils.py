#!/usr/bin/env python
# coding=utf-8
import typing
import time
import logging
import json as json_tool

from functools import wraps, partial


def requests_logger(
    func: typing.Optional[typing.Callable] = None,
    default_ua: str = "",
    logger_name: str = "pykit_tools.requests",
) -> typing.Callable:
    """
    `装饰器` 应用于对 requests 库的请求进行日志记录.

    扩展 requests 请求函数可传递的参数：

    - log_request: 是否记录请求的参数，默认True
    - log_response: 是否记录响应内容，默认True
    - raise_for: 需要抛出的异常类型/异常元组，仅当异常匹配才抛出异常，默认None不抛出异常

    Args:
        func:
        default_ua: 默认的 User-Agent
        logger_name: 日志名称，仅记录异常时使用

    Returns:
        function:

    """
    if not callable(func):
        return partial(requests_logger, default_ua=default_ua, logger_name=logger_name)

    fn = typing.cast(typing.Callable, func)
    logger = logging.getLogger(logger_name)

    @wraps(fn)
    def _wrapper(
        method: str,
        url: str,
        log_request: bool = True,
        log_response: bool = True,
        raise_for: typing.Optional[typing.Union[typing.Type, typing.Tuple]] = None,
        timeout: int = 10,
        headers: typing.Optional[typing.Dict] = None,
        **kwargs: typing.Any,
    ) -> typing.Any:

        if default_ua:
            # 设置默认的 User-Agent
            headers = headers or {}
            headers["User-Agent"] = default_ua

        req_msg = ""
        if log_request:
            req_msg = f"timeout={timeout} headers: {headers}"
            if kwargs.get("params") is not None:
                req_msg = f"{req_msg}\n\tparams: {kwargs.get('params')}"
            if kwargs.get("data") is not None:
                req_msg = f"{req_msg}\n\tdata: {kwargs.get('data')}"
            if kwargs.get("json") is not None:
                json_str = json_tool.dumps(kwargs.get("json"), separators=(",", ":"), ensure_ascii=False)
                req_msg = f"{req_msg}\n\tjson: {json_str}"
            if kwargs:
                req_msg = f"{req_msg}\n\tkwargs: {kwargs}"

        response = None
        err = ""
        code = 0
        length = 0
        resp_msg = ""
        _start = time.monotonic()
        try:
            response = fn(method, url, headers=headers, timeout=timeout, **kwargs)
            code = response.status_code
            length = len(response.content)
            if log_response:
                try:
                    resp_msg = response.text
                except Exception as _e:
                    resp_msg = f"parse response.text error]: {_e}"
        except Exception as e:
            err = str(e)
            if raise_for and isinstance(e, raise_for):
                raise
        finally:
            # 耗时
            _end = time.monotonic()
            cost = (_end - _start) * 1000
            # 日志内容
            msg = f"{method.upper()} {url} {code} {length} {cost:.3f} {err or '-'}"
            if req_msg:
                msg = f"{msg}\n\trequest: {req_msg}"
            if resp_msg:
                msg = f"{msg}\n\tresponse: {resp_msg}"

            if err:
                logger.exception(msg)
            else:
                logger.info(msg)

        # 返回结果
        return response

    return _wrapper
