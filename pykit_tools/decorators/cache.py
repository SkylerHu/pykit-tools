#!/usr/bin/env python
# coding=utf-8
import json
import inspect
import logging
import typing
from functools import wraps, partial
from py_enum import ChoiceEnum

import pykit_tools
from pykit_tools import str_tool, utils


error_logger = logging.getLogger("pykit_tools.error")


_g_cache_client: typing.Any = None


def set_global_cache_client(client: typing.Any) -> None:
    """
    设置全局缓存client对象，用于存储缓存数据

    Args:
        client:

    Tip: 注意
        client必须有get(key)和set(key, value, timeout)方法，一般使用redis客户端

    """
    global _g_cache_client
    _g_cache_client = client


def get_global_cache_client() -> typing.Any:
    """
    获取全局缓存client对象

    Returns:
        cache client

    """
    return _g_cache_client


class CacheScene(ChoiceEnum):
    """
    `枚举` 缓存场景类型，定义值详见源码。

    应用于装饰器 [method_deco_cache](./#decorators.cache.method_deco_cache)
    """

    DEFAULT = ("default", "优先使用缓存，无缓存执行函数")
    DEGRADED = ("degraded", "优先执行函数，失败后降级使用缓存")  # 执行函数成功后，会更新缓存数据
    SKIP = ("skip", "忽略使用缓存，直接执行函数")  # 执行函数成功后，会更新缓存数据


def method_deco_cache(
    func: typing.Optional[typing.Callable] = None,
    key: typing.Optional[typing.Union[str, typing.Callable]] = None,
    timeout: int = 60,
    scene: str = CacheScene.DEFAULT,  # type: ignore
    cannot_cache: typing.Union[list, tuple] = (None, False),
    cache_client: typing.Any = None,
    cache_max_length: int = 33554432,
) -> typing.Callable:
    """
    `装饰器` 方法缓存结果, 只能缓存json序列化的数据类型

    Args:
        func: 可以在放在参数添加 scene=CacheScene.DEGRADED,可以强制进行刷新
        key: str, 缓存数据存储的key； 也可以传递func，根据参数动态构造
        timeout: 缓存超时时间，单位 秒(s)
        scene: 默认使用场景 [CacheScene](./#decorators.cache.CacheScene)
        cannot_cache: 元组，不允许缓存的数值
            传递False或者None表示缓存所有类型的结果数据，若是仅None不缓存一定要设置值为元组(None, )
            若是设置的函数，则根据返回数据作为输入参数、输出bool表示不允许缓存；
        cache_client: 缓存client对象

        cache_max_length: 序列化后缓存的字符串最大长度限制，
            此处设置最大缓存 32M = 32 * 1024 * 1024
            若是redis, A String value can be at max 512 Megabytes in length.

    Returns:
        function

    """

    if not callable(func):
        return partial(
            method_deco_cache,
            key=key,
            timeout=timeout,
            scene=scene,
            cannot_cache=cannot_cache,
            cache_client=cache_client,
            cache_max_length=cache_max_length,
        )

    fn = typing.cast(typing.Callable, func)

    _redis_conf = pykit_tools.settings.APP_CACHE_REDIS
    if _redis_conf:
        import redis  # type: ignore

        __pool = redis.ConnectionPool(encoding="utf-8", decode_responses=True, **_redis_conf)
        _inner_client = redis.StrictRedis(connection_pool=__pool)
    else:
        _inner_client = utils.CacheMap()

    def __get_cache_client() -> typing.Any:
        if cache_client:
            _client = cache_client
        elif _g_cache_client:
            _client = _g_cache_client
        else:
            _client = _inner_client
        return _client

    def __load_cache_data(_client: typing.Any, _key: str) -> tuple[bool, typing.Any]:
        has_cache, data = False, None
        try:
            value = _client.get(_key)
            if value is not None:
                data = json.loads(value)
                has_cache = True
        except Exception:
            error_logger.exception("load cache_data error key={}".format(_key))
        return has_cache, data

    def __allow_value_cache(value: typing.Any) -> bool:
        if not cannot_cache:
            # 没设置任何不允许缓存
            return True
        elif callable(cannot_cache):
            v = cannot_cache(value)
            return not v
        elif isinstance(cannot_cache, (tuple, list)):
            # 不在 不允许缓存列表中
            return value not in cannot_cache
        else:
            raise TypeError("The 'cannot_cache' value format does not meet the requirements")

    @wraps(fn)
    def _wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        # 内置参数，force缓存
        _scene = kwargs.pop("scene", scene)
        if _scene not in CacheScene:  # type: ignore
            raise TypeError("scene={} not supported".format(scene))

        _client = __get_cache_client()
        if key:
            _key = key(*args, **kwargs) if callable(key) else key
        else:
            location = utils.get_caller_location(fn)
            _key = "method:{}:{}".format(fn.__name__, str_tool.compute_md5(location, *args, **kwargs))
        # else:
        #     _key = "method:{}".format(str_tool.compute_md5(*args, **kwargs))

        if _scene in (CacheScene.DEFAULT,):
            # 直接从缓存里获取结果
            has_cache, data = __load_cache_data(_client, _key)
            if has_cache and __allow_value_cache(data):
                # 直接返回缓存结果
                return data

        try:
            ret = fn(*args, **kwargs)
        except Exception as e:
            if _scene == CacheScene.DEGRADED:
                # 降级处理
                has_cache, data = __load_cache_data(_client, _key)
                if has_cache and __allow_value_cache(data):
                    return data
            raise e

        if not __allow_value_cache(ret):
            # 不需要缓存，直接返回
            return ret

        # 处理缓存，不影响函数结果返回
        try:
            _cache_str = json.dumps(ret, separators=(",", ":"))
            if len(_cache_str) > cache_max_length:
                error_logger.error("Cache too long, key={} limit is {}".format(_key, cache_max_length))
            else:
                _client.set(_key, _cache_str, timeout)
        except Exception:
            error_logger.exception("set cache_data error key={} ret={}".format(_key, ret))

        return ret

    return _wrapper


def singleton_refresh_regular(cls: typing.Optional[typing.Type] = None, timeout: int = 5) -> typing.Callable:
    """
    `装饰器` 带定时刷新的单例装饰器

    应用场景：例如某对象实例化后带有session相关信息，有一定有效期的情况可以在类上加上该装饰器

    Args:
        cls: 类
        timeout: 单例使用超时时间，单位秒(s)

    Returns:
        function

    示例：
    ```python
    @singleton_refresh_regular
    class YouClass(Singleton):
        pass
    ```
    """
    if cls is None:
        return partial(singleton_refresh_regular, timeout=timeout)

    if not inspect.isclass(cls):
        raise TypeError("this decorator can only be applied to classes, not {}".format(type(cls)))

    _cls = typing.cast(typing.Type, cls)

    cache_map = utils.CacheMap()

    @wraps(_cls)
    def _wrapper(*args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        _key = str_tool.compute_md5(utils.get_caller_location(_cls), *args, **kwargs)
        ins = cache_map.get(_key)
        if ins is None:
            ins = _cls(*args, **kwargs)
            cache_map.set(_key, ins, timeout=timeout)
        return ins

    return _wrapper
