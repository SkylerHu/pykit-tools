#!/usr/bin/env python
# coding=utf-8
import time
import random
import logging
import typing
from functools import wraps, partial

from pykit_tools.utils import get_caller_location
from pykit_tools.log.adapter import timer_common_logger


error_logger = logging.getLogger("pykit_tools.error")


def handle_exception(
    func: typing.Optional[typing.Callable] = None,
    default: typing.Any = False,
    is_raise: bool = False,
    retry_for: typing.Union[typing.Type, tuple] = Exception,
    max_retries: int = 1,
    retry_delay: int = 0,
    retry_jitter: bool = True,
    log_args: bool = True,
) -> typing.Callable:
    """
    `装饰器` 用于捕获函数异常，并在出现异常的时候返回默认值

    Args:
        func: 函数
        default: 出现异常后的默认值
        is_raise: 是否抛出异常；设置True时，default参数无效且一定会抛出异常，主要用于重试场景最后依然抛出异常
        retry_for: 需要重试的异常类/异常元组，仅当异常匹配才进行重试
        max_retries: 最大重试次数
        retry_delay: 重试等待时间，默认值0（不推荐开启）
        retry_jitter: 重试抖动，用于将随机性引入指数退避延迟，以防止队列中的所有任务同时执行；
                若设置为true, 随机范围值在[0, retry_delay]之间，随机值为真实delay时间
        log_args: 异常时将参数输出到日志

    Returns:
        function

    """
    if not callable(func):
        return partial(
            handle_exception,
            default=default,
            is_raise=is_raise,
            retry_for=retry_for,
            max_retries=max_retries,
            retry_delay=retry_delay,
            retry_jitter=retry_jitter,
            log_args=log_args,
        )

    fn = typing.cast(typing.Callable, func)

    @wraps(fn)
    def _wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        result = None
        location = get_caller_location(fn)
        error: typing.Optional[Exception] = Exception('Function "{}" not executed'.format(location))

        count = 0
        while error is not None and count < max_retries:
            count += 1
            try:
                result = fn(*args, **kwargs)
                error = None
            except Exception as e:
                error = e
                _msg = "%s retry=%d %s" % (location, count, str(e))
                if log_args:
                    _msg = "%s\nargs: %s\nkwargs: %s" % (_msg, args, kwargs)
                error_logger.exception(_msg)
                if isinstance(e, retry_for):
                    # 可以记录重试
                    if retry_delay > 0:
                        # 延迟重试
                        delay = retry_delay
                        if retry_jitter:
                            delay = int(random.randint(0, 100) * delay / 100.0)
                        if delay > 0:
                            time.sleep(delay)
                else:
                    # 其他异常不重试
                    break

        if error is not None:
            if is_raise:
                raise error
            result = default() if callable(default) else default

        return result

    return _wrapper


def time_record(
    func: typing.Optional[typing.Callable] = None,
    format_key: typing.Optional[typing.Callable] = None,
    format_ret: typing.Optional[typing.Callable] = None,
) -> typing.Callable:
    """
    `装饰器` 函数耗时统计

    Args:
        func:
        format_key: 根据函数输入的参数，格式化日志记录的唯一标记key
        format_ret: 根据函数返回的结果，格式化日志记录的结果ret

    Returns:
        function

    """
    if not callable(func):
        return partial(time_record, format_key=format_key, format_ret=format_ret)

    fn = typing.cast(typing.Callable, func)

    @wraps(fn)
    def _wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        _start = time.monotonic()
        location = fn.__name__

        ret = None
        try:
            ret = fn(*args, **kwargs)
        finally:
            # 耗时
            _end = time.monotonic()
            cost = "%.3f" % ((_end - _start) * 1000)
            # 日志记录结果
            _ret = ret
            # 日志记录的唯一标识
            key = "-"
            if args and len(args) > 0:
                key = str(args[0])
            try:
                location = get_caller_location(fn)
                if callable(format_key):
                    key = format_key(*args, **kwargs)

                if callable(format_ret):
                    _ret = format_ret(ret)
            except Exception as e:
                error_logger.exception("%s %s\nargs=%s\nkwargs=%s", location, str(e), args, kwargs)

            timer_common_logger.info(dict(location=location, key=key, cost=cost, ret=_ret))

        # 返回正确结果
        return ret

    return _wrapper
