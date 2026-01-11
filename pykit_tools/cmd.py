#!/usr/bin/env python
# coding=utf-8
import typing
import logging
import subprocess


def exec_command(
    command: str,
    timeout: int = 60,
    log_cmd: bool = False,
    err_max_length: int = 1024,
    logger_name: str = "pykit_tools.cmd",
    logger_level: int = logging.ERROR,
    popen_kwargs: typing.Optional[typing.Dict] = None,
) -> typing.Tuple[int, str, str]:
    """
    执行shell命令

    Args:
        command: 要执行的命令
        timeout: 超时时间，单位秒(s)
        log_cmd: 是否记录命令日志，默认不记录（仅在异常时记录异常日志）
        err_max_length: 错误输出最大长度，超过该长度则截断; 0表示不截断
        logger_name: 日志名称
        logger_level: 异常时设置日志的级别
        popen_kwargs: 透传 subprocess.Popen 的参数

    Returns:
        code 系统执行返回，等于0表示成功
        stdout 执行输出
        stderr 执行错误输出

    """
    _log_cmd = f"[timeout {timeout} {command}]"

    kwargs: typing.Dict = {
        "text": True,
        "shell": True,
        "encoding": "utf-8",
        "universal_newlines": True,
    }
    if popen_kwargs:
        kwargs.update(popen_kwargs)

    stdout, stderr = "", ""
    try:
        result: subprocess.CompletedProcess = subprocess.run(command, capture_output=True, timeout=timeout, **kwargs)
        code = result.returncode
        stdout = result.stdout
        stderr = result.stderr
    except subprocess.TimeoutExpired:
        code = -9

    # 记录日志
    _msg = f"{_log_cmd} code={code}"
    if code != 0 and err_max_length > 0:
        log_err = stderr or ""
        if len(stderr) > err_max_length:
            # 截取前后一半，中间用...代替
            pre_idx = err_max_length // 2
            log_err = stderr[:pre_idx] + "\n\t...\n" + stderr[:-pre_idx]
        _msg = f"{_msg}\n\tstderr: {log_err}"
        logging.getLogger(logger_name).log(logger_level, _msg)
    elif log_cmd:
        logging.getLogger(logger_name).info(_msg)

    return code, stdout, stderr
