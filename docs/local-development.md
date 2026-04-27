# 本地开发说明

## 依赖

- Python 3.12
- uv
- Node.js 24+
- npm

## 启动后端

```powershell
cd F:\Projects\XDownloader
$env:UV_CACHE_DIR="F:\Projects\XDownloader\.uv-cache"
uv run --project backend --python 'D:\Program Files\Python\Python3\python.exe' --no-managed-python --no-python-downloads uvicorn app.main:app --host 127.0.0.1 --port 8000
```

验证：

```powershell
Invoke-WebRequest -Uri "http://127.0.0.1:8000/api/health" -UseBasicParsing
```

## 启动前端

```powershell
cd F:\Projects\XDownloader\frontend
npm.cmd install
npm.cmd run dev
```

默认地址：

```text
http://127.0.0.1:5173
```

本地开发时，Vite 会把 `/api` 代理到 `http://127.0.0.1:8000`。

## 生产 API 配置

PWA 生产构建使用：

```text
frontend/.env.production
```

当前内容：

```text
VITE_API_BASE_URL=https://xdownloader-api-cyge.onrender.com
```

如果以后换 Render 服务名或自定义域名，只改这个变量即可。

## 验证

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
