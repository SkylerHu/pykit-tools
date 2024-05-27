#!/usr/bin/env python
# coding=utf-8
import os
import time
import datetime
import pytest
import logging

from pykit_tools.log import adapter, handlers


def test_format_adapter(caplog):
    caplog.set_level(logging.DEBUG, logger="pykit_tools")
    _logger = logging.getLogger("pykit_tools")

    with pytest.raises(TypeError):
        adapter.LoggerFormatAdapter(_logger, None, fields="message")

    fmt_logger = adapter.LoggerFormatAdapter(_logger, None, fmt="{message}")
    fmt_logger.debug(dict(message="Hello world"))
    assert "Hello world" in caplog.text
    assert len(caplog.records) == 1

    logger = adapter.LoggerFormatAdapter(_logger, None, fields=["message", "cost"])
    with pytest.raises(TypeError):
        logger.debug("test message")
    logger.debug(dict(message="Hello world"))
    assert len(caplog.records) == 2, "The log file has two lines"
    logger.debug(dict(message="Hello world"), extra={"hostname": "localhost"})

    logger = adapter.LoggerFormatAdapter(_logger, {"hostname": "localhost"}, fields=["message"])
    logger.debug(dict(message="Hello world"))


def test_format_logger():
    logger = adapter.get_format_logger("pykit_tools", fields=["message", "cost"], extra={"hostname": "localhost"})
    logger.debug(dict(message="Hello world"))


def get_logger(name, **kwargs):
    file_name = os.path.join(os.getcwd(), "{}.log".format(name))
    _handler = handlers.MultiProcessTimedRotatingFileHandler(file_name, when="D", **kwargs)
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(module)s.%(name)s[%(lineno)s] %(message)s")
    _handler.setFormatter(fmt)
    _logger = logging.getLogger(name)
    _logger.addHandler(_handler)
    _logger.setLevel(logging.DEBUG)
    _logger.propagate = False
    return _logger


def patch_handle_file_rotate(monkeypatch, logger, days=0):
    handler = logger.handlers[0]
    now = datetime.datetime.now()
    if days:
        t = (now + datetime.timedelta(days=days)).timetuple()
    else:
        t = now.timetuple()
    new_filename = handler.baseFilename + "." + time.strftime(handler.suffix, t)
    monkeypatch.setattr(handlers.MultiProcessTimedRotatingFileHandler, "_compute_fn", lambda *args: new_filename)


@pytest.mark.usefixtures("clean_dir")
def test_multi_handler_use_utc():
    get_logger("test_multi_utc", utc=True).debug("Hello world")


@pytest.mark.usefixtures("clean_dir")
def test_multi_handler_use_delay(monkeypatch):
    get_logger("test_multi_delay", delay=True).debug("Hello world")

    logger = get_logger("test_multi_delay_v2", delay=True)
    patch_handle_file_rotate(monkeypatch, logger, days=1)
    logger.debug("Hello world")


@pytest.mark.usefixtures("clean_dir")
def test_multi_handler(monkeypatch):
    name = "test_multi_handler"
    backup_count = 2
    logger = get_logger(name, backupCount=backup_count)
    handler = logger.handlers[0]
    assert isinstance(handler, handlers.MultiProcessTimedRotatingFileHandler)
    # 输出日志
    logger.debug("Hello world")
    log_file = handler.useFileName
    with open(log_file, "r") as f:
        message = f.read()
    assert "Hello world" in message

    log_dir, file_name = os.path.split(handler.baseFilename)
    log_dir = os.path.dirname(log_file)
    assert os.getcwd() == log_dir
    filenames = sorted(os.listdir(log_dir))
    assert len(filenames) == 2
    assert file_name in filenames
    assert os.path.islink(file_name), "{} is not a link".format(file_name)
    assert os.path.basename(os.readlink(file_name)) == filenames[1], filenames

    # 轮转日志
    patch_handle_file_rotate(monkeypatch, logger, days=1)
    assert handler.useFileName != handler._compute_fn()
    logger.debug("Hello world")
    # 会轮转生成3个文件
    filenames = sorted(os.listdir(log_dir))
    assert len(filenames) == 3, filenames

    # 再轮转一次
    patch_handle_file_rotate(monkeypatch, logger, days=2)
    logger.debug("Hello world")
    assert handler.backupCount == backup_count
    filenames = sorted(os.listdir(log_dir))
    # 文件数不变，会删除1个文件，之所以3个是因为还有个软链
    assert len(filenames) == handler.backupCount + 1

    # 测试轮转时文件报错
    patch_handle_file_rotate(monkeypatch, logger, days=3)
    monkeypatch.setattr(os.path, "isfile", lambda x: False)
    logger.debug("Hello world")
