#!/usr/bin/env python
# coding=utf-8
import os
import sys
import time
from logging.handlers import TimedRotatingFileHandler


class MultiProcessTimedRotatingFileHandler(TimedRotatingFileHandler):
    """Similar with `log.TimedRotatingFileHandler`, while this one is
    - Multi process safe
    """

    def __init__(self, *args, **kwargs):
        delay = kwargs.pop("delay", False)
        # 未初始化好，不能打开文件，所以设置delay=True
        super(MultiProcessTimedRotatingFileHandler, self).__init__(*args, delay=True, **kwargs)
        self.delay = delay
        self.useFileName = self._compute_fn()
        # 按需重新打开文件
        self.stream = None
        if not self.delay:
            self.stream = self._open()

    def _compute_fn(self):
        if self.utc:
            t = time.gmtime()
        else:
            t = time.localtime()
        return self.baseFilename + "." + time.strftime(self.suffix, t)

    def shouldRollover(self, record):
        if self.useFileName != self._compute_fn():
            return True
        return False

    def _open(self):
        if sys.version_info >= (3, 9):
            f = open(self.useFileName, self.mode, encoding=self.encoding, errors=self.errors)
        else:
            f = open(self.useFileName, self.mode, encoding=self.encoding)
        # 重置 软链接
        if os.path.isfile(self.baseFilename):
            os.remove(self.baseFilename)
        os.symlink(self.useFileName, self.baseFilename)
        # 返回打开的文件
        return f

    def doRollover(self):
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
