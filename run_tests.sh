#!/bin/bash

# 性能分析平台测试运行脚本

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查依赖
check_dependencies() {
    print_info "检查测试依赖..."
    
    # 检查Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 未安装"
        exit 1
    fi
    
    # 检查pip
    if ! command -v pip3 &> /dev/null; then
        print_error "pip3 未安装"
        exit 1
    fi
    
    # 检查pytest
    if ! python3 -c "import pytest" &> /dev/null; then
        print_warning "pytest 未安装，正在安装..."
        pip3 install pytest pytest-asyncio pytest-cov
    fi
    
    print_success "依赖检查完成"
}

# 安装测试依赖
install_test_deps() {
    print_info "安装测试依赖..."
    
    pip3 install -r backend/requirements.txt
    pip3 install pytest pytest-asyncio pytest-cov pytest-xdist httpx aiohttp
    
    print_success "测试依赖安装完成"
}

# 运行单元测试
run_unit_tests() {
    print_info "运行单元测试..."
    
    cd backend
    python3 -m pytest tests/ -v \
        --tb=short \
        --durations=10 \
        --color=yes \
        -m "not e2e and not integration"
    
    if [ $? -eq 0 ]; then
        print_success "单元测试通过"
    else
        print_error "单元测试失败"
        exit 1
    fi
}

# 运行集成测试
run_integration_tests() {
    print_info "运行集成测试..."
    
    cd backend
    python3 -m pytest tests/ -v \
        --tb=short \
        --durations=10 \
        --color=yes \
        -m "integration"
    
    if [ $? -eq 0 ]; then
        print_success "集成测试通过"
    else
        print_error "集成测试失败"
        exit 1
    fi
}

# 运行端到端测试
run_e2e_tests() {
    print_info "运行端到端测试..."
    
    # 检查服务是否运行
    if ! curl -f http://localhost:8000/health &> /dev/null; then
        print_warning "后端服务未运行，正在启动..."
        start_services
        sleep 10
    fi
    
    python3 tests/e2e_test.py --url http://localhost:8000 --verbose
    
    if [ $? -eq 0 ]; then
        print_success "端到端测试通过"
    else
        print_error "端到端测试失败"
        exit 1
    fi
}

# 启动服务
start_services() {
    print_info "启动测试服务..."
    
    # 启动Docker服务
    if command -v docker-compose &> /dev/null; then
        docker-compose -f docker-compose.yml up -d mongodb redis
        print_info "等待数据库服务启动..."
        sleep 15
        
        # 启动后端服务
        cd backend
        python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 &
        BACKEND_PID=$!
        print_info "后端服务PID: $BACKEND_PID"
        
        # 等待服务启动
        sleep 10
        
        cd ..
    else
        print_error "docker-compose 未安装，无法启动测试环境"
        exit 1
    fi
}

# 停止服务
stop_services() {
    print_info "停止测试服务..."
    
    # 停止后端服务
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    
    # 停止Docker服务
    if command -v docker-compose &> /dev/null; then
        docker-compose -f docker-compose.yml down
    fi
    
    print_success "服务已停止"
}

# 生成测试报告
generate_coverage_report() {
    print_info "生成测试覆盖率报告..."
    
    cd backend
    python3 -m pytest tests/ \
        --cov=app \
        --cov-report=html \
        --cov-report=term-missing \
        --cov-report=xml \
        -m "not e2e"
    
    print_success "覆盖率报告生成完成，查看 backend/htmlcov/index.html"
}

# 代码质量检查
run_code_quality_checks() {
    print_info "运行代码质量检查..."
    
    # 检查flake8
    if command -v flake8 &> /dev/null; then
        print_info "运行 flake8 检查..."
        flake8 backend/app --max-line-length=100 --ignore=E203,W503
    fi
    
    # 检查black
    if command -v black &> /dev/null; then
        print_info "运行 black 格式检查..."
        black --check backend/app
    fi
    
    # 检查isort
    if command -v isort &> /dev/null; then
        print_info "运行 isort 导入排序检查..."
        isort --check-only backend/app
    fi
    
    print_success "代码质量检查完成"
}

# 性能测试
run_performance_tests() {
    print_info "运行性能测试..."
    
    # 这里可以添加性能测试逻辑
    # 例如使用locust或者其他性能测试工具
    
    print_info "性能测试待实现"
}

# 清理测试环境
cleanup() {
    print_info "清理测试环境..."
    
    # 清理Python缓存
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete 2>/dev/null || true
    
    # 清理测试文件
    rm -rf backend/htmlcov/ 2>/dev/null || true
    rm -rf backend/.coverage 2>/dev/null || true
    rm -rf backend/.pytest_cache/ 2>/dev/null || true
    
    print_success "环境清理完成"
}

# 显示帮助信息
show_help() {
    echo "性能分析平台测试运行脚本"
    echo ""
    echo "用法: $0 [选项]"
    echo ""
    echo "选项:"
    echo "  unit              运行单元测试"
    echo "  integration       运行集成测试"
    echo "  e2e               运行端到端测试"
    echo "  all               运行所有测试"
    echo "  coverage          生成测试覆盖率报告"
    echo "  quality           运行代码质量检查"
    echo "  performance       运行性能测试"
    echo "  install-deps      安装测试依赖"
    echo "  start-services    启动测试服务"
    echo "  stop-services     停止测试服务"
    echo "  cleanup           清理测试环境"
    echo "  help              显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  $0 unit           # 只运行单元测试"
    echo "  $0 all            # 运行所有测试"
    echo "  $0 coverage       # 生成覆盖率报告"
}

# 主函数
main() {
    case "$1" in
        "unit")
            check_dependencies
            run_unit_tests
            ;;
        "integration")
            check_dependencies
            run_integration_tests
            ;;
        "e2e")
            check_dependencies
            run_e2e_tests
            ;;
        "all")
            check_dependencies
            run_unit_tests
            run_integration_tests
            run_e2e_tests
            ;;
        "coverage")
            check_dependencies
            generate_coverage_report
            ;;
        "quality")
            run_code_quality_checks
            ;;
        "performance")
            run_performance_tests
            ;;
        "install-deps")
            install_test_deps
            ;;
        "start-services")
            start_services
            ;;
        "stop-services")
            stop_services
            ;;
        "cleanup")
            cleanup
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        "")
            print_error "请指定操作"
            show_help
            exit 1
            ;;
        *)
            print_error "未知操作: $1"
            show_help
            exit 1
            ;;
    esac
}

# 捕获退出信号，确保清理
trap 'stop_services; cleanup' EXIT

# 运行主函数
main "$@"