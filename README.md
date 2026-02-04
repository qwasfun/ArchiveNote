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

```sh
# 启动（带日志）
docker compose -f docker-compose.dev.yml up
```

更多命令

```sh
# 后台启动
docker compose -f docker-compose.dev.yml up -d

# 查看日志
docker compose -f docker-compose.dev.yml logs -f

# 停止
docker compose -f docker-compose.dev.yml down

# 重新构建（如果修改了依赖）
docker compose -f docker-compose.dev.yml up --build
```

前端开发服务器：http://localhost:5173

后端 API：http://localhost:8000

API 文档：http://localhost:8000/docs

## 代码提交

使用 [pre-commit](https://pre-commit.com/) 格式化

```shell
pip install pre-commit

pre-commit run --all-files
```

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
