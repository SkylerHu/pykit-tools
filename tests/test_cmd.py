#!/usr/bin/env python
# coding=utf-8
import subprocess

from pykit_tools.cmd import exec_command


def test_exec_command(monkeypatch):
    code, stdout, stderr = exec_command("ls -al")
    assert code == 0
    assert stdout is not None
    assert stderr == ""

    code, stdout, stderr = exec_command("sleep 0.01", timeout=0.01)
    assert code == -9
    assert stdout == ""
    assert stderr == ""

    def for_stdout_raise(self):
        return {"a": "test"}, None

    monkeypatch.setattr(subprocess.Popen, "communicate", for_stdout_raise)
    code, stdout, stderr = exec_command("ls -al")
    # 返回数据类型不对会报错
    assert "object has no attribute" in stdout

    def for_stderr_raise(self):
        return None, {"a": "test"}

    monkeypatch.setattr(subprocess.Popen, "communicate", for_stderr_raise)
    code, stdout, stderr = exec_command("ls -al")
    # 返回数据类型不对会报错
    assert "object has no attribute" in stderr
