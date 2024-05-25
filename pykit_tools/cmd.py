#!/usr/bin/env python
# coding=utf-8
import logging
import subprocess
import threading


logger = logging.getLogger("pykit_tools.cmd")


def exec_command(command, timeout=60):
    """执行shell"""
    logger.debug("start exec command: timeout {} {}".format(timeout, command))

    child = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    # shell timeout 不能和 Python Timer结合，timeout是fork子进程去执行, Timer kill掉timeout会产生defunct僵尸进程
    my_timer = threading.Timer(timeout, lambda process: process.kill(), [child])
    try:
        my_timer.start()
        stdout, stderr = child.communicate()
        try:
            stdout = stdout.decode("utf-8", "strict") if stdout else None
        except Exception as e:
            stdout = str(e)
        try:
            stderr = stderr.decode("utf-8", "strict") if stderr else None
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
