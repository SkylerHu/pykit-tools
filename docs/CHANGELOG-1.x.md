# Release Notes

## 1.2.0
- feat: 新增函数 `requests_logger` 用于记录requests的请求详细

## 1.1.1
- chore: 调整typing声明兼容支持python3.6

## 1.1.0
- feat: 调整函数可以通过参数传递name名称使用logger
    - 涉及函数有：`exec_command`/`method_deco_cache`/`handle_exception`/`time_record`
- refactor: 字符串format函数都替换成`f`写法

## 1.0.2
- fix: update py-enum>=2.1.1

## 1.0.1 (2024-06-02)
- feat: str_tool中增加函数支持
    - `base64url_encode` 和 `base64url_decode` URL安全的Base64编码
    - `is_number` 和 `str_to_number` 对字符串数字的处理

## 1.0.0 (2024-05-27)
- build: lib发版
