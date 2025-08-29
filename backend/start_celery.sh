#!/bin/bash

# Celery Worker启动脚本
cd /Users/jahan/workspace/pystrument/backend

echo "启动Celery Worker..."
celery -A app.tasks.ai_analysis.celery_app worker \
  --loglevel=debug \
  --concurrency=2 \
  -Q analysis,batch,maintenance,reports \
  --hostname=pystrument-worker@%h \
  --logfile=/tmp/celery-worker.log \
  --pidfile=/tmp/celery-worker.pid

echo "Celery Worker已启动"