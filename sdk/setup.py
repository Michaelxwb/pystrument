"""
性能监控SDK安装配置
"""
from setuptools import setup, find_packages
import os

# 读取README文件
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "基于Pyinstrument的性能分析SDK"

# 读取requirements文件
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="performance-monitor-sdk",
    version="1.0.0",
    author="Performance Monitor Team",
    author_email="dev@performance-monitor.com",
    description="基于Pyinstrument的性能分析和监控SDK",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/performance-monitor/sdk",
    packages=[
        'performance_monitor',
        'performance_monitor.core',
        'performance_monitor.utils',
        'performance_monitor.flask',
        'performance_monitor.django',
        'performance_monitor.fastapi',
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Monitoring",
        "Topic :: Software Development :: Debuggers",
    ],
    python_requires=">=3.7",
    install_requires=read_requirements(),
    extras_require={
        "flask": ["Flask>=1.0.0"],
        "django": ["Django>=2.2.0"],
        "fastapi": ["fastapi>=0.68.0"],
        "dev": [
            "pytest>=6.0.0",
            "pytest-cov>=2.10.0",
            "black>=21.0.0",
            "isort>=5.0.0",
            "flake8>=3.8.0",
            "mypy>=0.800",
        ]
    },
    entry_points={
        "console_scripts": [
            "performance-monitor=performance_monitor.cli:main",
        ],
    },
    include_package_data=True,
    package_data={
        "performance_monitor": [
            "*.yaml",
            "*.yml", 
            "*.json",
            "templates/*",
        ],
    },
    keywords=[
        "performance", "monitoring", "profiling", "pyinstrument", 
        "flask", "django", "fastapi", "apm", "observability"
    ],
    project_urls={
        "Bug Reports": "https://github.com/performance-monitor/sdk/issues",
        "Source": "https://github.com/performance-monitor/sdk",
        "Documentation": "https://docs.performance-monitor.com",
    },
)