#!/usr/bin/env python
# coding=utf-8
import socket
import logging


class LoggerFormatAdapter(logging.LoggerAdapter):

    def __init__(self, logger, extra, fields=None, delimiter=" ", fmt=None):
        """
        :param logger:
        :param extra:
        :param fields:
        :param delimiter: 分隔符, 默认使用空格
        :param fmt:
        """
        super(LoggerFormatAdapter, self).__init__(logger, extra)
        if not fmt and not fields:
            raise ValueError("Either fmt or fields")
        if fields:
            if not isinstance(fields, (list, tuple)) or any([not isinstance(f, str) for f in fields]):
                raise TypeError("fields={}, fields item must be a string".format(fields))
            fmt = delimiter.join(["{%s}" % f for f in fields])
        self.fields = fields
        self.fmt = fmt

    def process(self, msg, kwargs):
        if not isinstance(msg, dict):
            raise TypeError("msg={}, LoggerFormatAdapter process msg must be a dict".format(msg))
        extra = {}
        if self.extra:
            extra.update(self.extra)
        if kwargs.get("extra"):
            extra.update(kwargs["extra"])
        kwargs["extra"] = extra

        params = {}
        if self.fields:
            for field in self.fields:
                v = msg.get(field)
                if v is None or v == "":
                    v = "-"
                params[field] = v
        else:
            params = msg

        _msg = self.fmt.format(**params)
        return _msg, kwargs


def get_format_logger(name, fields, delimiter=" ", extra=None):
    _logger = logging.getLogger(name)
    _extra = {
        "hostname": socket.gethostname(),
    }
    if extra:
        _extra.update(extra)
    logger = LoggerFormatAdapter(_logger, _extra, fields=fields, delimiter=delimiter)
    return logger


# eg: timer_logger.info(dict(key='my-key', cost=3, ret=True))
timer_common_logger = get_format_logger("pykit_tools.timer", ["location", "key", "cost", "ret"])
http_common_logger = get_format_logger(
    "pykit_tools.http",
    [
        "remote_addr",
        "method",
        "uri",
        "query",
        "referer",
        "xff",
        "agent",
        "user",
        "content_length",
        "status",
        "cost",
    ],
    delimiter="\t\t",
)
loop_common_logger = get_format_logger("pykit_tools.loop", ["queue", "action", "key", "wait", "cost", "ret"])
