#!/usr/bin/env python
# coding=utf-8
import logging

from pykit_tools.cmd import exec_command


def test_exec_command(monkeypatch):
    code, stdout, stderr = exec_command("ls -al")
    assert code == 0
    assert isinstance(stdout, str)
    assert stdout is not None
    assert stderr == ""

    code, stdout, stderr = exec_command("sleep 0.2", timeout=0.1)
    assert code == -9
    assert stdout == ""
    assert stderr == ""


def test_exec_command_popen_kwargs(monkeypatch):
    code, stdout, stderr = exec_command("ls -al", popen_kwargs={"cwd": "/tmp"})
    assert code == 0
    assert isinstance(stdout, str)
    assert stdout is not None
    assert stderr == ""


def test_exec_command_log_cmd(monkeypatch, caplog):
    caplog.set_level(logging.DEBUG, "pykit_tools.cmd")
    code, stdout, stderr = exec_command("ls -al", log_cmd=True)
    assert code == 0
    assert stdout is not None
    assert stderr == ""
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "INFO"
    assert "ls -al" in caplog.records[0].message
    assert "code=0" in caplog.records[0].message


def test_exec_command_stderr_truncation(caplog):
    """测试 stderr 超过 err_max_length 时的截断逻辑"""
    caplog.set_level(logging.DEBUG, "pykit_tools.cmd")

    # 使用一个会产生长 stderr 的命令，设置较小的 err_max_length
    # 用 bash -c 输出一个超长的 stderr
    long_stderr = "A" * 100
    code, stdout, stderr = exec_command(f"bash -c \"echo -n '{long_stderr}' >&2; exit 1\"", err_max_length=20)

    assert code == 1
    assert stderr == long_stderr
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "ERROR"
    # 验证日志中包含截断标记
    assert "\n\t...\n" in caplog.records[0].message
    # 验证日志中包含 stderr 的前半部分（前10个字符）
    assert "AAAAAAAAAA" in caplog.records[0].message


def test_exec_command_stderr_no_truncation(caplog):
    """测试 stderr 未超过 err_max_length 时不截断"""
    caplog.set_level(logging.DEBUG, "pykit_tools.cmd")

    short_stderr = "short error"
    code, stdout, stderr = exec_command(f"bash -c \"echo -n '{short_stderr}' >&2; exit 1\"", err_max_length=100)

    assert code == 1
    assert stderr == short_stderr
    assert len(caplog.records) == 1
    assert caplog.records[0].levelname == "ERROR"
    # 验证日志中包含完整的 stderr，没有截断标记
    assert "\n\t...\n" not in caplog.records[0].message
    assert short_stderr in caplog.records[0].message
