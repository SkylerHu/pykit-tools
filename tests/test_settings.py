#!/usr/bin/env python
# coding=utf-8
import pytest

from pykit_tools import settings, SettingsProxy


def test_settings():
    with pytest.raises(AttributeError):
        settings.DEBUG = True

    with pytest.raises(AttributeError):
        del settings.DEBUG


def test_proxy(monkeypatch):
    monkeypatch.setenv("PY_SETTINGS_MODULE", "tests.settings")
    assert SettingsProxy().APP_CACHE_REDIS is not None

    monkeypatch.setenv("PY_SETTINGS_MODULE", "")
    assert SettingsProxy().APP_CACHE_REDIS is None
