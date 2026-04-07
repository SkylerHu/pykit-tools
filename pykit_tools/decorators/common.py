#!/usr/bin/env python
# coding=utf-8
import time
import random
import logging
import typing
from functools import wraps, partial

from pykit_tools.utils import get_caller_location


def handle_exception(
    func: typing.Optional[typing.Callable] = None,
    default: typing.Any = False,
    is_raise: bool = False,
    retry_for: typing.Union[typing.Type, typing.Tuple] = Exception,
    max_retries: int = 1,
    retry_delay: int = 0,
    retry_jitter: bool = True,
    log_args: bool = True,
    logger_name: str = "pykit_tools.error",
    logger_level: int = logging.ERROR,
    logger_pre_level: int = logging.WARNING,
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
        logger_name: 日志名称，仅记录异常时使用
        logger_level: 异常时设置日志的级别
        logger_pre_level: 重试最后一次之前的日志级别，避免多次重试会有多次错误输出

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
            logger_name=logger_name,
            logger_level=logger_level,
            logger_pre_level=logger_pre_level,
        )

    fn = typing.cast(typing.Callable, func)

    @wraps(fn)
    def _wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        result = None
        location = get_caller_location(fn)
        error: typing.Optional[Exception] = Exception(f'Function "{location}" not executed')

        count = 0
        while error is not None and count < max_retries:
            count += 1
            try:
                result = fn(*args, **kwargs)
                error = None
            except Exception as e:
                error = e
                _level = logger_level if count >= max_retries else logger_pre_level
                if log_args:
                    logging.getLogger(logger_name).log(
                        _level,
                        "%s retry=%d %s\n\targs: %s\n\tkwargs: %s",
                        location,
                        count,
                        str(e),
                        args,
                        kwargs,
                        exc_info=True,
                    )
                else:
                    logging.getLogger(logger_name).log(
                        _level,
                        "%s retry=%d %s",
                        location,
                        count,
                        str(e),
                        exc_info=True,
                    )
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
    logger_name: str = "pykit_tools.error",
    logger_level: int = logging.ERROR,
) -> typing.Callable:
    """
    `装饰器` 函数耗时统计

    Args:
        func:
        format_key: 根据函数输入的参数，格式化日志记录的唯一标记key
        format_ret: 根据函数返回的结果，格式化日志记录的结果ret
        logger_name: 日志名称，仅记录异常时使用
        logger_level: 异常时设置日志的级别

    Returns:
        function

    """
    if not callable(func):
        return partial(
            time_record,
            format_key=format_key,
            format_ret=format_ret,
            logger_name=logger_name,
            logger_level=logger_level,
        )

    fn = typing.cast(typing.Callable, func)

    logger = logging.getLogger(logger_name)

    @wraps(fn)
    def _wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        _start = time.monotonic()
        location = fn.__name__
        key = "-"
        try:
            if args:
                key = str(args[0])
            location = get_caller_location(fn)
            if callable(format_key):
                key = format_key(*args, **kwargs)
        except Exception:
            pass

        ret = None
        try:
            ret = fn(*args, **kwargs)
        except Exception as exc:
            cost = "%.3f" % ((time.monotonic() - _start) * 1000)
            logger.log(logger_level, "%s %s %s %s", location, key, cost, exc, exc_info=True)
            raise
        else:
            cost = "%.3f" % ((time.monotonic() - _start) * 1000)
            _ret = ret
            try:
                if callable(format_ret):
                    _ret = format_ret(ret)
                logger.info("%s %s %s %s", location, key, cost, _ret)
            except Exception as e:
                logger.log(logger_level, "%s %s %s %s", location, key, cost, e, exc_info=True)

        return ret

    return _wrapper
