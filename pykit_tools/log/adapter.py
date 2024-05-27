#!/usr/bin/env python
# coding=utf-8
import socket
import logging
import typing


class LoggerFormatAdapter(logging.LoggerAdapter):
    """
    日志按照字段格式化输出

    eg: 示例
        ```python
        # 其中 get_format_logger 中使用该类
        timer_common_logger = get_format_logger("pykit_tools.timer", ["location", "key", "cost", "ret"])

        timer_common_logger.info(dict(location="my-method", key="my-key", cost=3, ret=True))
        # 日志输出>> "my-method my-key 3 True"
        ```
    """

    def __init__(
        self,
        logger: logging.Logger,
        extra: dict,
        fields: typing.Optional[typing.Union[list[str], tuple[str]]] = None,
        delimiter: str = " ",
        fmt: str = "{}",
    ) -> None:
        """
        初始化构造对象

        Args:
            logger: 通过 logging.getLogger("name") 获得
            extra: 额外字段
            fields: 自定义的字段
            delimiter: 各字段间分隔符，默认空格
            fmt: 自定义格式化字符串，用于最后 fmt.format(dict_msg)
        """
        super(LoggerFormatAdapter, self).__init__(logger, extra)
        if fields:
            if not isinstance(fields, (list, tuple)) or any([not isinstance(f, str) for f in fields]):
                raise TypeError("fields={}, fields item must be a string".format(fields))
            fmt = delimiter.join(["{%s}" % f for f in fields])
        self.fields = fields
        self.fmt: str = fmt

    def process(self, msg: dict, kwargs: typing.Any) -> tuple[str, dict]:
        """
        覆写 `logging.LoggerAdapter.process` 处理自定义格式化日志信息

        Args:
            msg: 使用日志输出时使用字典结构
            kwargs: logger输出定义其他参数

        Returns:
            msg 日志内容字符串
            kwargs 额外参数

        """
        if not isinstance(msg, dict):
            raise TypeError("msg={}, LoggerFormatAdapter process msg must be a dict".format(msg))
        extra: dict = {}
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


def get_format_logger(
    name: str, fields: typing.Union[list, tuple], delimiter: str = " ", extra: typing.Optional[dict] = None
) -> LoggerFormatAdapter:
    """
    根据 LoggerFormatAdapter 获取 logger

    Args:
        name: 名称
        fields: 自定义字段
        delimiter: 字段间分隔符
        extra: 额外参数

    Returns:
        通过Adapter生成的Logger

    """
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
