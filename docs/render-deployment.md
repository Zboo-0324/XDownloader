# Render 部署说明

这份配置只部署后端 API。部署完成后会得到一个公网地址，例如：

```text
https://xdownloader-api.onrender.com
```

后续 Android APP 调用：

```text
POST https://xdownloader-api.onrender.com/api/extract
```

## 1. 推送到 GitHub

在项目根目录执行：

```powershell
cd F:\Projects\XDownloader
git status
```

确认没有未提交改动后，把仓库推送到 GitHub。可以用 GitHub Desktop，也可以用命令行：

```powershell
git remote add origin https://github.com/<你的用户名>/<你的仓库名>.git
git push -u origin main
```

## 2. 在 Render 创建服务

1. 打开 Render。
2. New -> Blueprint。
3. 选择你的 GitHub 仓库。
4. Render 会读取根目录的 `render.yaml`。
5. 创建 `xdownloader-api` 服务。

## 3. 验证

部署完成后打开：

```text
https://<你的-render服务名>.onrender.com/api/health
```

看到下面内容代表后端已启动：

```json
{"status":"ok"}
```

## 4. 注意事项

- 免费服务一段时间没人访问会休眠，第一次访问可能慢。
- 当前后端只解析并返回媒体直链，不代理视频文件。
- 不要把私密账号 cookies 放到服务端；当前版本只支持公开帖子。
