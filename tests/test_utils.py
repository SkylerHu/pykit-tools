#!/usr/bin/env python
# coding=utf-8
import time

from pykit_tools import utils


def test_find_method():
    assert utils.find_method_by_str("") is None

    fn = utils.find_method_by_str("pykit_tools.utils.CacheMap")
    assert fn == utils.CacheMap

    assert utils.find_method_by_str("pykit_tools.utils") is None


def for_test_fn():
    pass


class ForTest(object):
    @staticmethod
    def s_fn():
        pass

    @classmethod
    def c_fn(cls):
        pass

    def my_fn(self):
        pass


def test_location():
    assert utils.get_caller_location(for_test_fn) == "tests.test_utils.for_test_fn"

    assert utils.get_caller_location(ForTest) == "tests.test_utils.ForTest"
    assert utils.get_caller_location(ForTest.s_fn) == "tests.test_utils.ForTest.s_fn"
    assert utils.get_caller_location(ForTest.c_fn) == "tests.test_utils.ForTest.c_fn"
    assert utils.get_caller_location(ForTest().my_fn) == "tests.test_utils.ForTest.my_fn"


def test_cache_map():
    cache_client = utils.CacheMap()
    cache_client.set("test", 1, timeout=0.001)
    assert cache_client.get("test") == 1
    time.sleep(0.001)
    assert cache_client.get("test") is None

    # test for clean
    cache_client.set("test", 1, timeout=0.001)
    cache_client.clean()
    time.sleep(0.001)
    cache_client.clean()
    assert cache_client.get("test") is None

    # test for clear
    cache_client.set("test", 1)
    assert cache_client.get("test") == 1
    cache_client.clear()
    assert cache_client.get("test") is None

    # test for delete
    cache_client.set("test", 1)
    cache_client.delete("test")
    assert cache_client.get("test") is None
