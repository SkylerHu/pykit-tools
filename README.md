# pykit-tools

[![PyPI - Version](https://img.shields.io/pypi/v/pykit-tools)](https://github.com/SkylerHu/pykit-tools)
[![GitHub Actions Workflow Status](https://github.com/SkylerHu/pykit-tools/actions/workflows/pre-commit.yml/badge.svg?branch=master)](https://github.com/SkylerHu/pykit-tools)
[![GitHub Actions Workflow Status](https://github.com/SkylerHu/pykit-tools/actions/workflows/test-py3.yml/badge.svg?branch=master)](https://github.com/SkylerHu/pykit-tools)
[![Coveralls](https://img.shields.io/coverallsCoverage/github/SkylerHu/pykit-tools?branch=master)](https://github.com/SkylerHu/pykit-tools)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/pykit-tools)](https://github.com/SkylerHu/pykit-tools)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/pykit-tools)](https://github.com/SkylerHu/pykit-tools)
[![PyPI - Implementation](https://img.shields.io/pypi/implementation/pykit-tools)](https://github.com/SkylerHu/pykit-tools)
[![GitHub License](https://img.shields.io/github/license/SkylerHu/pykit-tools)](https://github.com/SkylerHu/pykit-tools)
[![Read the Docs](https://img.shields.io/readthedocs/pykit-tools)](https://pykit-tools.readthedocs.io)


Some methods and decorators commonly used in Python development are encapsulated into lib for easy access and use by other projects.

Python开发经常用的一些方法和装饰器，封装成lib方便其他项目接入使用。

## 1. 安装

	pip install pykit-tools

可查看版本变更记录 [ChangeLog](./docs/CHANGELOG-1.x.md)

## 2. 介绍
各函数具体使用说明可以 [readthedocs](https://pykit-tools.readthedocs.io) 或者直接查看源码注释。

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
- `str_tool.base64url_encode` 和 `str_tool.base64url_decode` URL安全的Base64编码

## 3. 配置

### 3.1 运行配置
可以通过指定环境变量`PY_SETTINGS_MODULE`加载配置文件：

    export PY_SETTINGS_MODULE=${your_project.settings_file.py}

支持的配置项有：

| 配置项 | 类型 | 说明 | 默认值 |
| - | - | - | - |
| DEBUG | bool | 是否debug开发模式 | False |
| APP_CACHE_REDIS | dict | 用于缓存的redis配置，eg: `{'host': '127.0.0.1', 'port': 6379, 'db': 0, 'socket_timeout': 10}` | None |


### 3.2 日志配置
提供以下几种loggers：
- `pykit_tools` 用于消息的父日志记录器，一般用以下细分的logger
- `pykit_tools.cmd` 用于记录`cmd.exec_command`执行的命令行
- `pykit_tools.error` 用于处理错误时输出，例如`handle_exception`中有用到
