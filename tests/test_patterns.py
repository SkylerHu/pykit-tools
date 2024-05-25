#!/usr/bin/env python
# coding=utf-8
import pytest

from pykit_tools.patterns.singleton import Singleton
from pykit_tools.decorators.cache import singleton_refresh_regular


def test_singleton_cls():

    class Test(object):
        pass

    assert Test() != Test()

    class TestV2(Singleton):
        pass

    assert TestV2() == TestV2()


def test_refresh_singleton():

    class Test(object):

        @staticmethod
        def s_fn():
            pass

    t = singleton_refresh_regular(Test)
    assert t() == t()

    # 超时会重新构建实例
    t2 = singleton_refresh_regular(Test, timeout=0)
    assert t2() != t2()

    with pytest.raises(TypeError):
        singleton_refresh_regular(Test.s_fn)

    @singleton_refresh_regular()
    class TestV2(object):
        pass

    assert TestV2() == TestV2()
