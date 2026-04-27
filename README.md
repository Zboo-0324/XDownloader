# XDownloader

XDownloader 是一个面向 X/Twitter 公共帖子的媒体解析工具。

- `backend/`: FastAPI API，使用 `yt-dlp` 解析公开帖子里的视频、GIF 和图片直链。
- `frontend/`: React + Vite + TypeScript 移动 Web/PWA 第一版。

当前第一版目标是 PWA/移动 Web：输入 X/Twitter 链接，调用公网 API，展示媒体结果，然后下载或打开原文件。第二版计划用同一套前端通过 Capacitor 打包 Android APK。

## Public API

当前 Render 服务地址：

```text
https://xdownloader-api-cyge.onrender.com
```

接口：

```http
POST /api/extract
Content-Type: application/json

{ "url": "https://x.com/user/status/1234567890" }
```

返回字段包括 `title`、`author`、`thumbnail`、`source_url` 和 `items[]`。每个 `items[]` 条目包含 `type`、`url`、`quality`、`ext`、`width`、`height`、`filesize`。

## Local Development

启动后端：

```powershell
cd F:\Projects\XDownloader
$env:UV_CACHE_DIR="F:\Projects\XDownloader\.uv-cache"
uv run --project backend --python 'D:\Program Files\Python\Python3\python.exe' --no-managed-python --no-python-downloads uvicorn app.main:app --host 127.0.0.1 --port 8000
```

启动前端：

```powershell
cd F:\Projects\XDownloader\frontend
npm.cmd install
npm.cmd run dev
```

本地前端默认通过 Vite proxy 调用 `http://127.0.0.1:8000/api`。

生产构建默认使用：

```text
VITE_API_BASE_URL=https://xdownloader-api-cyge.onrender.com
```

配置文件在 `frontend/.env.production`。

## Deployment

后端已经通过 Render 部署。部署前端 PWA 时推荐用 Vercel、Netlify 或 Render Static Site。

前端域名确定后，在 Render 后端服务里设置：

```text
XDOWNLOADER_CORS_ORIGINS=https://your-pwa-domain.example
```

多个域名用英文逗号分隔。

## Verification

后端：

```powershell
cd F:\Projects\XDownloader
$env:UV_CACHE_DIR="F:\Projects\XDownloader\.uv-cache"
uv run --project backend --python 'D:\Program Files\Python\Python3\python.exe' --no-managed-python --no-python-downloads pytest backend\tests -q
```

前端：

```powershell
cd F:\Projects\XDownloader\frontend
npm.cmd test
npm.cmd run build
```

当前后端只返回媒体直链，不代理或存储视频文件。只支持公开帖子，不建议把私人账号 cookies 放到服务端。
