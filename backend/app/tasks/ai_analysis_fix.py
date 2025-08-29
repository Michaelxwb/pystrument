"""
修正版的Celery任务实现，接受传入的analysis_id参数
"""
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime
import logging

from app.tasks.ai_analysis import celery_app
from app.services.ai_analyzer import performance_analyzer
from app.utils.database import db_manager, init_database
from app.models.analysis import AnalysisRecord, AnalysisStatus, AnalysisPriority

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name='ai_analysis.analyze_performance_fixed')
def analyze_performance_fixed_task(
    self,
    performance_record_id: str,
    analysis_id: str,  # 接受传入的analysis_id
    ai_service: Optional[str] = None,
    priority: str = 'normal'
):
    """
    修正版的异步分析性能数据任务，接受传入的analysis_id
    
    Args:
        performance_record_id: 性能记录ID
        analysis_id: 分析ID，由API创建
        ai_service: AI服务名称
        priority: 分析优先级
    """
    # 初始化事件循环
    loop = None
    try:
        logger.info(f"开始执行修正版性能分析任务: {performance_record_id}, 分析ID: {analysis_id}, AI服务: {ai_service}")
        
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
        
        # 执行AI分析
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
        
        # 查询已存在的分析记录
        existing_record = loop.run_until_complete(
            db_manager.get_analysis_record_by_id(analysis_id)
        )
        
        if not existing_record:
            logger.warning(f"分析记录不存在，创建新记录: {analysis_id}")
            # 如果记录不存在，创建新的记录
            analysis_record = AnalysisRecord(
                analysis_id=analysis_id,
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
        else:
            logger.info(f"更新已存在的分析记录: {analysis_id}")
            # 更新已存在的记录
            existing_record.results = analysis_results
            existing_record.status = AnalysisStatus.SUCCESS
            existing_record.updated_at = datetime.utcnow()
            
            # 保存到数据库
            loop.run_until_complete(db_manager.save_analysis_record(existing_record))
        
        # 更新任务状态
        self.update_state(
            state='SUCCESS',
            meta={
                'step': 'completed',
                'progress': 100,
                'analysis_id': analysis_id,
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
            'analysis_id': analysis_id,
            'performance_score': analysis_results.performance_score,
            'bottleneck_count': len(analysis_results.bottleneck_analysis),
            'suggestion_count': len(analysis_results.optimization_suggestions)
        }
        
    except Exception as e:
        logger.error(f"修正版性能分析任务失败: {str(e)}")
        
        # 更新任务状态为失败
        self.update_state(
            state='FAILURE',
            meta={
                'step': 'failed',
                'error': str(e),
                'progress': 0
            }
        )
        
        # 更新任务状态记录
        if loop:
            loop.run_until_complete(
                db_manager.update_task_status(
                    self.request.id,
                    "FAILURE",
                    0,
                    datetime.utcnow()
                )
            )
        
        raise
    finally:
        # 关闭事件循环
        if loop:
            try:
                loop.close()
            except Exception as e:
                logger.error(f"关闭事件循环时出错: {str(e)}")