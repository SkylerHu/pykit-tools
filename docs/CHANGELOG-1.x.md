# Release Notes

## 1.1.0
- feat: 调整装饰器可以通过参数传递name名称使用logger
    - `exec_command` 函数新增参数 `logger_name`
    - `method_deco_cache` 函数新增参数 `err_logger_name`
    - `handle_exception` 函数新增参数 `err_logger_name`
    - `time_record` 函数新增参数 `err_logger_name`
- refactor: 字符串format函数都替换成`f`写法

## 1.0.2
- fix: update py-enum>=2.1.1

## 1.0.1 (2024-06-02)
- feat: str_tool中增加函数支持
    - `base64url_encode` 和 `base64url_decode` URL安全的Base64编码
    - `is_number` 和 `str_to_number` 对字符串数字的处理

## 1.0.0 (2024-05-27)
- build: lib发版
