# Render 部署说明

当前 Render 后端服务：

```text
https://xdownloader-api-cyge.onrender.com
```

健康检查：

```text
https://xdownloader-api-cyge.onrender.com/api/health
```

解析接口：

```text
POST https://xdownloader-api-cyge.onrender.com/api/extract
```

## 后端环境变量

部署 PWA 前端后，把前端正式域名加入后端 CORS：

```text
XDOWNLOADER_CORS_ORIGINS=https://your-pwa-domain.example
```

如果有多个前端域名，用英文逗号分隔：

```text
XDOWNLOADER_CORS_ORIGINS=https://app.example,https://preview.example
```

本地开发域名 `http://localhost:5173` 和 `http://127.0.0.1:5173` 会默认保留。

## 注意事项

- Render 免费服务空闲后会休眠，首次请求可能较慢。
- 当前版本只解析并返回媒体直链，不代理媒体文件。
- 当前版本只支持公开 X/Twitter 帖子。
- 不要把私人账号 cookies 放到服务端。

## Optional X cookies

For private personal use, the backend can pass an X account cookies file to
`yt-dlp`. Store the cookies only on the backend Render service, never on the
frontend static site.

1. Export X cookies in Netscape `cookies.txt` format from a browser logged in
   to the account you want to use.
2. Convert the file to base64 locally:

```powershell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("C:\path\to\x-cookies.txt")) | Set-Clipboard
```

3. Add this backend environment variable in Render:

```text
XDOWNLOADER_X_COOKIES_B64=<paste base64 cookies.txt content>
```

After saving the variable, redeploy the backend. Do not commit cookies or base64
cookies to git, and do not add this value to frontend environment variables.
