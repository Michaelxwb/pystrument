"""
Django应用性能监控支持
"""

class PerformanceMiddleware:
    """Django性能监控中间件（占位符）"""
    
    def __init__(self, get_response=None, **kwargs):
        self.get_response = get_response
        
    def __call__(self, request):
        response = self.get_response(request)
        return response