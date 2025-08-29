"""
北京时间转换测试
"""
import pytest
from datetime import datetime, timezone, timedelta
from app.utils.response import DataFormatter


class TestBeijingTimezone:
    """北京时间转换测试类"""
    
    def test_utc_to_beijing_conversion(self):
        """测试UTC时间转换为北京时间"""
        # 2023-01-01 12:00:00 UTC 应该转换为 2023-01-01 20:00:00 北京时间
        utc_dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = DataFormatter.format_datetime(utc_dt)
        
        # 验证结果包含正确的日期和时间
        assert "2023-01-01T20:00:00" in result
        # 验证结果包含东八区时区信息
        assert "+08:00" in result
    
    def test_different_timezones(self):
        """测试不同时区的时间转换"""
        # 纽约时间 EST (UTC-5) 2023-01-01 07:00:00 应该转换为北京时间 2023-01-01 20:00:00
        est_dt = datetime(2023, 1, 1, 7, 0, 0, tzinfo=timezone(timedelta(hours=-5)))
        result = DataFormatter.format_datetime(est_dt)
        
        # 验证结果包含正确的日期和时间
        assert "2023-01-01T20:00:00" in result
        # 验证结果包含东八区时区信息
        assert "+08:00" in result
    
    def test_iso_string_conversion(self):
        """测试ISO字符串时间转换"""
        # UTC时间字符串
        iso_string = "2023-01-01T12:00:00Z"
        result = DataFormatter.format_datetime(iso_string)
        
        # 验证结果包含正确的日期和时间
        assert "2023-01-01T20:00:00" in result
        # 验证结果包含东八区时区信息
        assert "+08:00" in result
    
    def test_beijing_time_remains_unchanged(self):
        """测试已经是北京时间的时间"""
        # 北京时间 2023-01-01 20:00:00+08:00
        beijing_dt = datetime(2023, 1, 1, 20, 0, 0, tzinfo=timezone(timedelta(hours=8)))
        result = DataFormatter.format_datetime(beijing_dt)
        
        # 验证结果包含正确的日期和时间
        assert "2023-01-01T20:00:00" in result
        # 验证结果包含东八区时区信息
        assert "+08:00" in result

if __name__ == "__main__":
    pytest.main([__file__])