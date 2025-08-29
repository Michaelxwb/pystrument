"""
时间格式化一致性测试
测试所有时间字段都按照东八区进行转换
"""
import pytest
from datetime import datetime, timezone, timedelta
from app.utils.response import DataFormatter


class TestTimeFormattingConsistency:
    """时间格式化一致性测试类"""
    
    def test_data_formatter_consistency(self):
        """测试DataFormatter.format_datetime的一致性"""
        # 测试UTC时间
        utc_dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        result = DataFormatter.format_datetime(utc_dt)
        assert "+08:00" in result
        assert "2023-01-01T20:00:00" in result  # UTC+8
        
        # 测试不同时区的时间
        est_dt = datetime(2023, 1, 1, 7, 0, 0, tzinfo=timezone(timedelta(hours=-5)))
        result = DataFormatter.format_datetime(est_dt)
        assert "+08:00" in result
        assert "2023-01-01T20:00:00" in result  # EST+13 = UTC+8
        
        # 测试ISO字符串
        iso_string = "2023-01-01T12:00:00Z"
        result = DataFormatter.format_datetime(iso_string)
        assert "+08:00" in result
        assert "2023-01-01T20:00:00" in result
    
    def test_edge_cases(self):
        """测试边界情况"""
        # 测试None值
        result = DataFormatter.format_datetime(None)
        assert result is None
        
        # 测试无效字符串
        result = DataFormatter.format_datetime("invalid")
        assert result == "invalid"
        
        # 测试普通字符串 - 现在会被解析并转换为东八区时间
        result = DataFormatter.format_datetime("2023-01-01")
        assert "+08:00" in result  # 确保包含时区信息
        
        # 测试普通字符串（带时间）
        result = DataFormatter.format_datetime("2023-01-01 12:00:00")
        assert "+08:00" in result  # 确保包含时区信息
    
    def test_timezone_conversion_across_date_boundary(self):
        """测试跨日期边界的时区转换"""
        # UTC时间 2023-01-01 07:00:00 转换为北京时间应该是 2023-01-01 15:00:00
        utc_dt = datetime(2023, 1, 1, 7, 0, 0, tzinfo=timezone.utc)
        result = DataFormatter.format_datetime(utc_dt)
        assert "2023-01-01T15:00:00" in result
        
        # UTC时间 2023-01-01 20:00:00 转换为北京时间应该是 2023-01-02 04:00:00
        utc_dt = datetime(2023, 1, 1, 20, 0, 0, tzinfo=timezone.utc)
        result = DataFormatter.format_datetime(utc_dt)
        assert "2023-01-02T04:00:00" in result

if __name__ == "__main__":
    pytest.main([__file__])