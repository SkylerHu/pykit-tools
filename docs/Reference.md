# 使用(Usage)

## 装饰器
::: decorators.common
    options:
        members:
          - handle_exception
          - time_record

::: decorators.cache
    options:
        members:
            - method_deco_cache
            - singleton_refresh_regular

## 装饰器相关
::: decorators.cache.CacheScene
    options:
        show_source: true
        show_bases: true

::: decorators.cache
    options:
        members:
            - set_global_cache_client
            - get_global_cache_client

## 日志相关
::: log.adapter

::: log.handlers

## 设计模式
::: patterns.singleton

## 其他
::: cmd
::: str_tool
::: utils
