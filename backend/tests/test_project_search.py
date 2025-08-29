"""
项目搜索功能测试
"""
import pytest
from httpx import AsyncClient
from app.main import app


class TestProjectSearch:
    """项目搜索功能测试类"""
    
    @pytest.fixture
    async def client(self):
        """创建测试客户端"""
        async with AsyncClient(app=app, base_url="http://test") as ac:
            yield ac
    
    @pytest.mark.asyncio
    async def test_project_search_by_name(self, client: AsyncClient):
        """测试项目名称模糊搜索"""
        # 测试不带搜索参数的请求
        response = await client.get("/api/v1/projects")
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data
        assert "total" in data
        
        # 测试带名称搜索参数的请求
        response = await client.get("/api/v1/projects?name=test")
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data
        assert "total" in data
        
        # 测试带多个参数的请求
        response = await client.get("/api/v1/projects?name=test&page=1&size=10")
        assert response.status_code == 200
        data = response.json()
        assert "projects" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data


if __name__ == "__main__":
    pytest.main([__file__])