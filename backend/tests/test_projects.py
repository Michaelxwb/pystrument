"""
项目管理API测试用例
"""
import pytest
import asyncio
from httpx import AsyncClient
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

from app.main import app
from app.models.project import Project, ProjectConfig
from app.services.database import db_manager


class TestProjectAPI:
    """项目API测试类"""
    
    @pytest.fixture
    async def client(self):
        """创建测试客户端"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.fixture
    async def mock_project(self):
        """模拟项目数据"""
        return Project(
            id="test_project_123",
            project_key="test_key_123",
            name="测试项目",
            description="这是一个测试项目",
            framework="flask",
            base_url="http://test.example.com",
            config=ProjectConfig(
                sampling_rate=10.0,
                enable_ai_analysis=True,
                max_trace_duration=30.0,
                excluded_paths=["/health", "/metrics"]
            ),
            status="active",
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    
    @pytest.mark.asyncio
    async def test_create_project_success(self, client: AsyncClient):
        """测试创建项目成功"""
        project_data = {
            "name": "新测试项目",
            "description": "项目描述",
            "framework": "flask",
            "base_url": "http://example.com",
            "sampling_rate": 15.0,
            "enable_ai_analysis": True
        }
        
        with patch.object(db_manager, 'create_project') as mock_create:
            mock_create.return_value = Project(
                **project_data,
                id="new_project_id",
                project_key="new_project_key",
                status="active",
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            response = await client.post("/api/v1/projects", json=project_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 0
            assert data["data"]["name"] == project_data["name"]
            assert data["data"]["framework"] == project_data["framework"]
            mock_create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_project_validation_error(self, client: AsyncClient):
        """测试创建项目验证错误"""
        invalid_data = {
            "name": "",  # 空名称
            "framework": "invalid_framework"  # 无效框架
        }
        
        response = await client.post("/api/v1/projects", json=invalid_data)
        
        assert response.status_code == 422  # Validation error
    
    @pytest.mark.asyncio
    async def test_get_projects_success(self, client: AsyncClient, mock_project):
        """测试获取项目列表成功"""
        with patch.object(db_manager, 'get_projects') as mock_get:
            mock_get.return_value = {
                "projects": [mock_project],
                "total": 1,
                "page": 1,
                "size": 20,
                "pages": 1
            }
            
            response = await client.get("/api/v1/projects?page=1&size=20")
            
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 0
            assert len(data["data"]["projects"]) == 1
            assert data["data"]["total"] == 1
            mock_get.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_project_by_key_success(self, client: AsyncClient, mock_project):
        """测试根据项目键获取项目成功"""
        project_key = "test_key_123"
        
        with patch.object(db_manager, 'get_project_by_key') as mock_get:
            mock_get.return_value = mock_project
            
            response = await client.get(f"/api/v1/projects/{project_key}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 0
            assert data["data"]["project_key"] == project_key
            mock_get.assert_called_once_with(project_key)
    
    @pytest.mark.asyncio
    async def test_get_project_by_key_not_found(self, client: AsyncClient):
        """测试获取不存在的项目"""
        project_key = "nonexistent_key"
        
        with patch.object(db_manager, 'get_project_by_key') as mock_get:
            mock_get.return_value = None
            
            response = await client.get(f"/api/v1/projects/{project_key}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 20001  # PROJECT_NOT_FOUND
            mock_get.assert_called_once_with(project_key)
    
    @pytest.mark.asyncio
    async def test_update_project_success(self, client: AsyncClient, mock_project):
        """测试更新项目成功"""
        project_key = "test_key_123"
        update_data = {
            "name": "更新后的项目名",
            "description": "更新后的描述",
            "sampling_rate": 25.0
        }
        
        with patch.object(db_manager, 'get_project_by_key') as mock_get, \
             patch.object(db_manager, 'update_project') as mock_update:
            
            mock_get.return_value = mock_project
            updated_project = mock_project.copy()
            updated_project.name = update_data["name"]
            updated_project.description = update_data["description"]
            mock_update.return_value = updated_project
            
            response = await client.put(f"/api/v1/projects/{project_key}", json=update_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 0
            assert data["data"]["name"] == update_data["name"]
            mock_get.assert_called_once()
            mock_update.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_project_success(self, client: AsyncClient, mock_project):
        """测试删除项目成功"""
        project_key = "test_key_123"
        
        with patch.object(db_manager, 'get_project_by_key') as mock_get, \
             patch.object(db_manager, 'delete_project') as mock_delete:
            
            mock_get.return_value = mock_project
            mock_delete.return_value = True
            
            response = await client.delete(f"/api/v1/projects/{project_key}")
            
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 0
            mock_get.assert_called_once()
            mock_delete.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_project_stats_success(self, client: AsyncClient, mock_project):
        """测试获取项目统计信息成功"""
        project_key = "test_key_123"
        mock_stats = {
            "total_requests": 1500,
            "today_requests": 150,
            "avg_response_time": 250.5,
            "error_rate": 0.02,
            "performance_score": 85.5,
            "last_24h_trends": [
                {"hour": 0, "requests": 10, "avg_duration": 0.2},
                {"hour": 1, "requests": 15, "avg_duration": 0.18}
            ]
        }
        
        with patch.object(db_manager, 'get_project_by_key') as mock_get, \
             patch.object(db_manager, 'get_project_stats') as mock_stats_func:
            
            mock_get.return_value = mock_project
            mock_stats_func.return_value = mock_stats
            
            response = await client.get(f"/api/v1/projects/{project_key}/stats")
            
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 0
            assert data["data"]["total_requests"] == mock_stats["total_requests"]
            assert data["data"]["performance_score"] == mock_stats["performance_score"]
            mock_get.assert_called_once()
            mock_stats_func.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_database_error_handling(self, client: AsyncClient):
        """测试数据库错误处理"""
        with patch.object(db_manager, 'get_projects') as mock_get:
            mock_get.side_effect = Exception("数据库连接失败")
            
            response = await client.get("/api/v1/projects")
            
            assert response.status_code == 200
            data = response.json()
            assert data["code"] == 10000  # SYSTEM_ERROR
            assert "数据库连接失败" in data["msg"]


class TestProjectValidation:
    """项目数据验证测试"""
    
    def test_project_config_validation(self):
        """测试项目配置验证"""
        # 有效配置
        valid_config = ProjectConfig(
            sampling_rate=10.0,
            enable_ai_analysis=True,
            max_trace_duration=30.0,
            excluded_paths=["/health"]
        )
        assert valid_config.sampling_rate == 10.0
        assert valid_config.enable_ai_analysis is True
        
        # 无效采样率
        with pytest.raises(ValueError):
            ProjectConfig(sampling_rate=150.0)  # 超过100%
        
        with pytest.raises(ValueError):
            ProjectConfig(sampling_rate=-5.0)   # 负数
    
    def test_project_key_generation(self):
        """测试项目键生成"""
        from app.utils.helpers import generate_project_key
        
        key1 = generate_project_key()
        key2 = generate_project_key()
        
        assert len(key1) == 32
        assert len(key2) == 32
        assert key1 != key2  # 应该是唯一的
        assert key1.isalnum()  # 应该只包含字母和数字
    
    def test_project_url_validation(self):
        """测试项目URL验证"""
        from app.models.project import ProjectCreate
        
        # 有效URL
        valid_project = ProjectCreate(
            name="测试项目",
            framework="flask",
            base_url="https://api.example.com"
        )
        assert valid_project.base_url == "https://api.example.com"
        
        # 无效URL应该在Pydantic验证时被捕获
        with pytest.raises(ValueError):
            ProjectCreate(
                name="测试项目",
                framework="flask",
                base_url="not_a_url"
            )


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v", "--tb=short"])