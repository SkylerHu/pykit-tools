#!/usr/bin/env python
# coding=utf-8
import random
import logging

import pytest

from pykit_tools.decorators.common import handle_exception, time_record


def test_handle_exception(caplog, monkeypatch):
    caplog.set_level(logging.DEBUG, "pykit_tools.error")

    def test(a, b):
        return a + b

    assert test(1, 2) == 3
    with pytest.raises(TypeError):
        test(1, "2")

    # test for max_retries and retry_for
    fn = handle_exception(test, max_retries=2, retry_for=ValueError)
    assert fn(1, 2) == 3
    assert fn(1, "2") is False
    # 重试了1次, 没有加retry_for
    assert len(caplog.records) == 1, "'max_retries' must be used in conjunction with 'retry_for'"
    caplog.clear()
    fn = handle_exception(test, default=0, max_retries=2, retry_for=TypeError)
    assert fn(1, "2") == 0
    assert len(caplog.records) == 2  # 重试了2次

    # test for is_raise
    caplog.clear()
    fn = handle_exception(test, default=0, max_retries=2, retry_for=TypeError, is_raise=True)
    with pytest.raises(TypeError):
        fn(1, "2")
    assert len(caplog.records) == 2  # 重试了2次

    # test for retry_delay/retry_jitter
    caplog.clear()
    fn = handle_exception(test, default=0, max_retries=2, retry_for=TypeError, retry_delay=0.01, retry_jitter=False)
    assert fn(1, "2") == 0
    monkeypatch.setattr(random, "randint", lambda *args: 0)
    assert fn(1, "2") == 0
    fn = handle_exception(test, default=0, max_retries=2, retry_for=TypeError, retry_delay=0.1)
    assert fn(1, "2") == 0

    # test for log_args
    error_msg = caplog.records[-1].getMessage()
    assert "unsupported operand type" in error_msg
    assert "args: (1, '2')" in error_msg
    caplog.clear()
    fn = handle_exception(test, default=0, log_args=False)
    assert fn(1, "2") == 0
    assert "args: (1, '2')" not in caplog.records[-1].getMessage()

    # test for default is function

    @handle_exception(default=dict)
    def test2(a, b):
        return a + b

    # 错误参数执行，返回默认值
    assert test2(1, "2") == {}


def test_time_record(caplog):
    caplog.set_level(logging.DEBUG, "pykit_tools.timer")
    caplog.set_level(logging.DEBUG, "pykit_tools.error")

    def test(a):
        return a

    fn = time_record(test)
    value = 0
    fn(value)
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "INFO"
    key, cost, ret = caplog.text.split()[-3:]
    assert key == str(value)
    assert float(cost) * 1000 == int(float(cost) * 1000), "Time cost to 3 decimal places"
    assert float(cost) >= value * 1000
    assert ret == str(value)

    # test for format_key / format_ret
    caplog.clear()
    fn = time_record(test, format_key=lambda *args, **kwargs: "key", format_ret=lambda v: "ret")
    fn(value)
    key, cost, ret = caplog.text.split()[-3:]
    assert key == "key"
    assert ret == "ret"

    # tet format_key raise error
    caplog.clear()
    fn = time_record(test, format_key=lambda v: "key" + 1)
    fn(value)
    assert len(caplog.records) == 2
    assert caplog.records[0].levelname == "ERROR"

    # test for other ...

    @time_record()
    def test2():
        pass

    caplog.clear()
    test2()
    key, cost, ret = caplog.text.split()[-3:]
    assert key == "-"
    assert float(cost) >= 0
    assert ret == "-"
