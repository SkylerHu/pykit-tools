#!/usr/bin/env python
# coding=utf-8
import typing

from pykit_tools import str_tool, utils


class SingletonMeta(type):
    """
    设计模式：单例类

    eg: 示例
        ```python
        class YouClass(metaclass=SingletonMeta)
            pass
        ```
    """

    _instances: dict = {}

    def __call__(cls, *args: typing.Any, **kwargs: typing.Any) -> typing.Any:
        _key = str_tool.compute_md5(utils.get_caller_location(cls), *args, **kwargs)
        if _key not in cls._instances:
            cls._instances[_key] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[_key]


class Singleton(metaclass=SingletonMeta):
    """可以提供给类直接继承"""

    pass
