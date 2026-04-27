# 本地开发说明

## 依赖

- Python 3.12
- uv
- Node.js 24+
- npm

## 启动顺序

1. 启动后端：

   ```powershell
   cd backend
   $env:UV_CACHE_DIR=(Join-Path (Resolve-Path '..').Path '.uv-cache')
   uv run --python 'D:\Program Files\Python\Python3\python.exe' --no-managed-python --no-python-downloads fastapi dev app/main.py
   ```

2. 启动前端：

   ```powershell
   cd frontend
   npm.cmd install
   npm.cmd run dev
   ```

3. 打开 Vite 输出的本地地址，默认是 `http://127.0.0.1:5173`。

## 验证

```powershell
cd backend
$env:UV_CACHE_DIR=(Join-Path (Resolve-Path '..').Path '.uv-cache')
uv run --python 'D:\Program Files\Python\Python3\python.exe' --no-managed-python --no-python-downloads pytest -q

cd ..\frontend
npm.cmd test
npm.cmd run build
```

如果依赖安装被网络策略阻止，先允许 uv 访问 PyPI、npm 访问 npm registry，再重新运行验证命令。
