"""
CORS跨域配置中间件
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config.settings import settings


def setup_cors(app: FastAPI):
    """设置CORS中间件"""
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.get_cors_origins(),
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=[
            "Accept",
            "Accept-Language",
            "Content-Language",
            "Content-Type",
            "Authorization",
            "X-Project-Key",
            "X-Request-ID"
        ],
        expose_headers=[
            "X-Total-Count",
            "X-Page-Count",
            "X-Current-Page"
        ]
    )