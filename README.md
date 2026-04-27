# XDownloader

XDownloader 是一个本地优先的 X/Twitter 公开帖子媒体下载器。当前版本包含：

- `backend/`：FastAPI 后端，使用 `yt-dlp` 解析公开帖子的视频、GIF 和图片直链。
- `frontend/`：React + Vite + TypeScript 网页端，负责输入链接、展示媒体列表和打开下载直链。

后端不代理、不存储第三方媒体文件；下载链接来自 X/Twitter CDN，由浏览器直接打开或保存。

## 功能范围

- 支持公开、无需登录访问的 `x.com` / `twitter.com` 单条帖子链接。
- 支持视频、GIF、图片。
- 不支持私密帖、受保护账号、cookies、批量下载、MP3 转换或后端代理下载。

## 目录结构

```text
backend/   FastAPI API 服务
frontend/  React + Vite 网页端
docs/      本地开发说明
```

## 后端启动

```powershell
cd F:\Projects\XDownloader\backend
$env:UV_CACHE_DIR="F:\Projects\XDownloader\.uv-cache"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

健康检查：

```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health" -UseBasicParsing
```

## 前端启动

```powershell
cd F:\Projects\XDownloader\frontend
$env:npm_config_cache="F:\Projects\XDownloader\.npm-cache"
npm.cmd install --no-audit --no-fund --registry=https://registry.npmmirror.com
npm.cmd run dev
```

本机访问：

```text
http://127.0.0.1:5173
```

局域网访问时，前端改用：

```powershell
cd F:\Projects\XDownloader\frontend
.\node_modules\.bin\vite.cmd --host 0.0.0.0 --port 5173
```

然后在同一局域网其他设备访问：

```text
http://<本机局域网IP>:5173
```

当前本机示例 IP 曾检测为 `10.10.28.191`，如果网络变化，请用 `ipconfig` 重新确认。

## API

```http
POST /api/extract
Content-Type: application/json

{ "url": "https://x.com/user/status/1234567890" }
```

响应包含 `title`、`author`、`thumbnail`、`source_url` 和 `items[]`。每个 `items[]` 元素包含媒体类型、直链、清晰度、扩展名、尺寸和文件大小等信息。

## 验证

后端：

```powershell
cd F:\Projects\XDownloader\backend
$env:UV_CACHE_DIR="F:\Projects\XDownloader\.uv-cache"
uv run --python 'D:\Program Files\Python\Python3\python.exe' --no-managed-python --no-python-downloads pytest -q
```

前端：

```powershell
cd F:\Projects\XDownloader\frontend
npm.cmd test
npm.cmd run build
```

## 后续方向

下一步优先开发 Android APP。建议复用当前后端的 `/api/extract`，Android 端做独立原生界面；如果要完全离线独立解析，需要在 Android 内嵌 Python/yt-dlp，复杂度和维护成本明显更高。

## 公网部署

项目根目录提供了 `render.yaml`，可把后端部署到 Render 免费 Web Service。

部署文档见：

```text
docs/render-deployment.md
```
