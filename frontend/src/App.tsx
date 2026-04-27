import { AlertCircle, Loader2, Search } from "lucide-react";
import { FormEvent, useState } from "react";

import { extractMedia } from "./api";
import { MediaResult } from "./components/MediaResult";
import type { ExtractResponse } from "./types";
import "./styles.css";

export default function App() {
  const [url, setUrl] = useState("");
  const [result, setResult] = useState<ExtractResponse | null>(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const trimmedUrl = url.trim();
    setError("");
    setResult(null);

    if (!trimmedUrl) {
      setError("请先输入帖子链接。");
      return;
    }

    setIsLoading(true);
    try {
      setResult(await extractMedia(trimmedUrl));
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "解析失败，请稍后重试。");
    } finally {
      setIsLoading(false);
    }
  }

  return (
    <main className="app-shell">
      <header className="topbar">
        <p className="eyebrow">XDownloader</p>
        <h1>保存 X/Twitter 媒体</h1>
      </header>

      <form className="extract-form" onSubmit={handleSubmit}>
        <label htmlFor="tweet-url">X/Twitter 链接</label>
        <div className="input-row">
          <input
            id="tweet-url"
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            placeholder="https://x.com/user/status/1234567890"
            autoComplete="off"
            inputMode="url"
          />
          <button type="submit" disabled={isLoading}>
            {isLoading ? <Loader2 className="spin" aria-hidden="true" /> : <Search aria-hidden="true" />}
            <span>{isLoading ? "正在解析" : "解析"}</span>
          </button>
        </div>
      </form>

      {isLoading ? (
        <div className="message info" role="status">
          <Loader2 className="spin" aria-hidden="true" />
          <span>正在解析，Render 免费服务首次唤醒可能需要几十秒。</span>
        </div>
      ) : null}

      {error ? (
        <div className="message error" role="alert">
          <AlertCircle aria-hidden="true" />
          <span>{error}</span>
        </div>
      ) : null}

      {result ? <MediaResult result={result} /> : null}
    </main>
  );
}
