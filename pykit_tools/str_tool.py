#!/usr/bin/env python
# coding=utf-8
import typing
import hashlib
import base64


def compute_md5(*args: typing.Any, **kwargs: typing.Any) -> str:
    """
    根据输入的参数计算出唯一值（将参数值拼接后最后计算md5）

    Args:
        *args: 输入的参数
        **kwargs: 输入的k-v参数

    Returns:
        唯一值
    """
    if not args and not kwargs:
        raise ValueError("*args or **kwargs must not be None")
    if len(args) == 1 and not kwargs:
        if isinstance(args[0], str):
            input_str = args[0]
        else:
            input_str = str(args[0])
    else:
        _info = ["{}:{}".format(i, arg) for i, arg in enumerate(args)]
        _info.extend(["{}:{}".format(k, v) for k, v in kwargs.items()])
        input_str = "&#".join(_info)
    hl = hashlib.md5()
    hl.update(input_str.encode(encoding="utf-8"))
    _key = hl.hexdigest()
    return _key


def is_number(s: str) -> bool:
    """
    判断字符串是否是数值

    Args:
        s: 输入字符串

    Returns:
        返回判断结果

    """
    if s.isdigit():
        # 只能判断正整数
        return True
    try:
        float(s)
        return True
    except ValueError:
        pass
    return False


def str_to_number(s: str) -> typing.Union[int, float]:
    """
    字符串转化成数字

    Args:
        s: 输入字符串

    Returns:
        输出数值，若是不能转化会抛出异常

    """
    if s.isdigit():
        return int(s)
    f = float(s)
    i = int(f)
    if f == i:
        # 浮点和整数相等，直接返回整数
        return i
    # 返回浮点数
    return f


def base64url_encode(value: str) -> str:
    """
    对内容进行URL安全的Base64编码，需要将结果中的部分编码替换：

    - 将结果中的加号 `+` 替换成短划线 `-`;
    - 将结果中的正斜线 `/` 替换成下划线 `_`;
    - 将结果中尾部的所有等号 `=` 省略。

    Args:
        value: 输入字符串

    Returns:
        返回编码后字符串

    """
    s = base64.urlsafe_b64encode(value.encode()).decode()
    s = s.strip("=")
    return s


def base64url_decode(value: str) -> str:
    """
    对URL安全编码进行解码

    Args:
        value: 输入编码字符串

    Returns:
        解码后字符串

    """
    # 补全后面等号
    padding = 4 - (len(value) % 4)
    value = value + ("=" * padding)
    # 解码
    s = base64.urlsafe_b64decode(value.encode()).decode()
    s = s.strip("=")
    return s
