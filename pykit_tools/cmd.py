#!/usr/bin/env python
# coding=utf-8
import typing
import logging
import subprocess
import threading


def exec_command(
    command: str,
    timeout: int = 60,
    log_cmd: bool = False,
    err_max_length: int = 1024,
    logger_name: str = "pykit_tools.cmd",
) -> typing.Tuple[int, str, str]:
    """
    执行shell命令

    Args:
        command: 要执行的命令
        timeout: 超时时间，单位秒(s)
        log_cmd: 是否记录命令日志，默认不记录（仅在异常时记录异常日志）
        err_max_length: 错误输出最大长度，超过该长度则截断; 0表示不截断
        logger_name: 日志名称

    Returns:
        code 系统执行返回，等于0表示成功
        stdout 执行输出
        stderr 执行错误输出

    """
    _log_cmd = f"[timeout {timeout} {command}]"

    child = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # shell timeout 不能和 Python Timer结合，timeout是fork子进程去执行, Timer kill掉timeout会产生defunct僵尸进程
    my_timer = threading.Timer(timeout, lambda process: process.kill(), [child])
    stdout, stderr = "", ""
    try:
        my_timer.start()
        b_stdout, b_stderr = child.communicate()
        try:
            stdout = b_stdout.decode("utf-8", "strict") if b_stdout else ""
        except Exception as e:
            logging.getLogger(logger_name).exception(f"{_log_cmd} decode stdout error: {e}")
            stdout = str(e)
        try:
            stderr = b_stderr.decode("utf-8", "strict") if b_stderr else ""
        except Exception as e:
            logging.getLogger(logger_name).exception(f"{_log_cmd} decode stderr error: {e}")
            stderr = str(e)
    finally:
        my_timer.cancel()
    code = child.returncode

    # 记录日志
    _msg = f"{_log_cmd} code={code}"
    if code != 0 and err_max_length > 0:
        log_err = stderr
        if len(stderr) > err_max_length:
            # 截取前后一半，中间用...代替
            pre_idx = err_max_length // 2
            log_err = stderr[:pre_idx] + "\n\t...\n" + stderr[:-pre_idx]
        _msg = f"{_msg}\n\tstderr: {log_err}"
        logging.getLogger(logger_name).error(_msg)
    elif log_cmd:
        logging.getLogger(logger_name).info(_msg)

    return code, stdout, stderr
