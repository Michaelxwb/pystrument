"""
性能数据收集和分析测试用例
"""
import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock
from datetime import datetime, timedelta

from app.services.ai_analyzer import PerformanceAnalyzer
from app.models.analysis import AnalysisResults, BottleneckAnalysis, OptimizationSuggestion, RiskAssessment


class TestPerformanceAnalyzer:
    """性能分析器测试类"""
    
    @pytest.fixture
    def analyzer(self):
        """创建性能分析器实例"""
        return PerformanceAnalyzer()
    
    @pytest.fixture
    def sample_performance_data(self):
        """示例性能数据"""
        return {
            "request_info": {
                "path": "/api/users",
                "method": "GET",
                "headers": {"User-Agent": "test-client"},
                "remote_ip": "127.0.0.1"
            },
            "response_info": {
                "status_code": 200,
                "response_size": 1024,
                "content_type": "application/json"
            },
            "performance_metrics": {
                "total_duration": 1.5,  # 1.5秒
                "cpu_time": 0.8,
                "memory_usage": {
                    "start_memory": 50,
                    "peak_memory": 120  # MB
                }
            },
            "function_calls": [
                {
                    "id": "call_1",
                    "function_name": "get_users",
                    "file_path": "/app/api/users.py",
                    "line_number": 25,
                    "duration": 0.8,
                    "depth": 0
                },
                {
                    "id": "call_2", 
                    "function_name": "db_query",
                    "file_path": "/app/db/query.py",
                    "line_number": 45,
                    "duration": 0.6,
                    "depth": 1
                },
                {
                    "id": "call_3",
                    "function_name": "sql_execute",
                    "file_path": "/app/db/sql.py", 
                    "line_number": 120,
                    "duration": 0.5,
                    "depth": 2
                }
            ],
            "environment": {
                "python_version": "3.9.6",
                "framework_version": "Flask 2.0.1",
                "platform": "Linux-5.4.0",
                "hostname": "test-server"
            }
        }
    
    @pytest.mark.asyncio
    async def test_preprocess_performance_data(self, analyzer, sample_performance_data):
        """测试性能数据预处理"""
        processed = analyzer._preprocess_performance_data(sample_performance_data)
        
        # 检查基本信息
        assert processed["basic_info"]["request_path"] == "/api/users"
        assert processed["basic_info"]["request_method"] == "GET"
        assert processed["basic_info"]["status_code"] == 200
        
        # 检查性能汇总
        assert processed["performance_summary"]["total_duration"] == 1.5
        assert processed["performance_summary"]["cpu_time"] == 0.8
        assert processed["performance_summary"]["memory_peak"] == 120
        assert processed["performance_summary"]["function_count"] == 3
        assert processed["performance_summary"]["slow_function_count"] == 2  # duration > 0.1
        
        # 检查慢函数识别
        slow_functions = processed["slow_functions"]
        assert len(slow_functions) == 2
        assert slow_functions[0]["function_name"] == "get_users"  # 最慢的函数
        assert slow_functions[0]["duration"] == 0.8
    
    def test_analyze_call_patterns(self, analyzer):
        """测试函数调用模式分析"""
        function_calls = [
            {"function_name": "db_query", "file_path": "/app/db.py", "duration": 0.3, "depth": 1},
            {"function_name": "db_query", "file_path": "/app/db.py", "duration": 0.2, "depth": 1},
            {"function_name": "sql_execute", "file_path": "/app/sql.py", "duration": 0.4, "depth": 2},
            {"function_name": "file_read", "file_path": "/app/io.py", "duration": 0.1, "depth": 1},
            {"function_name": "compute_hash", "file_path": "/app/utils.py", "duration": 0.08, "depth": 1}
        ]
        
        patterns = analyzer._analyze_call_patterns(function_calls)
        
        # 检查数据库调用统计
        assert patterns["database_calls"] == 2  # db_query 和 sql_execute
        
        # 检查I/O操作统计
        assert patterns["io_operations"] == 1  # file_read
        
        # 检查计算密集型操作
        assert patterns["computation_heavy"] == 3  # duration > 0.05
        
        # 检查热点路径
        hot_paths = patterns["hot_paths"]
        assert len(hot_paths) > 0
        assert hot_paths[0]["function"] == "db_query"
        assert hot_paths[0]["calls"] == 2
    
    def test_identify_bottleneck_types(self, analyzer):
        """测试瓶颈类型识别"""
        function_calls = [
            {"function_name": "sql_query", "file_path": "/app/db.py", "duration": 0.8},
            {"function_name": "database_fetch", "file_path": "/app/orm.py", "duration": 0.3}
        ]
        performance_metrics = {
            "total_duration": 2.0,
            "cpu_time": 0.3,
            "memory_usage": {"peak_memory": 800}
        }
        
        bottlenecks = analyzer._identify_bottleneck_types(function_calls, performance_metrics)
        
        # 应该识别出数据库瓶颈
        db_bottleneck = next((b for b in bottlenecks if b["type"] == "database"), None)
        assert db_bottleneck is not None
        assert db_bottleneck["severity"] == "high"  # 数据库时间超过50%
        
        # 应该识别出I/O瓶颈
        io_bottleneck = next((b for b in bottlenecks if b["type"] == "io"), None)
        assert io_bottleneck is not None
        
        # 应该识别出内存瓶颈
        memory_bottleneck = next((b for b in bottlenecks if b["type"] == "memory"), None)
        assert memory_bottleneck is not None
    
    @pytest.mark.asyncio
    async def test_analyze_with_fallback(self, analyzer, sample_performance_data):
        """测试回退分析功能"""
        processed_data = analyzer._preprocess_performance_data(sample_performance_data)
        
        result = await analyzer._analyze_with_fallback(processed_data)
        
        # 检查返回结果类型
        assert isinstance(result, AnalysisResults)
        assert isinstance(result.performance_score, float)
        assert isinstance(result.bottleneck_analysis, list)
        assert isinstance(result.optimization_suggestions, list)
        assert isinstance(result.risk_assessment, RiskAssessment)
        
        # 检查性能评分
        assert 0 <= result.performance_score <= 100
        
        # 由于响应时间为1.5秒，评分应该较低
        assert result.performance_score < 70
    
    def test_calculate_performance_score(self, analyzer):
        """测试性能评分计算"""
        # 优秀性能
        excellent_summary = {
            "total_duration": 0.05,  # 50ms
            "memory_peak": 30,       # 30MB
            "cpu_utilization": 0.3   # 30%
        }
        score = analyzer._calculate_performance_score(excellent_summary)
        assert score >= 90
        
        # 较差性能
        poor_summary = {
            "total_duration": 3.0,   # 3秒
            "memory_peak": 800,      # 800MB
            "cpu_utilization": 0.95  # 95%
        }
        score = analyzer._calculate_performance_score(poor_summary)
        assert score <= 40
    
    def test_generate_fallback_suggestions(self, analyzer):
        """测试回退优化建议生成"""
        performance_summary = {
            "total_duration": 3.0,  # 慢响应
            "memory_peak": 600
        }
        bottleneck_types = [
            {"type": "database", "severity": "high", "impact": 0.7},
            {"type": "memory", "severity": "medium", "impact": 0.3}
        ]
        
        suggestions = analyzer._generate_fallback_suggestions(performance_summary, bottleneck_types)
        
        # 应该生成响应时间优化建议
        response_suggestion = next((s for s in suggestions if "响应时间" in s.title), None)
        assert response_suggestion is not None
        assert response_suggestion.priority == "high"
        
        # 应该生成数据库优化建议
        db_suggestion = next((s for s in suggestions if s.category == "database"), None)
        assert db_suggestion is not None
        assert "索引" in db_suggestion.description or "SQL" in db_suggestion.description
        
        # 应该生成内存优化建议
        memory_suggestion = next((s for s in suggestions if s.category == "memory"), None)
        assert memory_suggestion is not None
    
    def test_generate_fallback_risks(self, analyzer):
        """测试回退风险评估生成"""
        performance_summary = {
            "total_duration": 6.0,   # 很慢
            "memory_peak": 1200      # 高内存使用
        }
        
        risk_assessment = analyzer._generate_fallback_risks(performance_summary)
        
        # 应该识别当前风险
        assert len(risk_assessment.current_risks) > 0
        assert any("响应时间" in risk for risk in risk_assessment.current_risks)
        assert any("内存" in risk for risk in risk_assessment.current_risks)
        
        # 应该有建议措施
        assert len(risk_assessment.recommendations) > 0


class TestPerformanceDataIntegration:
    """性能数据集成测试"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_analysis(self):
        """测试端到端性能分析流程"""
        # 模拟完整的分析流程
        analyzer = PerformanceAnalyzer()
        
        # 构造测试数据
        performance_data = {
            "request_info": {"path": "/api/slow-endpoint", "method": "POST"},
            "response_info": {"status_code": 200},
            "performance_metrics": {
                "total_duration": 2.5,
                "cpu_time": 1.8,
                "memory_usage": {"start_memory": 100, "peak_memory": 400}
            },
            "function_calls": [
                {"function_name": "slow_function", "duration": 1.5, "depth": 0},
                {"function_name": "db_heavy_query", "duration": 1.0, "depth": 1},
                {"function_name": "memory_intensive", "duration": 0.8, "depth": 1}
            ]
        }
        
        # 执行分析
        result = await analyzer.analyze_performance(performance_data)
        
        # 验证结果
        assert isinstance(result, AnalysisResults)
        assert result.performance_score < 60  # 性能较差
        assert len(result.bottleneck_analysis) > 0
        assert len(result.optimization_suggestions) > 0
        
        # 验证瓶颈分析
        has_performance_bottleneck = any(
            b.type in ["database", "computation", "memory"] 
            for b in result.bottleneck_analysis
        )
        assert has_performance_bottleneck
        
        # 验证优化建议
        has_high_priority_suggestion = any(
            s.priority == "high" 
            for s in result.optimization_suggestions
        )
        assert has_high_priority_suggestion
    
    @pytest.mark.asyncio
    async def test_analysis_error_handling(self):
        """测试分析错误处理"""
        analyzer = PerformanceAnalyzer()
        
        # 测试空数据
        empty_data = {}
        result = await analyzer.analyze_performance(empty_data)
        assert isinstance(result, AnalysisResults)
        assert result.performance_score == 50.0  # 默认评分
        
        # 测试无效数据格式
        invalid_data = {"invalid": "format"}
        result = await analyzer.analyze_performance(invalid_data)
        assert isinstance(result, AnalysisResults)


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])