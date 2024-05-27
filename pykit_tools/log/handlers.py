#!/usr/bin/env python
# coding=utf-8
import os
import io
import time
import typing
import logging
from logging.handlers import TimedRotatingFileHandler


class MultiProcessTimedRotatingFileHandler(TimedRotatingFileHandler):
    """
    Similar with `logging.TimedRotatingFileHandler`, while this one is Multi process safe.

    多进程使用的LoggerHandler
    """

    def __init__(self, *args: typing.Any, **kwargs: typing.Any) -> None:
        delay = kwargs.get("delay", False)
        # 未初始化好，不能打开文件，所以设置delay=True
        kwargs["delay"] = True
        super(MultiProcessTimedRotatingFileHandler, self).__init__(*args, **kwargs)
        self.delay = delay
        self.useFileName = self._compute_fn()
        # 按需重新打开文件
        self.stream: typing.Optional[io.TextIOWrapper] = None  # type: ignore
        if not self.delay:
            self.stream = self._open()

    def _open(self) -> io.TextIOWrapper:
        _file = open(self.useFileName, self.mode, encoding=self.encoding, errors=self.errors)
        # 重置 软链接
        try:
            if os.path.isfile(self.baseFilename):
                os.remove(self.baseFilename)
            os.symlink(self.useFileName, self.baseFilename)
        except Exception:
            # 避免多进程并发删除
            pass

        _f = typing.cast(io.TextIOWrapper, _file)
        # 返回打开的文件
        return _f

    def _compute_fn(self) -> str:
        if self.utc:
            t = time.gmtime()
        else:
            t = time.localtime()
        filename = f"{self.baseFilename}.{time.strftime(self.suffix, t)}"
        return filename

    def shouldRollover(self, record: logging.LogRecord) -> bool:
        if self.useFileName != self._compute_fn():
            return True
        return False

    def doRollover(self) -> None:
        if self.stream:
            self.stream.close()
            self.stream = None

        # rotate
        self.useFileName = self._compute_fn()
        if not self.delay:
            self.stream = self._open()

        if self.backupCount > 0:
            # del backup
            for s in self.getFilesToDelete():
                os.remove(s)
