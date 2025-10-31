#!/usr/bin/env python
# coding=utf-8
import logging
import typing
import pytest
from unittest.mock import Mock
import requests  # type: ignore

from pykit_tools.decorators.req_utils import requests_logger


class BaseRequest(object):

    def __init__(self, default_ua: str = "", logger_name: str = "pykit_tools.requests"):
        self.request = requests_logger(requests.request, default_ua=default_ua, logger_name=logger_name)

    def get(self, url: str, **kwargs: typing.Any) -> requests.Response:
        return self.request("GET", url, **kwargs)

    def post(self, url: str, **kwargs: typing.Any) -> requests.Response:
        return self.request("POST", url, **kwargs)

    def put(self, url: str, **kwargs: typing.Any) -> requests.Response:
        return self.request("PUT", url, **kwargs)

    def delete(self, url: str, **kwargs: typing.Any) -> requests.Response:
        return self.request("DELETE", url, **kwargs)

    def patch(self, url: str, **kwargs: typing.Any) -> requests.Response:
        return self.request("PATCH", url, **kwargs)

    def head(self, url: str, **kwargs: typing.Any) -> requests.Response:
        return self.request("HEAD", url, **kwargs)

    def options(self, url: str, **kwargs: typing.Any) -> requests.Response:
        return self.request("OPTIONS", url, **kwargs)


class TestRequestsLogger:
    """测试 requests_logger 装饰器的所有分支"""

    def test_decorator_without_args(self, caplog):
        """测试不带参数直接装饰函数"""
        caplog.set_level(logging.DEBUG, "pykit_tools.requests")

        @requests_logger
        def mock_request(method, url, **kwargs):
            response = Mock()
            response.status_code = 200
            response.content = b"test response"
            response.text = "test response"
            return response

        response = mock_request("GET", "http://example.com")
        assert response.status_code == 200
        assert len(caplog.records) == 1
        # err 初始化为 ""，如果没有异常，if err 为 False，会调用 logger.info
        assert caplog.records[0].levelname == "INFO"
        assert "GET http://example.com" in caplog.records[0].message

    def test_decorator_as_partial(self, caplog):
        """测试装饰器作为 partial 函数使用"""
        caplog.set_level(logging.DEBUG, "pykit_tools.custom_logger")

        def mock_request(method, url, **kwargs):
            response = Mock()
            response.status_code = 200
            response.content = b"test"
            response.text = "test"
            return response

        decorated = requests_logger(default_ua="TestUA/1.0", logger_name="pykit_tools.custom_logger")(mock_request)

        response = decorated("GET", "http://example.com", headers={"X-Custom": "value"})
        assert response.status_code == 200
        assert len(caplog.records) == 1
        # 验证默认 UA 被设置
        assert decorated.__wrapped__ == mock_request

    def test_default_ua_setting(self, caplog):
        """测试 default_ua 参数设置 User-Agent"""
        caplog.set_level(logging.DEBUG, "pykit_tools.requests")
        default_ua = "MyBot/1.0"

        @requests_logger(default_ua=default_ua)
        def mock_request(method, url, headers=None, **kwargs):
            assert headers is not None
            assert headers["User-Agent"] == default_ua
            response = Mock()
            response.status_code = 200
            response.content = b"test"
            response.text = "test"
            return response

        mock_request("GET", "http://example.com")

    def test_default_ua_with_existing_headers(self, caplog):
        """测试 default_ua 与已有 headers 合并"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")
        default_ua = "MyBot/1.0"

        @requests_logger(default_ua=default_ua)
        def mock_request(method, url, headers=None, **kwargs):
            assert headers is not None
            assert headers["User-Agent"] == default_ua
            assert headers["X-Custom"] == "value"
            response = Mock()
            response.status_code = 200
            response.content = b"test"
            response.text = "test"
            return response

        mock_request("GET", "http://example.com", headers={"X-Custom": "value"})

    def test_default_ua_with_existing_user_agent_lowercase(self, caplog):
        """测试 headers 中已存在 user-agent (小写) 时不添加默认 UA"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")
        default_ua = "MyBot/1.0"
        existing_ua = "ExistingBot/1.0"

        @requests_logger(default_ua=default_ua)
        def mock_request(method, url, headers=None, **kwargs):
            assert headers is not None
            # 应该保留原有的 user-agent，不添加默认的
            assert headers["user-agent"] == existing_ua
            assert headers.get("User-Agent") != default_ua
            response = Mock()
            response.status_code = 200
            response.content = b"test"
            response.text = "test"
            return response

        mock_request("GET", "http://example.com", headers={"user-agent": existing_ua})

    def test_default_ua_with_existing_user_agent_uppercase(self, caplog):
        """测试 headers 中已存在 User-Agent (首字母大写) 时不添加默认 UA"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")
        default_ua = "MyBot/1.0"
        existing_ua = "ExistingBot/1.0"

        @requests_logger(default_ua=default_ua)
        def mock_request(method, url, headers=None, **kwargs):
            assert headers is not None
            # 应该保留原有的 User-Agent，不添加默认的
            assert headers["User-Agent"] == existing_ua
            response = Mock()
            response.status_code = 200
            response.content = b"test"
            response.text = "test"
            return response

        mock_request("GET", "http://example.com", headers={"User-Agent": existing_ua})

    def test_default_ua_with_existing_user_agent_all_uppercase(self, caplog):
        """测试 headers 中已存在 USER-AGENT (全大写) 时不添加默认 UA"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")
        default_ua = "MyBot/1.0"
        existing_ua = "ExistingBot/1.0"

        @requests_logger(default_ua=default_ua)
        def mock_request(method, url, headers=None, **kwargs):
            assert headers is not None
            # 应该保留原有的 USER-AGENT，不添加默认的
            assert headers["USER-AGENT"] == existing_ua
            assert headers.get("User-Agent") != default_ua
            response = Mock()
            response.status_code = 200
            response.content = b"test"
            response.text = "test"
            return response

        mock_request("GET", "http://example.com", headers={"USER-AGENT": existing_ua})

    def test_default_ua_with_existing_user_agent_mixed_case(self, caplog):
        """测试 headers 中已存在 User-AGeNt (混合大小写) 时不添加默认 UA"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")
        default_ua = "MyBot/1.0"
        existing_ua = "ExistingBot/1.0"

        @requests_logger(default_ua=default_ua)
        def mock_request(method, url, headers=None, **kwargs):
            assert headers is not None
            # 应该保留原有的 User-AGeNt，不添加默认的
            assert headers["User-AGeNt"] == existing_ua
            assert headers.get("User-Agent") != default_ua
            response = Mock()
            response.status_code = 200
            response.content = b"test"
            response.text = "test"
            return response

        mock_request("GET", "http://example.com", headers={"User-AGeNt": existing_ua})

    def test_default_ua_empty_no_headers(self, caplog):
        """测试 default_ua 为空时，没有 headers 的情况"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")

        @requests_logger(default_ua="")
        def mock_request(method, url, headers=None, **kwargs):
            assert headers is None
            response = Mock()
            response.status_code = 200
            response.content = b"test"
            response.text = "test"
            return response

        mock_request("GET", "http://example.com")

    def test_log_request_true_with_params(self, caplog):
        """测试 log_request=True 时记录 params"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")

        @requests_logger
        def mock_request(method, url, **kwargs):
            response = Mock()
            response.status_code = 200
            response.content = b"test"
            response.text = "test"
            return response

        mock_request("GET", "http://example.com", params={"key": "value"})
        assert len(caplog.records) == 1
        assert "params:" in caplog.records[0].message

    def test_log_request_true_with_data(self, caplog):
        """测试 log_request=True 时记录 data"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")

        @requests_logger
        def mock_request(method, url, **kwargs):
            response = Mock()
            response.status_code = 200
            response.content = b"test"
            response.text = "test"
            return response

        mock_request("POST", "http://example.com", data={"key": "value"})
        assert len(caplog.records) == 1
        assert "data:" in caplog.records[0].message

    def test_log_request_true_with_json(self, caplog):
        """测试 log_request=True 时记录 json"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")

        @requests_logger
        def mock_request(method, url, **kwargs):
            response = Mock()
            response.status_code = 200
            response.content = b"test"
            response.text = "test"
            return response

        mock_request("POST", "http://example.com", json={"key": "value", "中文": "测试"})
        assert len(caplog.records) == 1
        assert "json:" in caplog.records[0].message
        # 验证 JSON 格式化（ensure_ascii=False）
        assert "中文" in caplog.records[0].message

    def test_log_request_true_with_other_kwargs(self, caplog):
        """测试 log_request=True 时记录其他 kwargs"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")

        @requests_logger
        def mock_request(method, url, **kwargs):
            response = Mock()
            response.status_code = 200
            response.content = b"test"
            response.text = "test"
            return response

        mock_request("GET", "http://example.com", verify=False, stream=True)
        assert len(caplog.records) == 1
        assert "kwargs:" in caplog.records[0].message

    def test_log_request_false(self, caplog):
        """测试 log_request=False 时不记录请求信息"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")

        @requests_logger
        def mock_request(method, url, **kwargs):
            response = Mock()
            response.status_code = 200
            response.content = b"test"
            response.text = "test"
            return response

        mock_request("GET", "http://example.com", log_request=False, params={"key": "value"})
        assert len(caplog.records) == 1
        assert "request:" not in caplog.records[0].message

    def test_log_response_true_normal(self, caplog):
        """测试 log_response=True 时正常记录响应内容"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")

        @requests_logger
        def mock_request(method, url, **kwargs):
            response = Mock()
            response.status_code = 200
            response.content = b"test response"
            response.text = "test response"
            return response

        mock_request("GET", "http://example.com")
        assert len(caplog.records) == 1
        assert "response:" in caplog.records[0].message
        assert "test response" in caplog.records[0].message

    def test_log_response_true_with_exception(self, caplog):
        """测试 log_response=True 时 response.text 解析异常"""
        caplog.set_level(logging.DEBUG, "pykit_tools.requests")

        # 创建一个 Mock 对象，访问 text 属性时抛出异常
        @requests_logger
        def mock_request_simple(method, url, **kwargs):
            class ResponseWithTextError:
                def __init__(self):
                    self.status_code = 200
                    self.content = b"test"

                @property
                def text(self):
                    raise Exception("parse error")

            return ResponseWithTextError()

        mock_request_simple("GET", "http://example.com")
        assert len(caplog.records) == 1
        assert "response:" in caplog.records[0].message
        # 检查是否包含解析错误信息
        assert "parse response.text error" in caplog.records[0].message

    def test_log_response_false(self, caplog):
        """测试 log_response=False 时不记录响应内容"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")

        @requests_logger
        def mock_request(method, url, **kwargs):
            response = Mock()
            response.status_code = 200
            response.content = b"test"
            response.text = "test response"
            return response

        mock_request("GET", "http://example.com", log_response=False)
        assert len(caplog.records) == 1
        assert "response:" not in caplog.records[0].message

    def test_log_response_false_with_legal_codes_in_list(self, caplog):
        """测试 log_response=False + legal_codes 存在 + 状态码在 legal_codes 中时不记录响应"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")

        @requests_logger
        def mock_request(method, url, **kwargs):
            response = Mock()
            response.status_code = 200
            response.content = b"test"
            response.text = "test response"
            return response

        mock_request("GET", "http://example.com", log_response=False, legal_codes=[200, 201, 204])
        assert len(caplog.records) == 1
        assert "response:" not in caplog.records[0].message

    def test_log_response_false_with_legal_codes_not_in_list(self, caplog):
        """测试 log_response=False + legal_codes 存在 + 状态码不在 legal_codes 中时记录响应"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")

        @requests_logger
        def mock_request(method, url, **kwargs):
            response = Mock()
            response.status_code = 404
            response.content = b"not found"
            response.text = "not found"
            return response

        mock_request("GET", "http://example.com", log_response=False, legal_codes=[200, 201, 204])
        assert len(caplog.records) == 1
        assert "response:" in caplog.records[0].message
        assert "not found" in caplog.records[0].message

    def test_log_response_false_with_legal_codes_tuple(self, caplog):
        """测试 log_response=False + legal_codes 为元组 + 状态码不在 legal_codes 中时记录响应"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")

        @requests_logger
        def mock_request(method, url, **kwargs):
            response = Mock()
            response.status_code = 500
            response.content = b"server error"
            response.text = "server error"
            return response

        mock_request("GET", "http://example.com", log_response=False, legal_codes=(200, 201, 204))
        assert len(caplog.records) == 1
        assert "response:" in caplog.records[0].message
        assert "server error" in caplog.records[0].message

    def test_log_response_false_with_legal_codes_and_format_resp(self, caplog):
        """测试 log_response=False + legal_codes 存在 + 状态码不在 legal_codes 中 + format_resp 可调用时使用 format_resp"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")

        def custom_format(resp):
            return f"Formatted: {resp.status_code} - {resp.text}"

        @requests_logger
        def mock_request(method, url, **kwargs):
            response = Mock()
            response.status_code = 500
            response.content = b"error"
            response.text = "error"
            return response

        mock_request("GET", "http://example.com", log_response=False, legal_codes=[200, 201], format_resp=custom_format)
        assert len(caplog.records) == 1
        assert "response:" in caplog.records[0].message
        assert "Formatted: 500 - error" in caplog.records[0].message

    def test_log_response_false_with_legal_codes_and_format_resp_non_callable(self, caplog):
        """测试 log_response=False + legal_codes 存在 + 状态码不在 legal_codes 中 + format_resp 不可调用时使用 response.text"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")

        @requests_logger
        def mock_request(method, url, **kwargs):
            response = Mock()
            response.status_code = 500
            response.content = b"error"
            response.text = "error response"
            return response

        mock_request(
            "GET",
            "http://example.com",
            log_response=False,
            legal_codes=[200, 201],
            format_resp="not a function",  # 不可调用
        )
        assert len(caplog.records) == 1
        assert "response:" in caplog.records[0].message
        assert "error response" in caplog.records[0].message

    def test_log_response_false_with_legal_codes_and_format_resp_exception(self, caplog):
        """测试 log_response=False + legal_codes 存在 + 状态码不在 legal_codes 中 + format_resp 抛出异常"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")

        def format_resp_with_error(resp):
            raise ValueError("format error")

        @requests_logger
        def mock_request(method, url, **kwargs):
            response = Mock()
            response.status_code = 500
            response.content = b"error"
            response.text = "error"
            return response

        mock_request(
            "GET", "http://example.com", log_response=False, legal_codes=[200, 201], format_resp=format_resp_with_error
        )
        assert len(caplog.records) == 1
        assert "response:" in caplog.records[0].message
        assert "parse response.text error" in caplog.records[0].message

    def test_log_response_false_with_legal_codes_none(self, caplog):
        """测试 log_response=False + legal_codes=None 时不记录响应"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")

        @requests_logger
        def mock_request(method, url, **kwargs):
            response = Mock()
            response.status_code = 404
            response.content = b"not found"
            response.text = "not found"
            return response

        mock_request("GET", "http://example.com", log_response=False, legal_codes=None)
        assert len(caplog.records) == 1
        assert "response:" not in caplog.records[0].message

    def test_exception_no_raise_for(self, caplog):
        """测试异常时 raise_for=None 不抛出异常"""
        caplog.set_level(logging.ERROR, "pykit_tools.requests")

        @requests_logger
        def mock_request(method, url, **kwargs):
            raise ValueError("test error")

        result = mock_request("GET", "http://example.com", raise_for=None)
        assert result is None
        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "ERROR"
        assert "test error" in caplog.records[0].message

    def test_exception_raise_for_matched(self, caplog):
        """测试异常时 raise_for 匹配异常类型时抛出异常"""
        caplog.set_level(logging.ERROR, "pykit_tools.requests")

        @requests_logger
        def mock_request(method, url, **kwargs):
            raise ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            mock_request("GET", "http://example.com", raise_for=ValueError)
        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "ERROR"

    def test_exception_raise_for_tuple_matched(self, caplog):
        """测试异常时 raise_for 为元组且匹配时抛出异常"""
        caplog.set_level(logging.ERROR, "pykit_tools.requests")

        @requests_logger
        def mock_request(method, url, **kwargs):
            raise ValueError("test error")

        with pytest.raises(ValueError, match="test error"):
            mock_request("GET", "http://example.com", raise_for=(ValueError, TypeError))
        assert len(caplog.records) == 1

    def test_exception_raise_for_not_matched(self, caplog):
        """测试异常时 raise_for 不匹配异常类型时不抛出异常"""
        caplog.set_level(logging.ERROR, "pykit_tools.requests")

        @requests_logger
        def mock_request(method, url, **kwargs):
            raise ValueError("test error")

        result = mock_request("GET", "http://example.com", raise_for=TypeError)
        assert result is None
        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "ERROR"

    def test_logger_exception_on_error(self, caplog):
        """测试有错误时使用 logger.exception"""
        caplog.set_level(logging.ERROR, "pykit_tools.requests")

        @requests_logger
        def mock_request(method, url, **kwargs):
            raise ValueError("test error")

        mock_request("GET", "http://example.com")
        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "ERROR"

    def test_logger_info_on_success(self, caplog):
        """测试成功时使用 logger.info"""
        # err 初始化为 ""，如果没有异常，if err 为 False，会调用 logger.info
        caplog.set_level(logging.DEBUG, "pykit_tools.requests")

        @requests_logger
        def mock_request(method, url, **kwargs):
            response = Mock()
            response.status_code = 200
            response.content = b"test"
            response.text = "test"
            return response

        mock_request("GET", "http://example.com")
        assert len(caplog.records) == 1
        assert caplog.records[0].levelname == "INFO"
        assert "GET http://example.com" in caplog.records[0].message

    def test_timeout_parameter(self, caplog):
        """测试 timeout 参数传递"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")
        custom_timeout = 30

        @requests_logger
        def mock_request(method, url, timeout=10, **kwargs):
            assert timeout == custom_timeout
            response = Mock()
            response.status_code = 200
            response.content = b"test"
            response.text = "test"
            return response

        mock_request("GET", "http://example.com", timeout=custom_timeout)

    def test_response_status_code_and_length(self, caplog):
        """测试响应状态码和内容长度记录"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")

        @requests_logger
        def mock_request(method, url, **kwargs):
            response = Mock()
            response.status_code = 404
            response.content = b"not found" * 10
            response.text = "not found" * 10
            return response

        mock_request("GET", "http://example.com")
        assert len(caplog.records) == 1
        msg = caplog.records[0].message
        assert "404" in msg
        assert "90" in msg  # len(b"not found" * 10) = 90

    def test_cost_time_calculation(self, caplog):
        """测试耗时计算"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")

        @requests_logger
        def mock_request(method, url, **kwargs):
            import time

            time.sleep(0.1)  # 模拟耗时
            response = Mock()
            response.status_code = 200
            response.content = b"test"
            response.text = "test"
            return response

        mock_request("GET", "http://example.com")
        assert len(caplog.records) == 1
        msg = caplog.records[0].message
        # 验证耗时格式（应该包含毫秒，格式为 xxx.xxx）
        import re

        assert re.search(r"\d+\.\d{3}", msg) is not None

    def test_custom_logger_name(self, caplog):
        """测试自定义 logger_name"""
        custom_logger_name = "custom.requests"
        caplog.set_level(logging.INFO, custom_logger_name)

        @requests_logger(logger_name=custom_logger_name)
        def mock_request(method, url, **kwargs):
            response = Mock()
            response.status_code = 200
            response.content = b"test"
            response.text = "test"
            return response

        mock_request("GET", "http://example.com")
        assert len(caplog.records) == 1
        assert caplog.records[0].name == custom_logger_name

    def test_method_upper_case(self, caplog):
        """测试 HTTP 方法转大写"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")

        @requests_logger
        def mock_request(method, url, **kwargs):
            response = Mock()
            response.status_code = 200
            response.content = b"test"
            response.text = "test"
            return response

        mock_request("get", "http://example.com")
        assert len(caplog.records) == 1
        assert "GET http://example.com" in caplog.records[0].message

    def test_all_parameters_combined(self, caplog):
        """测试所有参数组合使用"""
        caplog.set_level(logging.DEBUG, "pykit_tools.requests")

        @requests_logger(default_ua="TestBot/1.0", logger_name="pykit_tools.requests")
        def mock_request(method, url, headers=None, timeout=10, **kwargs):
            assert headers is not None
            assert headers["User-Agent"] == "TestBot/1.0"
            assert timeout == 30
            response = Mock()
            response.status_code = 201
            response.content = b"created"
            response.text = "created"
            return response

        mock_request(
            "POST",
            "http://example.com",
            headers={"X-Custom": "value"},
            timeout=30,
            params={"key1": "value1"},
            json={"key2": "value2"},
            log_request=True,
            log_response=True,
        )
        assert len(caplog.records) == 1
        msg = caplog.records[0].message
        assert "POST http://example.com" in msg
        assert "201" in msg
        assert "params:" in msg
        assert "json:" in msg
        assert "response:" in msg

    def test_logger_info_when_exception_str_is_empty(self, caplog):
        """测试当异常字符串为空时使用 logger.info（覆盖 line 102）"""
        caplog.set_level(logging.DEBUG, "pykit_tools.requests")

        class EmptyStrException(Exception):
            """异常类，str 返回空字符串"""

            def __str__(self):
                return ""

        @requests_logger
        def mock_request(method, url, **kwargs):
            raise EmptyStrException()

        result = mock_request("GET", "http://example.com", raise_for=None)
        assert result is None
        assert len(caplog.records) == 1
        # 当 err = "" 时，if err 为 False，会执行 logger.info
        assert caplog.records[0].levelname == "INFO"
        assert "GET http://example.com" in caplog.records[0].message


class TestBaseRequest:
    """测试 BaseRequest 类的使用"""

    def test_base_request_init(self, caplog):
        """测试 BaseRequest 初始化"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")
        br = BaseRequest()
        assert br.request is not None

    def test_base_request_get(self, caplog, monkeypatch):
        """测试 BaseRequest.get 方法"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")

        def mock_request(method, url, **kwargs):
            response = Mock()
            response.status_code = 200
            response.content = b"test"
            response.text = "test"
            return response

        monkeypatch.setattr("requests.request", mock_request)
        br = BaseRequest()
        result = br.get("http://example.com")
        assert result.status_code == 200

    def test_base_request_post(self, caplog, monkeypatch):
        """测试 BaseRequest.post 方法"""
        caplog.set_level(logging.INFO, "pykit_tools.requests")

        def mock_request(method, url, **kwargs):
            response = Mock()
            response.status_code = 200
            response.content = b"test"
            response.text = "test"
            return response

        monkeypatch.setattr("requests.request", mock_request)
        br = BaseRequest()
        result = br.post("http://example.com", json={"key": "value"})
        assert result.status_code == 200
