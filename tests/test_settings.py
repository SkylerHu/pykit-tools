#!/usr/bin/env python
# coding=utf-8
import pytest

from pykit_tools import settings, SettingsProxy


def test_settings():
    with pytest.raises(AttributeError):
        settings.DEBUG = True

    with pytest.raises(AttributeError):
        del settings.DEBUG


def test_proxy(monkeypatch, capsys):
    monkeypatch.setenv("PY_SETTINGS_MODULE", "tests.settings")
    assert SettingsProxy().APP_CACHE_REDIS is not None

    monkeypatch.setenv("PY_SETTINGS_MODULE", "")
    assert SettingsProxy().APP_CACHE_REDIS is None
    # 有提示
    captured = capsys.readouterr()
    assert "Warning: settings configuration file not found" in captured.out

    monkeypatch.setenv("PY_SETTINGS_MODULE", "tests.settings_v2")
    assert SettingsProxy().APP_CACHE_REDIS is None
    captured = capsys.readouterr()
    assert "Please set the correct" in captured.out
