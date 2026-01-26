![ArchiveNote Screenshot](./docs/assets/home.png)

# ArchiveNote

一款支持文件、笔记双向关联的轻量级管理系统

[在线演示](https://demo.archivenote.org/)

## 🚀 部署

### 使用 Docker

```bash
# 构建并启动容器
docker pull ghcr.io/qwasfun/archivenote:latest

docker run -d -p 2601:2601 -v $(pwd)/data:/app/data -e SECRET_KEY=your-production-secret-key  ghcr.io/qwasfun/archivenote:latest
```

访问 http://localhost:2601

### Docker Compose

创建 `docker-compose.yml`：

```yaml
services:
  archivenote:
    image: ghcr.io/qwasfun/archivenote:latest
    container_name: archivenote
    ports:
      - "2601:2601"
    volumes:
      - ./data:/app/data
    environment:
      - SECRET_KEY=your-production-secret-key
      # - DATABASE_URL: postgres://postgres:password@localhost:5432/postgres
    restart: unless-stopped
```

运行：

```bash
docker-compose up -d
```

## 🔐 账户

第一位注册用户自动成为系统管理员，其他注册用户为普通用户

## 💻 本地开发

### 前置要求

- Python 3.13
- Node.js 24
- npm

### 环境配置

创建 `api/.env` 文件配置环境变量：

```env
# 数据库配置
DATABASE_URL=sqlite+aiosqlite:///./data/app.db
# DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/dbname

# JWT 配置
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7
ALGORITHM=HS256
```

### 后端设置

```bash
cd api

# 创建虚拟环境
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
pip install uv
uv sync

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器
python main.py
```

后端将在 http://localhost:8000 运行

### 前端设置

```bash
cd web

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:5173 运行

## 📖 API 文档

启动后端服务后，访问以下地址查看自动生成的 API 文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📚 数据库迁移

```bash
cd api

# 创建新迁移
alembic revision --autogenerate -m "描述"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 📧 联系方式

如有问题或建议，请提交 Issue 或 Pull Request。

---

⭐ 如果这个项目对您有帮助，请给个 Star！
