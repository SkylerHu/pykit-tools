#!/usr/bin/env python
# coding=utf-8
import time
import importlib
import typing


def find_method_by_str(method_path: str) -> typing.Optional[typing.Callable]:
    """
    通过字符串初始化方法

    Args:
        method_path: 方法路径, eg: "pykit_tools.utils.get_caller_location"

    Returns:
        function，未找到返回None

    """
    if not method_path:
        return None
    methods = method_path.split(".")
    _module = importlib.import_module(".".join(methods[:-1]))
    _method = getattr(_module, methods[-1], None)
    if not callable(_method):
        return None
    return _method


def get_caller_location(caller: typing.Callable) -> str:
    """
    或者 类/方法 在项目中的路径
    Args:
        caller: 方法或者类

    Returns:
        路径字符串

    """
    location = "{}.{}".format(caller.__module__, caller.__qualname__)
    return location


class CacheMap(object):
    """
    缓存对象

    Tip: 注意
        若是key太多，容易OOM内存溢出； 且进程销毁会回收
    """

    def __init__(self) -> None:
        # 缓存数据, eg: { key: (timeout, value) }
        self.cache: dict = {}

    def clean(self) -> None:
        """
        清理过期的数据
        """
        now = time.time()
        for key, (timeout, value) in list(self.cache.items()):
            if timeout < now:
                self.cache.pop(key, None)

    def clear(self) -> None:
        """
        清理所有缓存过的数据
        """
        self.cache = {}

    def delete(self, key: str) -> typing.Any:
        """
        根据key删除数据

        Args:
            key:

        Returns:
            返回删除的值

        """
        return self.cache.pop(key, None)

    def get(self, key: str) -> typing.Any:
        """
        根据key获取缓存的数据

        Args:
            key:

        Returns:
            数据值

        """
        now = time.time()
        data = self.cache.get(key)
        if not isinstance(data, (tuple, list)) or len(data) != 2:
            return None
        timeout, value = data
        if timeout < now:
            # 过了超时时间
            self.cache.pop(key, None)
            return None
        return value

    def set(self, key: str, value: typing.Any, timeout: int = 60) -> typing.Any:
        """
        根据key设置数据值value

        Args:
            key: 键
            value: 值
            timeout: 超时时间，单位秒(s)

        Returns:
            值

        """
        t = time.time() + timeout
        self.cache[key] = t, value
        return value
