#!/usr/bin/env python
# coding=utf-8
import pytest

from pykit_tools.str_tool import compute_md5


@pytest.mark.usefixtures("clean_dir")
def test_md5():
    with pytest.raises(ValueError):
        compute_md5()

    value = "test"
    exp_md5 = "098f6bcd4621d373cade4e832627b4f6"
    # test for string
    assert compute_md5(value) == exp_md5
    # test for not string
    assert compute_md5(1) == "c4ca4238a0b923820dcc509a6f75849b"
