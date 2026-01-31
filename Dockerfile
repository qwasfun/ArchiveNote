################################
# 1. Build Vue Frontend
################################
FROM node:24-alpine AS frontend-builder

WORKDIR /app/web
COPY web/. ./
RUN npm install && npm run build


################################
# 2. Build FastAPI Backend
################################
FROM python:3.13-slim

WORKDIR /api

# 拷贝后端
COPY api/ ./

ENV PATH="/api/.venv/bin:$PATH"

# 安装后端依赖
RUN mkdir -p data && pip install uv && uv sync

# 拷贝前端静态文件到 FastAPI
COPY --from=frontend-builder /app/web/dist ./app/static

EXPOSE 2601

# Uvicorn 启动 FastAPI
CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "2601"]
