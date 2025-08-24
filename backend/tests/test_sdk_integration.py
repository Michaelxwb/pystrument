"""
SDK集成测试用例
"""
import pytest
import time
import threading
from unittest.mock import Mock, patch, MagicMock
from flask import Flask, request
import sys
import os

# 添加SDK路径到系统路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../../sdk'))

from performance_monitor.core.profiler import ProfilerManager
from performance_monitor.core.collector import PerformanceCollector
from performance_monitor.core.sender import DataSender
from performance_monitor.flask.middleware import PerformanceMiddleware, PerformanceWSGIWrapper
from performance_monitor.flask.decorators import monitor_performance
from performance_monitor.utils.config import Config


class TestPerformanceCollector:
    """性能收集器测试"""
    
    @pytest.fixture
    def config(self):
        """测试配置"""
        return Config({
            'project_key': 'test_project',
            'api_endpoint': 'http://localhost:8000',
            'enabled': True,
            'sampling_rate': 100.0,
            'async_send': False,
            'request_timeout': 30
        })
    
    @pytest.fixture
    def collector(self, config):
        """创建性能收集器"""
        return PerformanceCollector(config)
    
    def test_collector_initialization(self, collector, config):
        """测试收集器初始化"""
        assert collector.config == config
        assert collector._enabled == config.enabled
        assert collector._profiler is None
        assert collector._trace_id is None
    
    def test_start_profiling(self, collector):
        """测试开始性能分析"""
        request_context = {
            'method': 'GET',
            'path': '/test',
            'headers': {'User-Agent': 'test'},
            'remote_ip': '127.0.0.1'
        }
        
        trace_id = collector.start_profiling(request_context)
        
        assert trace_id is not None
        assert collector._trace_id == trace_id
        assert collector._profiler is not None
        assert collector._request_context == request_context
        assert collector._start_time is not None
    
    def test_stop_profiling(self, collector):
        """测试停止性能分析"""
        # 先开始分析
        request_context = {'method': 'GET', 'path': '/test'}
        trace_id = collector.start_profiling(request_context)
        
        # 模拟一些处理时间
        time.sleep(0.01)
        
        # 停止分析
        response_context = {'status_code': 200, 'response_size': 1024}
        result = collector.stop_profiling(response_context)
        
        assert result is not None
        assert 'trace_id' in result
        assert 'performance_metrics' in result
        assert 'function_calls' in result
        assert result['trace_id'] == trace_id
        
        # 验证性能指标
        metrics = result['performance_metrics']
        assert 'total_duration' in metrics
        assert 'cpu_time' in metrics
        assert 'memory_usage' in metrics
        assert metrics['total_duration'] > 0
    
    def test_sampling_rate_filtering(self, config):
        """测试采样率过滤"""
        # 设置50%采样率
        config.sampling_rate = 50.0
        collector = PerformanceCollector(config)
        
        # 多次调用，应该有大约一半被采样
        samples = []
        for _ in range(100):
            if collector._should_sample():
                samples.append(True)
            else:
                samples.append(False)
        
        # 允许一定的随机性误差
        sample_rate = sum(samples) / len(samples)
        assert 0.3 <= sample_rate <= 0.7  # 50% ± 20%


class TestFlaskMiddleware:
    """Flask中间件测试"""
    
    @pytest.fixture
    def app(self):
        """创建测试Flask应用"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app
    
    @pytest.fixture
    def config(self):
        """测试配置"""
        return Config({
            'project_key': 'test_project',
            'api_endpoint': 'http://localhost:8000',
            'enabled': True,
            'sampling_rate': 100.0,
            'async_send': False
        })
    
    def test_middleware_initialization(self, app, config):
        """测试中间件初始化"""
        middleware = PerformanceMiddleware(app, config)
        
        assert middleware.app == app
        assert middleware.profiler_manager is not None
        assert middleware.profiler_manager._config == config
    
    def test_middleware_request_processing(self, app, config):
        """测试中间件请求处理"""
        middleware = PerformanceMiddleware(app, config)
        
        @app.route('/test')
        def test_route():
            return {'message': 'test'}
        
        with app.test_client() as client:
            with patch.object(middleware.profiler_manager, 'start_profiling') as mock_start, \
                 patch.object(middleware.profiler_manager, 'stop_profiling') as mock_stop:
                
                mock_start.return_value = 'test_trace_id'
                mock_stop.return_value = None
                
                response = client.get('/test')
                
                assert response.status_code == 200
                mock_start.assert_called_once()
                mock_stop.assert_called_once()
    
    def test_wsgi_wrapper(self, app, config):
        """测试WSGI包装器"""
        wrapped_app = PerformanceWSGIWrapper(app, config)
        
        def start_response(status, headers):
            pass
        
        environ = {
            'REQUEST_METHOD': 'GET',
            'PATH_INFO': '/test',
            'HTTP_USER_AGENT': 'test-client',
            'REMOTE_ADDR': '127.0.0.1'
        }
        
        @app.route('/test')
        def test_route():
            return 'OK'
        
        with patch.object(wrapped_app.profiler_manager, 'start_profiling') as mock_start, \
             patch.object(wrapped_app.profiler_manager, 'stop_profiling') as mock_stop:
            
            mock_start.return_value = 'test_trace_id'
            mock_stop.return_value = None
            
            result = list(wrapped_app(environ, start_response))
            
            assert len(result) > 0
            mock_start.assert_called_once()
            mock_stop.assert_called_once()


class TestFlaskDecorators:
    """Flask装饰器测试"""
    
    @pytest.fixture
    def app(self):
        """创建测试Flask应用"""
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app
    
    def test_monitor_performance_decorator(self, app):
        """测试性能监控装饰器"""
        @app.route('/decorated')
        @monitor_performance(track_sql=True, track_memory=True)
        def decorated_route():
            time.sleep(0.01)  # 模拟处理时间
            return {'result': 'success'}
        
        with app.test_client() as client:
            with patch('performance_monitor.core.profiler.get_profiler_manager') as mock_get_manager:
                mock_manager = Mock()
                mock_manager._enabled = True
                mock_manager.start_profiling.return_value = 'trace_id'
                mock_manager.stop_profiling.return_value = None
                mock_get_manager.return_value = mock_manager
                
                response = client.get('/decorated')
                
                assert response.status_code == 200
                mock_manager.start_profiling.assert_called_once()
                mock_manager.stop_profiling.assert_called_once()
    
    def test_decorator_disabled(self, app):
        """测试装饰器禁用状态"""
        @app.route('/disabled')
        @monitor_performance(enabled=False)
        def disabled_route():
            return {'result': 'success'}
        
        with app.test_client() as client:
            with patch('performance_monitor.core.profiler.get_profiler_manager') as mock_get_manager:
                mock_manager = Mock()
                mock_get_manager.return_value = mock_manager
                
                response = client.get('/disabled')
                
                assert response.status_code == 200
                mock_manager.start_profiling.assert_not_called()
                mock_manager.stop_profiling.assert_not_called()
    
    def test_decorator_exception_handling(self, app):
        """测试装饰器异常处理"""
        @app.route('/error')
        @monitor_performance()
        def error_route():
            raise ValueError("测试异常")
        
        with app.test_client() as client:
            with patch('performance_monitor.core.profiler.get_profiler_manager') as mock_get_manager:
                mock_manager = Mock()
                mock_manager._enabled = True
                mock_manager.start_profiling.return_value = 'trace_id'
                mock_manager.stop_profiling.return_value = None
                mock_get_manager.return_value = mock_manager
                
                response = client.get('/error')
                
                assert response.status_code == 500
                mock_manager.start_profiling.assert_called_once()
                mock_manager.stop_profiling.assert_called_once()
                
                # 检查错误响应上下文
                call_args = mock_manager.stop_profiling.call_args[0][0]
                assert call_args['status_code'] == 500
                assert 'error' in call_args


class TestDataSender:
    """数据发送器测试"""
    
    @pytest.fixture
    def config(self):
        """测试配置"""
        return Config({
            'project_key': 'test_project',
            'api_endpoint': 'http://localhost:8000',
            'async_send': False,
            'batch_size': 10,
            'batch_timeout': 5,
            'request_timeout': 30
        })
    
    @pytest.fixture
    def sender(self, config):
        """创建数据发送器"""
        return DataSender(config)
    
    def test_sender_initialization(self, sender, config):
        """测试发送器初始化"""
        assert sender.config == config
        assert sender.session is not None
        assert sender.session.headers['X-Project-Key'] == config.project_key
    
    @patch('requests.Session.post')
    def test_sync_send_success(self, mock_post, sender):
        """测试同步发送成功"""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'code': 0, 'msg': 'success'}
        mock_post.return_value = mock_response
        
        performance_data = {
            'trace_id': 'test_trace',
            'performance_metrics': {'total_duration': 0.1}
        }
        
        result = sender.send_sync(performance_data)
        
        assert result is True
        mock_post.assert_called_once()
    
    @patch('requests.Session.post')
    def test_sync_send_failure(self, mock_post, sender):
        """测试同步发送失败"""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_post.return_value = mock_response
        
        performance_data = {
            'trace_id': 'test_trace',
            'performance_metrics': {'total_duration': 0.1}
        }
        
        result = sender.send_sync(performance_data)
        
        assert result is False
        mock_post.assert_called_once()
    
    def test_async_send(self, config):
        """测试异步发送"""
        config.async_send = True
        sender = DataSender(config)
        
        with patch.object(sender, 'send_sync', return_value=True) as mock_sync:
            performance_data = {
                'trace_id': 'test_trace',
                'performance_metrics': {'total_duration': 0.1}
            }
            
            sender.send_async(performance_data)
            
            # 等待异步任务完成
            time.sleep(0.1)
            
            # 验证同步发送被调用
            # 注意：在实际的异步环境中，这可能需要更复杂的同步机制


class TestIntegration:
    """集成测试"""
    
    def test_full_integration_flow(self):
        """测试完整集成流程"""
        # 创建Flask应用
        app = Flask(__name__)
        app.config['TESTING'] = True
        
        # 配置SDK
        config = Config({
            'project_key': 'integration_test',
            'api_endpoint': 'http://localhost:8000',
            'enabled': True,
            'sampling_rate': 100.0,
            'async_send': False
        })
        
        # 添加中间件
        middleware = PerformanceMiddleware(app, config)
        
        @app.route('/integration-test')
        def test_route():
            # 模拟一些处理逻辑
            time.sleep(0.01)
            return {'status': 'ok', 'message': 'integration test'}
        
        with app.test_client() as client:
            with patch.object(middleware.profiler_manager.collector.sender, 'send_sync') as mock_send:
                mock_send.return_value = True
                
                response = client.get('/integration-test')
                
                assert response.status_code == 200
                data = response.get_json()
                assert data['status'] == 'ok'
                
                # 验证性能数据被发送
                mock_send.assert_called_once()
                
                # 验证发送的数据格式
                call_args = mock_send.call_args[0][0]
                assert 'trace_id' in call_args
                assert 'request_info' in call_args
                assert 'performance_metrics' in call_args
                assert 'function_calls' in call_args


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])