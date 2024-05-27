#!/usr/bin/env python
# coding=utf-8
import logging
import subprocess
import threading


logger = logging.getLogger("pykit_tools.cmd")


def exec_command(command: str, timeout: int = 60) -> tuple[int, str, str]:
    """
    执行shell命令

    Args:
        command: 要执行的命令
        timeout: 超时时间，单位秒(s)

    Returns:
        code 系统执行返回，等于0表示成功
        stdout 执行输出
        stderr 执行错误输出

    """
    logger.debug("start exec command: timeout {} {}".format(timeout, command))

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
            stdout = str(e)
        try:
            stderr = b_stderr.decode("utf-8", "strict") if b_stderr else ""
        except Exception as e:
            stderr = str(e)
    finally:
        my_timer.cancel()
    code = child.returncode

    # 记录日志
    msg = "command:[timeout {} {}] code={}\nstdout: {}\nstderr: {}".format(timeout, command, code, stdout, stdout)
    if code != 0:
        logger.error(msg)
    else:
        logger.info(msg)

    return code, stdout, stderr
