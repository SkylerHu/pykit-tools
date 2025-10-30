#!/usr/bin/env python
# coding=utf-8
import logging
import subprocess

from pykit_tools.cmd import exec_command


def test_exec_command(monkeypatch):
    code, stdout, stderr = exec_command("ls -al")
    assert code == 0
    assert isinstance(stdout, str)
    assert stdout is not None
    assert stderr == ""

    code, stdout, stderr = exec_command("sleep 0.01", timeout=0.01)
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


def test_exec_command_err_max_length(monkeypatch, caplog):
    caplog.set_level(logging.DEBUG, "pykit_tools.cmd")

    def for_stderr_max_length(self):
        return None, "a" * 1024

    monkeypatch.setattr(subprocess.Popen, "communicate", for_stderr_max_length)
    _, _, stderr = exec_command("ls -al", err_max_length=16)
    assert stderr == "a" * 1024
    assert caplog.records[0].levelname == "ERROR"
    assert "a" * 8 + "\n\t...\n" + "a" * 8 in caplog.records[0].message
