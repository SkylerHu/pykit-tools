#!/usr/bin/env python
# coding=utf-8
import time
import importlib


def find_method_by_str(method_path):
    """通过字符串，寻找方法"""
    if not method_path:
        return None
    methods = method_path.split(".")
    _module = importlib.import_module(".".join(methods[:-1]))
    _method = getattr(_module, methods[-1], None)
    if not callable(_method):
        return None
    return _method


def get_caller_location(caller):
    location = "{}.{}".format(caller.__module__, caller.__qualname__)
    return location


class CacheMap(object):
    """
    需要注意的是：若是key太多，容易OOM内存溢出
    """

    def __init__(self):
        # 缓存数据, eg: { key: (timeout, value) }
        self.cache = {}

    def clean(self):
        """清理过期的数据"""
        now = time.time()
        for key, (timeout, value) in list(self.cache.items()):
            if timeout < now:
                self.cache.pop(key, None)

    def clear(self):
        self.cache = {}

    def delete(self, key):
        self.cache.pop(key, None)

    def get(self, key):
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

    def set(self, key, value, timeout=60):
        """
        :param key:
        :param value:
        :param timeout: 单位秒
        :return:
        """
        t = time.time() + timeout
        self.cache[key] = t, value
        return value
