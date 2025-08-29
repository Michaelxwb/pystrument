"""
AI分析算法实现
"""
import json
import asyncio
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

from app.services.ai_config import ai_config_manager, AIProvider, AIServiceConfig
from app.models.analysis import AnalysisResults, BottleneckAnalysis, OptimizationSuggestion, RiskAssessment

logger = logging.getLogger(__name__)


class PerformanceAnalyzer:
    """性能分析器"""
    
    def __init__(self):
        self.config_manager = ai_config_manager
    
    async def analyze_performance(
        self,
        performance_data: Dict[str, Any],
        ai_service: str = None
    ) -> AnalysisResults:
        """分析性能数据"""
        try:
            # 获取AI服务配置
            service_config = self.config_manager.get_service(ai_service)
            if not service_config or not service_config.enabled:
                raise ValueError(f"AI服务 '{ai_service}' 不可用")
            
            # 预处理性能数据
            processed_data = self._preprocess_performance_data(performance_data)
            
            # 调用对应的AI服务
            if service_config.provider == AIProvider.OPENAI:
                return await self._analyze_with_openai(processed_data, service_config)
            elif service_config.provider == AIProvider.ALIYUN_QIANWEN:
                return await self._analyze_with_qianwen(processed_data, service_config)
            elif service_config.provider == AIProvider.CUSTOM:
                return await self._analyze_with_custom_ai(processed_data, service_config)
            else:
                return await self._analyze_with_fallback(processed_data)
                
        except Exception as e:
            logger.error(f"性能分析失败: {str(e)}")
            # 返回基础分析结果
            return await self._analyze_with_fallback(performance_data)
    
    def _preprocess_performance_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """预处理性能数据"""
        try:
            performance_metrics = data.get("performance_metrics", {})
            function_calls = data.get("function_calls", [])
            request_info = data.get("request_info", {})
            
            # 计算关键指标
            total_duration = performance_metrics.get("total_duration", 0)
            cpu_time = performance_metrics.get("cpu_time", 0)
            memory_peak = performance_metrics.get("memory_usage", {}).get("peak_memory", 0)
            
            # 识别慢函数
            slow_functions = [
                fc for fc in function_calls 
                if fc.get("duration", 0) > 0.1  # 大于100ms
            ]
            slow_functions.sort(key=lambda x: x.get("duration", 0), reverse=True)
            
            # 分析函数调用模式
            call_patterns = self._analyze_call_patterns(function_calls)
            
            # 识别瓶颈类型
            bottleneck_types = self._identify_bottleneck_types(function_calls, performance_metrics)
            
            return {
                "basic_info": {
                    "request_path": request_info.get("path", ""),
                    "request_method": request_info.get("method", ""),
                    "status_code": data.get("response_info", {}).get("status_code", 200),
                    "framework": data.get("environment", {}).get("framework_version", "")
                },
                "performance_summary": {
                    "total_duration": total_duration,
                    "cpu_time": cpu_time,
                    "memory_peak": memory_peak,
                    "function_count": len(function_calls),
                    "slow_function_count": len(slow_functions),
                    "cpu_utilization": cpu_time / total_duration if total_duration > 0 else 0
                },
                "slow_functions": slow_functions[:10],  # 取前10个最慢的函数
                "call_patterns": call_patterns,
                "bottleneck_types": bottleneck_types,
                "raw_data": data
            }
            
        except Exception as e:
            logger.error(f"预处理性能数据失败: {str(e)}")
            return {"raw_data": data}
    
    def _analyze_call_patterns(self, function_calls: List[Dict[str, Any]]) -> Dict[str, Any]:
        """分析函数调用模式"""
        patterns = {
            "recursion_detected": False,
            "deep_nesting": False,
            "hot_paths": [],
            "database_calls": 0,
            "io_operations": 0,
            "computation_heavy": 0
        }
        
        try:
            # 检测递归调用
            function_names = [fc.get("function_name", "") for fc in function_calls]
            function_counts = {}
            for name in function_names:
                function_counts[name] = function_counts.get(name, 0) + 1
            
            patterns["recursion_detected"] = any(count > 5 for count in function_counts.values())
            
            # 检测深层嵌套
            max_depth = max((fc.get("depth", 0) for fc in function_calls), default=0)
            patterns["deep_nesting"] = max_depth > 10
            
            # 识别热点路径
            hot_functions = sorted(
                function_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            patterns["hot_paths"] = [{"function": name, "calls": count} for name, count in hot_functions]
            
            # 分类函数调用
            for fc in function_calls:
                func_name = fc.get("function_name", "").lower()
                file_path = fc.get("file_path", "").lower()
                
                if any(keyword in func_name or keyword in file_path 
                       for keyword in ["sql", "query", "database", "db", "orm"]):
                    patterns["database_calls"] += 1
                elif any(keyword in func_name or keyword in file_path 
                         for keyword in ["read", "write", "file", "io", "request", "http"]):
                    patterns["io_operations"] += 1
                elif fc.get("duration", 0) > 0.05:  # 大于50ms的计算
                    patterns["computation_heavy"] += 1
            
            return patterns
            
        except Exception as e:
            logger.error(f"分析调用模式失败: {str(e)}")
            return patterns
    
    def _identify_bottleneck_types(
        self, 
        function_calls: List[Dict[str, Any]], 
        performance_metrics: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """识别瓶颈类型"""
        bottlenecks = []
        
        try:
            total_duration = performance_metrics.get("total_duration", 0)
            cpu_time = performance_metrics.get("cpu_time", 0)
            
            # 数据库瓶颈
            db_time = sum(
                fc.get("duration", 0) for fc in function_calls
                if any(keyword in fc.get("function_name", "").lower() 
                       for keyword in ["sql", "query", "database"])
            )
            if db_time > total_duration * 0.3:  # 数据库时间超过30%
                bottlenecks.append({
                    "type": "database",
                    "severity": "high" if db_time > total_duration * 0.5 else "medium",
                    "impact": db_time / total_duration,
                    "description": f"数据库操作耗时{db_time:.3f}秒，占总时间的{db_time/total_duration*100:.1f}%"
                })
            
            # CPU密集型瓶颈
            if cpu_time > total_duration * 0.8:  # CPU时间超过80%
                bottlenecks.append({
                    "type": "computation",
                    "severity": "medium",
                    "impact": cpu_time / total_duration,
                    "description": f"CPU密集型操作，CPU时间占{cpu_time/total_duration*100:.1f}%"
                })
            
            # I/O瓶颈
            io_time = total_duration - cpu_time
            if io_time > total_duration * 0.4:  # I/O等待时间超过40%
                bottlenecks.append({
                    "type": "io",
                    "severity": "medium",
                    "impact": io_time / total_duration,
                    "description": f"I/O等待时间过长，占总时间的{io_time/total_duration*100:.1f}%"
                })
            
            # 内存瓶颈
            memory_peak = performance_metrics.get("memory_usage", {}).get("peak_memory", 0)
            if memory_peak > 500:  # 内存使用超过500MB
                bottlenecks.append({
                    "type": "memory",
                    "severity": "high" if memory_peak > 1000 else "medium",
                    "impact": min(memory_peak / 1000, 1.0),
                    "description": f"内存使用过高，峰值达到{memory_peak}MB"
                })
            
            return bottlenecks
            
        except Exception as e:
            logger.error(f"识别瓶颈类型失败: {str(e)}")
            return []
    
    async def _analyze_with_openai(
        self, 
        processed_data: Dict[str, Any], 
        service_config
    ) -> AnalysisResults:
        """使用OpenAI进行分析"""
        try:
            import openai
            
            # 构建分析提示
            prompt = self._build_analysis_prompt(processed_data)
            
            # 调用OpenAI API
            client = openai.AsyncOpenAI(api_key=service_config.api_key)
            
            response = await client.chat.completions.create(
                model=service_config.model,
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的Python性能分析专家。请分析给定的性能数据，识别瓶颈并提供优化建议。返回结构化的JSON格式结果。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=service_config.temperature,
                max_tokens=service_config.max_tokens,
                timeout=service_config.timeout
            )
            
            # 解析AI响应
            ai_response = response.choices[0].message.content
            
            # 尝试解析为JSON
            try:
                parsed_result = json.loads(ai_response)
                return self._parse_ai_result(parsed_result, processed_data)
            except json.JSONDecodeError:
                # 如果无法解析为JSON，使用文本解析
                return self._parse_text_result(ai_response, processed_data)
                
        except Exception as e:
            logger.error(f"OpenAI分析失败: {str(e)}")
            return await self._analyze_with_fallback(processed_data)
    
    async def _analyze_with_custom_ai(
        self, 
        processed_data: Dict[str, Any], 
        service_config
    ) -> AnalysisResults:
        """使用自定义AI服务进行分析"""
        try:
            import aiohttp
            
            # 构建请求数据
            request_data = {
                "performance_data": processed_data,
                "analysis_type": "performance_bottleneck",
                "options": {
                    "include_suggestions": True,
                    "include_risk_assessment": True
                }
            }
            
            # 调用自定义AI服务
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    service_config.endpoint,
                    json=request_data,
                    headers=service_config.headers,
                    timeout=aiohttp.ClientTimeout(total=service_config.timeout)
                ) as response:
                    
                    if response.status == 200:
                        result = await response.json()
                        return self._parse_custom_ai_result(result, processed_data)
                    else:
                        logger.error(f"自定义AI服务返回错误: {response.status}")
                        return await self._analyze_with_fallback(processed_data)
                        
        except Exception as e:
            logger.error(f"自定义AI分析失败: {str(e)}")
            return await self._analyze_with_fallback(processed_data)

    async def _analyze_with_qianwen(self, processed_data: Dict[str, Any], service_config: AIServiceConfig) -> AnalysisResults:
        """使用阿里千问进行分析"""
        try:
            import httpx
            import json
            from tenacity import retry, stop_after_attempt, wait_exponential
            
            # 构建提示语
            prompt = self._build_analysis_prompt(processed_data)
            
            # 准备请求体
            request_data = {
                "model": service_config.model,
                "input": {
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一个专业的性能分析师，专注于Python Web应用的性能分析与优化。请分析用户提供的性能数据，并提供结构化的分析结果。"
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                },
                "parameters": {
                    "max_tokens": service_config.max_tokens,
                    "temperature": service_config.temperature,
                    "result_format": "json"
                }
            }
            
            # 防止网络问题，使用 tenacity 进行重试
            @retry(stop=stop_after_attempt(service_config.max_retries), 
                  wait=wait_exponential(multiplier=1, min=1, max=10))
            async def call_qianwen_api():
                async with httpx.AsyncClient(timeout=service_config.timeout) as client:
                    response = await client.post(
                        service_config.endpoint,
                        json=request_data,
                        headers=service_config.headers
                    )
                    response.raise_for_status()
                    return response.json()
        
            # 调用API
            logger.info(f"调用阿里千问 API: {service_config.endpoint}")
            api_response = await call_qianwen_api()
            
            # 处理响应
            content = None
            # 首先尝试从output.choices获取内容（OpenAI格式）
            if 'output' in api_response and 'choices' in api_response['output']:
                content = api_response['output']['choices'][0]['message']['content']
            # 然后尝试从output.text获取内容（阿里千问格式）
            elif 'output' in api_response and 'text' in api_response['output']:
                content = api_response['output']['text']
            
            if content:
                # 尝试解析JSON结构
                try:
                    # 处理不同的JSON格式
                    if content.startswith('```json') and content.endswith('```'):
                        # 从代码块中提取 JSON
                        json_str = content.replace('```json', '').replace('```', '').strip()
                        result_json = json.loads(json_str)
                    elif content.strip().startswith('{') and content.strip().endswith('}'):
                        # 直接是JSON对象
                        result_json = json.loads(content.strip())
                    else:
                        # 尝试直接解析
                        result_json = json.loads(content)
                    
                    # 解析完整的分析结果
                    performance_score = float(result_json.get('performance_score', 70))
                    
                    # 解析瓶颈分析
                    bottlenecks = []
                    for bottleneck in result_json.get('bottlenecks', []):
                        bottlenecks.append(BottleneckAnalysis(
                            type=bottleneck.get('type', 'unknown'),
                            severity=bottleneck.get('severity', 'medium'),
                            function=bottleneck.get('function', 'system'),
                            description=bottleneck.get('description', ''),
                            impact=float(bottleneck.get('impact', 0.5)) if isinstance(bottleneck.get('impact'), (int, float)) else 0.5
                        ))
                    
                    # 解析优化建议
                    suggestions = []
                    for suggestion in result_json.get('suggestions', []):
                        suggestions.append(OptimizationSuggestion(
                            category=suggestion.get('category', 'performance'),
                            priority=suggestion.get('priority', 'medium'),
                            title=suggestion.get('title', ''),
                            description=suggestion.get('description', ''),
                            code_example=suggestion.get('code_example', ''),
                            expected_improvement=suggestion.get('expected_improvement', '')
                        ))
                    
                    # 解析风险评估
                    risks = RiskAssessment(
                        current_risks=result_json.get('risks', {}).get('current_risks', []),
                        potential_issues=result_json.get('risks', {}).get('potential_issues', []),
                        recommendations=result_json.get('risks', {}).get('recommendations', [])
                    )
                    
                    return AnalysisResults(
                        performance_score=performance_score,
                        bottleneck_analysis=bottlenecks,
                        optimization_suggestions=suggestions,
                        risk_assessment=risks
                    )
                except json.JSONDecodeError:
                    # 结果不是JSON格式，采用文本解析
                    logger.warning("千问响应不是JSON格式，尝试用文本解析")
                    return self._parse_text_result(content, processed_data)
            
            # 处理异常情况
            logger.error(f"千问响应格式异常: {api_response}")
            return await self._analyze_with_fallback(processed_data)
            
        except Exception as e:
            logger.error(f"使用阿里千问分析失败: {str(e)}")
            return await self._analyze_with_fallback(processed_data)

    async def _analyze_with_fallback(self, data: Dict[str, Any]) -> AnalysisResults:
        """基于规则的回退分析"""
        try:
            performance_summary = data.get("performance_summary", {})
            bottleneck_types = data.get("bottleneck_types", [])
            
            total_duration = performance_summary.get("total_duration", 0)
            
            # 计算性能评分
            performance_score = self._calculate_performance_score(performance_summary)
            
            # 生成瓶颈分析
            bottleneck_analysis = []
            for bt in bottleneck_types:
                bottleneck_analysis.append(BottleneckAnalysis(
                    type=bt["type"],
                    severity=bt["severity"],
                    function="system_analysis",
                    description=bt["description"],
                    impact=bt["impact"]
                ))
            
            # 生成优化建议
            optimization_suggestions = self._generate_fallback_suggestions(
                performance_summary, bottleneck_types
            )
            
            # 生成风险评估
            risk_assessment = self._generate_fallback_risks(performance_summary)
            
            return AnalysisResults(
                performance_score=performance_score,
                bottleneck_analysis=bottleneck_analysis,
                optimization_suggestions=optimization_suggestions,
                risk_assessment=risk_assessment
            )
            
        except Exception as e:
            logger.error(f"回退分析失败: {str(e)}")
            return AnalysisResults(
                performance_score=50.0,
                bottleneck_analysis=[],
                optimization_suggestions=[],
                risk_assessment=RiskAssessment()
            )
    
    def _build_analysis_prompt(self, processed_data: Dict[str, Any]) -> str:
        """构建分析提示"""
        template = self.config_manager.get_template("performance_analysis")
        if not template:
            template = "请分析以下性能数据并提供优化建议。"
        
        basic_info = processed_data.get("basic_info", {})
        perf_summary = processed_data.get("performance_summary", {})
        slow_functions = processed_data.get("slow_functions", [])
        
        # 格式化慢函数信息
        slow_func_text = ""
        for i, func in enumerate(slow_functions[:5], 1):
            slow_func_text += f"{i}. {func.get('function_name', 'unknown')} - {func.get('duration', 0):.3f}秒\n"
            slow_func_text += f"   文件: {func.get('file_path', 'unknown')}\n"
        
        return template.format(
            request_path=basic_info.get("request_path", ""),
            request_method=basic_info.get("request_method", ""),
            status_code=basic_info.get("status_code", ""),
            framework=basic_info.get("framework", ""),
            total_duration=perf_summary.get("total_duration", 0),
            cpu_time=perf_summary.get("cpu_time", 0),
            memory_peak=perf_summary.get("memory_peak", 0),
            function_count=perf_summary.get("function_count", 0),
            slow_function_count=perf_summary.get("slow_function_count", 0),
            slow_functions=slow_func_text
        )
    
    def _calculate_performance_score(self, performance_summary: Dict[str, Any]) -> float:
        """计算性能评分"""
        total_duration = performance_summary.get("total_duration", 0)
        memory_peak = performance_summary.get("memory_peak", 0)
        cpu_utilization = performance_summary.get("cpu_utilization", 0)
        
        # 基于响应时间的评分
        if total_duration < 0.1:
            time_score = 100
        elif total_duration < 0.5:
            time_score = 90
        elif total_duration < 1.0:
            time_score = 75
        elif total_duration < 2.0:
            time_score = 60
        elif total_duration < 5.0:
            time_score = 40
        else:
            time_score = 20
        
        # 基于内存使用的评分
        if memory_peak < 50:
            memory_score = 100
        elif memory_peak < 100:
            memory_score = 90
        elif memory_peak < 200:
            memory_score = 80
        elif memory_peak < 500:
            memory_score = 60
        else:
            memory_score = 40
        
        # 基于CPU利用率的评分
        if cpu_utilization < 0.5:
            cpu_score = 100
        elif cpu_utilization < 0.7:
            cpu_score = 85
        elif cpu_utilization < 0.9:
            cpu_score = 70
        else:
            cpu_score = 50
        
        # 综合评分
        final_score = (time_score * 0.5 + memory_score * 0.3 + cpu_score * 0.2)
        return round(final_score, 1)
    
    def _generate_fallback_suggestions(
        self, 
        performance_summary: Dict[str, Any], 
        bottleneck_types: List[Dict[str, Any]]
    ) -> List[OptimizationSuggestion]:
        """生成回退优化建议"""
        suggestions = []
        
        total_duration = performance_summary.get("total_duration", 0)
        
        # 基于响应时间的建议
        if total_duration > 2.0:
            suggestions.append(OptimizationSuggestion(
                category="performance",
                priority="high",
                title="优化响应时间",
                description="当前响应时间过长，建议进行性能优化",
                expected_improvement="预计可减少30-50%的响应时间"
            ))
        
        # 基于瓶颈类型的建议
        for bt in bottleneck_types:
            if bt["type"] == "database":
                suggestions.append(OptimizationSuggestion(
                    category="database",
                    priority="high",
                    title="优化数据库查询",
                    description="添加适当的数据库索引，优化SQL查询语句",
                    code_example="# 添加数据库索引\ndb.collection.create_index([('field', 1)])",
                    expected_improvement="预计可减少50-70%的数据库查询时间"
                ))
            elif bt["type"] == "memory":
                suggestions.append(OptimizationSuggestion(
                    category="memory",
                    priority="medium",
                    title="优化内存使用",
                    description="减少内存占用，避免内存泄漏",
                    expected_improvement="预计可减少20-40%的内存使用"
                ))
        
        return suggestions
    
    def _generate_fallback_risks(self, performance_summary: Dict[str, Any]) -> RiskAssessment:
        """生成回退风险评估"""
        current_risks = []
        potential_issues = []
        recommendations = []
        
        total_duration = performance_summary.get("total_duration", 0)
        memory_peak = performance_summary.get("memory_peak", 0)
        
        if total_duration > 5.0:
            current_risks.append("响应时间过长可能导致用户体验下降")
            recommendations.append("建议立即进行性能优化")
        
        if memory_peak > 1000:
            current_risks.append("内存使用过高可能导致系统不稳定")
            recommendations.append("建议优化内存使用或增加服务器内存")
        
        if total_duration > 2.0:
            potential_issues.append("在高并发情况下可能出现严重的性能瓶颈")
            recommendations.append("建议进行压力测试")
        
        return RiskAssessment(
            current_risks=current_risks,
            potential_issues=potential_issues,
            recommendations=recommendations
        )
    
    async def _parse_ai_result(self, ai_result: Dict[str, Any], processed_data: Dict[str, Any]) -> AnalysisResults:
        """解析AI结构化结果"""
        # 这里需要根据实际的AI响应格式进行解析
        # 当前返回回退分析
        return await self._analyze_with_fallback(processed_data)
    
    async def _parse_text_result(self, ai_text: str, processed_data: Dict[str, Any]) -> AnalysisResults:
        """解析AI文本结果"""
        # 这里可以实现文本解析逻辑
        # 当前返回回退分析
        return await self._analyze_with_fallback(processed_data)
    
    async def _parse_custom_ai_result(self, ai_result: Dict[str, Any], processed_data: Dict[str, Any]) -> AnalysisResults:
        """解析自定义AI结果"""
        # 这里需要根据自定义AI的响应格式进行解析
        # 当前返回回退分析
        return await self._analyze_with_fallback(processed_data)


# 全局性能分析器实例
performance_analyzer = PerformanceAnalyzer()