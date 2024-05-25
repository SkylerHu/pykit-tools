#!/usr/bin/env python
# coding=utf-8
import hashlib


def compute_md5(*args, **kwargs):
    """计算md5"""
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
