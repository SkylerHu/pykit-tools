#!/usr/bin/env python
# coding=utf-8
import json
import uuid
import pytest
import logging


import pykit_tools
from pykit_tools.utils import CacheMap
from pykit_tools.decorators import cache
from pykit_tools.decorators.cache import method_deco_cache


def test_deco_cache(caplog):
    caplog.set_level(logging.DEBUG, "pykit_tools.error")

    def test(*args):
        if len(args) == 1 and isinstance(args[0], str):
            return args[0]
        return str(uuid.uuid4())

    assert test() != test()

    # test for cache
    fn = method_deco_cache(test)
    assert fn(1, 1) == fn(1, 1)
    assert fn(1, 1) != fn(2, 1)

    # test for key
    fn = method_deco_cache(test, key="test")
    v = fn()
    assert v == fn()
    assert v == fn(1)

    # test for timeout
    fn = method_deco_cache(test, timeout=0)
    v = fn()
    assert v != fn()

    # test for scene
    fn = method_deco_cache(test, scene=cache.CacheScene.DEGRADED)
    assert fn() != fn()
    fn = method_deco_cache(test)
    v = fn()
    assert v == fn()
    with pytest.raises(TypeError):
        fn(scene=1)  # 非法数值
    assert v != fn(scene=cache.CacheScene.DEGRADED)
    assert v != fn(scene=cache.CacheScene.SKIP)

    # test for cannot_cache
    fn = method_deco_cache(test, cannot_cache=lambda a: isinstance(a, str))
    assert fn() != fn()

    # test for cache_max_length
    fn = method_deco_cache(test, cache_max_length=1)
    v = fn()
    assert len(v) > 1
    assert v != fn()

    # test for cache_client
    client = CacheMap()  # also use redis
    fn = method_deco_cache(test, cache_client=client)
    assert fn() == fn()
    fn = method_deco_cache(test, key="test")
    cache.set_global_cache_client(client)
    assert cache.get_global_cache_client() == client
    v = fn()
    assert v == fn()
    assert client.get("test") == json.dumps(v, separators=(",", ":"))
    # 设置错误的缓存数据
    client.set("test", 1)
    assert v != fn()
    # 会有错误日志输出
    assert caplog.records[-1].levelname == "ERROR"

    @method_deco_cache()
    def test2(*args):
        return str(uuid.uuid4())

    assert test2() == test2()

    cache.set_global_cache_client(None)


def test_for_cls_cache():
    class Test(object):

        @method_deco_cache
        def fn(self, *args):
            return str(uuid.uuid4())

        @classmethod
        @method_deco_cache
        def c_fn(cls, *args):
            return str(uuid.uuid4())

        @staticmethod
        @method_deco_cache
        def s_fn(*args):
            return str(uuid.uuid4())

    t = Test()
    assert t.fn() == t.fn()
    assert t.fn() != Test().fn()
    assert t.fn(1, 1) == t.fn(1, 1)
    assert t.fn(1, 1) != t.fn(2, 1)
    assert Test().c_fn(1, 1) == Test().c_fn(1, 1)
    assert Test().c_fn(1, 1) != Test().c_fn(2, 1)
    assert Test.s_fn(1, 1) == Test.s_fn(1, 1)
    assert Test.s_fn(1, 1) != Test.s_fn(2, 1)


def test_cannot_cache():
    def test(*args):
        return str(uuid.uuid4())

    # test for cannot_cache , set tuple value
    client = CacheMap()
    fn = method_deco_cache(test, key="test", cache_client=client, cannot_cache=(1,))
    v = fn()
    assert v == fn()
    # 设置一个缓存失效的数据
    client.set("test", json.dumps(1, separators=(",", ":")))
    assert v != fn()

    # test for cannot_cache , set function
    fn = method_deco_cache(test, key="test2", cache_client=client, cannot_cache=lambda a: isinstance(a, int))
    v = fn()
    assert v == fn()
    client.set("test2", json.dumps(1, separators=(",", ":")))
    assert v != fn()
    client.set("test2", json.dumps("1", separators=(",", ":")))
    assert fn() == "1"

    # disable cannot_cache
    fn = method_deco_cache(test, key="test3", cache_client=client, cannot_cache=False)
    client.set("test3", json.dumps(1, separators=(",", ":")))
    assert fn() == 1

    # cannot_cache set illegal value
    with pytest.raises(TypeError):
        fn = method_deco_cache(test, key="test4", cannot_cache={"test": 1})
        fn()  # 这次设置缓存
        fn()  # 判断缓存是否有效会报错


def test_cache_raise(caplog):
    caplog.set_level(logging.DEBUG, "pykit_tools.error")

    client = CacheMap()

    @method_deco_cache(key="test", cache_client=client)
    def test(a, b):
        return a + b

    with pytest.raises(Exception):
        test(1, "2")
    # 若是提前已有缓存
    client.set("test", json.dumps(3, separators=(",", ":")))
    assert test(1, "2") == 3
    assert test(1, "2", scene=cache.CacheScene.DEGRADED) == 3
    # 设置了标记不被缓存的数据
    client.set("test", json.dumps(False, separators=(",", ":")))
    with pytest.raises(Exception):
        test(1, "2", scene=cache.CacheScene.DEGRADED)

    class Test(object):
        def __init__(self):
            self.a = str(uuid.uuid4())

    @method_deco_cache()
    def get_value():
        return Test()

    # 不会报错，也不会走缓存
    t1 = get_value()
    t2 = get_value()
    assert t1.a != t2.a
    assert "set cache_data error key" in caplog.records[0].message
    assert len(caplog.records) == 2  # 执行函数一次会抛出一次异常


def test_redis_cache(monkeypatch):
    test_key = "test"
    test_word = "Hello world"
    redis_conf = {"host": "127.0.0.1", "port": 6379, "db": 0, "socket_timeout": 10}

    class Settings(object):
        def __init__(self):
            self.APP_CACHE_REDIS = redis_conf

    monkeypatch.setattr(pykit_tools, "settings", Settings())

    assert pykit_tools.settings.APP_CACHE_REDIS == redis_conf

    import redis

    __pool = redis.ConnectionPool(encoding="utf-8", decode_responses=True, **redis_conf)
    _client = redis.StrictRedis(connection_pool=__pool)

    @method_deco_cache(key=test_key)
    def test():
        return test_word

    _client.delete(test_key)
    assert _client.get(test_key) is None
    assert test() == test_word
    assert json.loads(_client.get(test_key)) == test_word
