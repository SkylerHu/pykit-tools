# pykit-tools

[![PyPI - Version](https://img.shields.io/pypi/v/pykit_tools)](https://github.com/SkylerHu/pykit-tools)
[![GitHub Actions Workflow Status](https://github.com/SkylerHu/pykit-tools/actions/workflows/pre-commit.yml/badge.svg?branch=master)](https://github.com/SkylerHu/pykit-tools)
[![GitHub Actions Workflow Status](https://github.com/SkylerHu/pykit-tools/actions/workflows/test-py3.yml/badge.svg?branch=master)](https://github.com/SkylerHu/pykit-tools)
[![Coveralls](https://img.shields.io/coverallsCoverage/github/SkylerHu/pykit-tools?branch=master)](https://github.com/SkylerHu/pykit-tools)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/pykit_tools)](https://github.com/SkylerHu/pykit-tools)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pykit_tools)](https://github.com/SkylerHu/pykit-tools)
[![PyPI - Implementation](https://img.shields.io/pypi/implementation/pykit_tools)](https://github.com/SkylerHu/pykit-tools)
[![GitHub License](https://img.shields.io/github/license/SkylerHu/pykit_tools)](https://github.com/SkylerHu/pykit-tools)

Some methods and decorators commonly used in Python development are encapsulated into lib for easy access and use by other projects.

Python开发经常用的一些方法和装饰器，封装成lib方便其他项目接入使用。

## 1. 安装

	pip install pykit-tools

可查看版本变更记录 [ChangeLog](docs/CHANGELOG-1.x.md)

## 2. 使用(Usage)
各函数具体使用说明可以查看源码注释。

### 2.1 装饰器decorator
- `handle_exception` 用于捕获函数异常，并在出现异常的时候返回默认值
- `time_record` 函数耗时统计
- `method_deco_cache` 方法缓存结果, 只能缓存json序列化的数据类型

### 2.2 日志log相关
- `MultiProcessTimedRotatingFileHandler` 多进程使用的LoggerHandler
- `LoggerFormatAdapter` 日志按照字典字段格式化输出

### 2.3 设计模式
- `Singleton` 单例类

### 2.4 其他工具集
- `cmd.exec_command` 执行shell命令
- `str_tool.compute_md5` 根据输入的参数计算出唯一值（将参数值拼接后最后计算md5）
