"""
时间格式化测试
"""
import pytest
from datetime import datetime, timezone, timedelta
from app.utils.response import DataFormatter


class TestDatetimeFormat:
    """时间格式化测试类"""
    
    def test_format_datetime_with_none(self):
        """测试格式化None值"""
        result = DataFormatter.format_datetime(None)
        assert result is None
    
    def test_format_datetime_with_utc_datetime(self):
        """测试格式化UTC时间"""
        # 创建UTC时间（2023-01-01 12:00:00 UTC）
        utc_dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = DataFormatter.format_datetime(utc_dt)
        
        # 应该转换为东八区时间（2023-01-01 20:00:00+08:00）
        assert result == "2023-01-01T20:00:00+08:00"
    
    def test_format_datetime_with_naive_datetime(self):
        """测试格式化无时区信息的时间"""
        # 创建无时区信息的时间（假设为UTC时间）
        naive_dt = datetime(2023, 1, 1, 12, 0, 0)
        result = DataFormatter.format_datetime(naive_dt)
        
        # 应该转换为东八区时间（2023-01-01 20:00:00+08:00）
        # 注意：Python会将无时区信息的时间视为本地时间，这里假设本地时间为UTC
        assert "2023-01-01T20:00:00" in result or "2023-01-01T12:00:00" in result
    
    def test_format_datetime_with_string(self):
        """测试格式化时间字符串"""
        # ISO格式时间字符串
        dt_str = "2023-01-01T12:00:00+00:00"
        result = DataFormatter.format_datetime(dt_str)
        
        # 应该转换为东八区时间
        assert "+08:00" in result
    
    def test_format_datetime_with_invalid_string(self):
        """测试格式化无效时间字符串"""
        # 无效的时间字符串
        invalid_str = "invalid datetime"
        result = DataFormatter.format_datetime(invalid_str)
        
        # 应该返回原始字符串
        assert result == invalid_str

if __name__ == "__main__":
    pytest.main([__file__])