#!/usr/bin/env python
# coding=utf-8
import pytest
import base64

from pykit_tools import str_tool


@pytest.mark.usefixtures("clean_dir")
def test_md5():
    with pytest.raises(ValueError):
        str_tool.compute_md5()

    value = "test"
    exp_md5 = "098f6bcd4621d373cade4e832627b4f6"
    # test for string
    assert str_tool.compute_md5(value) == exp_md5
    # test for not string
    assert str_tool.compute_md5(1) == "c4ca4238a0b923820dcc509a6f75849b"


@pytest.mark.parametrize(
    "text,expected",
    [
        ("Hello 世界", ""),
        ("Hello世界", "/"),
        ("Hello World", "="),
    ],
)
def test_bse64(text: str, expected: str) -> None:
    s = str_tool.base64url_encode(text)
    if expected:
        assert expected in base64.b64encode(text.encode()).decode()
    assert "+" not in s
    assert "/" not in s
    assert not s.endswith("=")
    assert str_tool.base64url_decode(s) == text


def test_str_number() -> None:
    assert str_tool.is_number("a") is False
    assert str_tool.is_number("2") is True
    assert str_tool.is_number("2.3") is True
    assert str_tool.is_number("-2.3") is True

    assert str_tool.str_to_number("2") == 2
    assert str_tool.str_to_number("2.3") == 2.3
    assert str_tool.str_to_number("2.0") == 2
    assert str_tool.str_to_number("-2.3") == -2.3

    with pytest.raises(ValueError):
        assert str_tool.str_to_number("a")
