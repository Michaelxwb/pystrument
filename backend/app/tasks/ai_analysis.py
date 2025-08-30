"""
Celery异步任务
"""
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from celery import Celery
from app.config.settings import settings
from app.services.ai_analyzer import performance_analyzer
from app.utils.database import db_manager, init_database
from app.models.analysis import AnalysisRecord, AnalysisStatus, AnalysisPriority
from app.utils.database import get_database

logger = logging.getLogger(__name__)

# 创建Celery应用
celery_app = Celery(
    'performance_monitor',
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=['app.tasks.ai_analysis']
)

# 配置Celery
celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,  # 5分钟超时
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=100,
)


# 初始化数据库连接
async def initialize_database():
    """初始化数据库连接"""
    try:
        await init_database()
        logger.info("数据库连接初始化成功")
    except Exception as e:
        logger.error(f"数据库连接初始化失败: {str(e)}")
        raise


@celery_app.task(bind=True, name='ai_analysis.analyze_performance')
def analyze_performance_task(
    self,
    performance_record_id: str,
    ai_service: Optional[str] = None,
    priority: str = 'normal',
    analysis_id: Optional[str] = None  # 新增参数，接受API传入的analysis_id
):
    """
    异步分析性能数据
    
    Args:
        performance_record_id: 性能记录ID
        ai_service: AI服务名称
        priority: 分析优先级
        analysis_id: 分析ID（可选，由API传入）
    """
    # 初始化事件循环
    loop = None
    try:
        logger.info(f"开始执行性能分析任务: {performance_record_id}, AI服务: {ai_service}, 优先级: {priority}")
        
        # 初始化数据库连接
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(initialize_database())
        
        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={'step': 'loading_data', 'progress': 10}
        )
        
        # 获取性能记录
        performance_record = loop.run_until_complete(
            db_manager.get_performance_record(performance_record_id)
        )
        
        if not performance_record:
            raise ValueError(f"性能记录不存在: {performance_record_id}")
        
        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={'step': 'analyzing', 'progress': 30}
        )
        
        # 执行AI分析（传递数据库连接以加载最新配置）
        db = get_database()
        analysis_results = loop.run_until_complete(
            performance_analyzer.analyze_performance(
                performance_record,
                ai_service=ai_service
            )
        )
        
        # 更新任务状态
        self.update_state(
            state='PROGRESS',
            meta={'step': 'saving_results', 'progress': 80}
        )
        
        # 使用传入的analysis_id，如果不为空的话
        final_analysis_id = analysis_id or f"analysis_{performance_record_id}_{int(datetime.utcnow().timestamp())}"
        
        # 检查是否已存在分析记录
        existing_record = None
        if analysis_id:
            existing_record = loop.run_until_complete(
                db_manager.get_analysis_record_by_id(analysis_id)
            )
        
        if existing_record:
            # 更新现有记录
            logger.info(f"更新分析记录: {analysis_id}")
            existing_record.results = analysis_results
            existing_record.status = AnalysisStatus.SUCCESS
            existing_record.updated_at = datetime.utcnow()
            
            # 保存到数据库
            loop.run_until_complete(db_manager.save_analysis_record(existing_record))
            
            analysis_record = existing_record
        else:
            # 创建新记录
            analysis_record = AnalysisRecord(
                analysis_id=final_analysis_id,
                performance_record_id=performance_record_id,
                project_key=performance_record.get("project_key", "unknown"),
                ai_service=ai_service or "fallback",
                results=analysis_results,
                task_id=self.request.id,
                status=AnalysisStatus.SUCCESS,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
                priority=AnalysisPriority(priority)
            )
            
            # 保存到数据库
            loop.run_until_complete(db_manager.save_analysis_record(analysis_record))
        
        # 更新任务状态
        self.update_state(
            state='SUCCESS',
            meta={
                'step': 'completed',
                'progress': 100,
                'analysis_id': analysis_record.analysis_id,
                'performance_score': analysis_results.performance_score
            }
        )
        
        # 更新任务状态记录
        loop.run_until_complete(
            db_manager.update_task_status(
                self.request.id,
                "SUCCESS",
                100,
                datetime.utcnow()
            )
        )
        
        return {
            'status': 'success',
            'analysis_id': analysis_record.analysis_id,
            'performance_score': analysis_results.performance_score,
            'bottleneck_count': len(analysis_results.bottleneck_analysis),
            'suggestion_count': len(analysis_results.optimization_suggestions)
        }
        
    except Exception as e:
        logger.error(f"性能分析任务失败: {str(e)}")
        
        # 更新任务状态为失败
        self.update_state(
            state='FAILURE',
            meta={
                'step': 'failed',
                'error': str(e),
                'progress': 0
            }
        )
        
        # 保存失败记录
        try:
            if loop:
                # 使用传入的analysis_id，如果不为空的话
                final_analysis_id = analysis_id or f"analysis_{performance_record_id}_{int(datetime.utcnow().timestamp())}"
                
                analysis_record = AnalysisRecord(
                    analysis_id=final_analysis_id,
                    performance_record_id=performance_record_id,
                    project_key="unknown",
                    ai_service=ai_service or "fallback",
                    results=None,
                    task_id=self.request.id,
                    status=AnalysisStatus.FAILURE,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow(),
                    priority=AnalysisPriority(priority)
                )
                loop.run_until_complete(db_manager.save_analysis_record(analysis_record))
        except Exception as inner_e:
            logger.error(f"保存失败记录时出错: {str(inner_e)}")
        
        raise
    finally:
        # 关闭事件循环
        if loop:
            try:
                loop.close()
            except Exception as e:
                logger.error(f"关闭事件循环时出错: {str(e)}")


@celery_app.task(name='ai_analysis.batch_analyze_performance')
def batch_analyze_performance_task(
    performance_record_ids: list,
    ai_service: Optional[str] = None,
    priority: str = 'normal'
):
    """
    批量分析性能数据
    
    Args:
        performance_record_ids: 性能记录ID列表
        ai_service: AI服务名称
        priority: 分析优先级
    """
    try:
        results = []
        total_count = len(performance_record_ids)
        
        for i, record_id in enumerate(performance_record_ids):
            try:
                # 调用单个分析任务
                result = analyze_performance_task.apply_async(
                    args=[record_id, ai_service, priority],
                    countdown=i * 2  # 间隔2秒执行，避免同时处理过多任务
                )
                
                results.append({
                    'record_id': record_id,
                    'task_id': result.id,
                    'status': 'queued'
                })
                
            except Exception as e:
                logger.error(f"批量分析任务创建失败: {record_id}, {str(e)}")
                results.append({
                    'record_id': record_id,
                    'status': 'failed',
                    'error': str(e)
                })
        
        return {
            'status': 'success',
            'total_count': total_count,
            'queued_count': sum(1 for r in results if r['status'] == 'queued'),
            'failed_count': sum(1 for r in results if r['status'] == 'failed'),
            'results': results
        }
        
    except Exception as e:
        logger.error(f"批量分析任务失败: {str(e)}")
        raise


@celery_app.task(name='ai_analysis.cleanup_old_analysis')
def cleanup_old_analysis_task(days: int = 30):
    """
    清理旧的分析记录
    
    Args:
        days: 保留天数
    """
    try:
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # 删除旧的分析记录
        result = asyncio.run(
            db_manager.cleanup_old_analysis_records(cutoff_date)
        )
        
        logger.info(f"清理了 {result.get('deleted_count', 0)} 条旧的分析记录")
        
        return {
            'status': 'success',
            'deleted_count': result.get('deleted_count', 0),
            'cutoff_date': cutoff_date.isoformat()
        }
        
    except Exception as e:
        logger.error(f"清理旧分析记录失败: {str(e)}")
        raise


@celery_app.task(name='ai_analysis.performance_report')
def generate_performance_report_task(
    project_key: str,
    start_date: str,
    end_date: str,
    report_type: str = 'summary'
):
    """
    生成性能报告
    
    Args:
        project_key: 项目键
        start_date: 开始日期 (ISO格式)
        end_date: 结束日期 (ISO格式)
        report_type: 报告类型 (summary, detailed, trend)
    """
    try:
        from datetime import datetime
        
        start_dt = datetime.fromisoformat(start_date.replace('Z', '+00:00'))
        end_dt = datetime.fromisoformat(end_date.replace('Z', '+00:00'))
        
        # 获取时间范围内的性能数据
        performance_records = asyncio.run(
            db_manager.get_performance_records_by_date_range(
                project_key, start_dt, end_dt
            )
        )
        
        # 获取分析结果
        analysis_records = asyncio.run(
            db_manager.get_analysis_records_by_date_range(
                project_key, start_dt, end_dt
            )
        )
        
        # 生成报告
        report_data = {
            'project_key': project_key,
            'report_type': report_type,
            'date_range': {
                'start': start_date,
                'end': end_date
            },
            'summary': {
                'total_requests': len(performance_records),
                'analyzed_requests': len(analysis_records),
                'avg_response_time': 0,
                'avg_performance_score': 0,
                'top_bottlenecks': []
            },
            'generated_at': datetime.utcnow().isoformat()
        }
        
        if performance_records:
            # 计算平均响应时间
            total_duration = sum(
                record.get('performance_metrics', {}).get('total_duration', 0)
                for record in performance_records
            )
            report_data['summary']['avg_response_time'] = total_duration / len(performance_records)
        
        if analysis_records:
            # 计算平均性能评分
            total_score = sum(
                record.get('results', {}).get('performance_score', 0)
                for record in analysis_records
            )
            report_data['summary']['avg_performance_score'] = total_score / len(analysis_records)
            
            # 统计瓶颈类型
            bottleneck_stats = {}
            for record in analysis_records:
                bottlenecks = record.get('results', {}).get('bottleneck_analysis', [])
                for bottleneck in bottlenecks:
                    bt_type = bottleneck.get('type', 'unknown')
                    bottleneck_stats[bt_type] = bottleneck_stats.get(bt_type, 0) + 1
            
            # 获取前5个瓶颈类型
            report_data['summary']['top_bottlenecks'] = sorted(
                bottleneck_stats.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        
        # 保存报告
        report_id = f"report_{project_key}_{int(datetime.utcnow().timestamp())}"
        asyncio.run(
            db_manager.save_performance_report(report_id, report_data)
        )
        
        return {
            'status': 'success',
            'report_id': report_id,
            'summary': report_data['summary']
        }
        
    except Exception as e:
        logger.error(f"生成性能报告失败: {str(e)}")
        raise


# 任务路由配置
celery_app.conf.task_routes = {
    'ai_analysis.analyze_performance': {'queue': 'analysis'},
    'ai_analysis.batch_analyze_performance': {'queue': 'batch'},
    'ai_analysis.cleanup_old_analysis': {'queue': 'maintenance'},
    'ai_analysis.performance_report': {'queue': 'reports'},
}

# 定时任务配置
from celery.schedules import crontab

celery_app.conf.beat_schedule = {
    'cleanup-old-analysis': {
        'task': 'ai_analysis.cleanup_old_analysis',
        'schedule': crontab(hour=2, minute=0),  # 每天凌晨2点执行
        'args': (30,)  # 保留30天的数据
    },
}