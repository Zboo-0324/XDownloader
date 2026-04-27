import { Download, FileImage, FileVideo, ImageIcon } from "lucide-react";

import type { ExtractResponse, MediaItem } from "../types";

interface MediaResultProps {
  result: ExtractResponse;
}

export function MediaResult({ result }: MediaResultProps) {
  if (result.items.length === 0) {
    return <p className="empty-state">没有找到媒体。</p>;
  }

  return (
    <section className="results" aria-label="解析结果">
      <div className="result-header">
        <div>
          <p className="source">{result.author ? `@${result.author}` : "X/Twitter"}</p>
          <h2>{result.title || "媒体资源"}</h2>
        </div>
        <a className="source-link" href={result.source_url} target="_blank" rel="noreferrer">
          原帖
        </a>
      </div>

      <div className="media-list">
        {result.items.map((item) => (
          <MediaRow key={item.url} item={item} />
        ))}
      </div>
    </section>
  );
}

function MediaRow({ item }: { item: MediaItem }) {
  const icon =
    item.type === "image" ? (
      <ImageIcon aria-hidden="true" />
    ) : item.type === "gif" ? (
      <FileImage aria-hidden="true" />
    ) : (
      <FileVideo aria-hidden="true" />
    );

  return (
    <article className="media-item">
      <div className="media-icon">{icon}</div>
      <div className="media-body">
        <div className="media-line">
          <span className="media-type">{mediaTypeLabel(item.type)}</span>
          <strong>{item.quality}</strong>
          {item.ext ? <span className="pill">{item.ext.toUpperCase()}</span> : null}
        </div>
        <div className="media-meta">
          {dimensions(item)}
          {item.filesize ? <span>{formatBytes(item.filesize)}</span> : null}
        </div>
      </div>
      <a
        className="download-link"
        href={item.url}
        target="_blank"
        rel="noreferrer"
        aria-label="下载"
        title="下载"
      >
        <Download aria-hidden="true" />
        <span>下载</span>
      </a>
    </article>
  );
}

function mediaTypeLabel(type: MediaItem["type"]) {
  if (type === "image") {
    return "图片";
  }
  if (type === "gif") {
    return "GIF";
  }
  return "视频";
}

function dimensions(item: MediaItem) {
  if (!item.width || !item.height) {
    return null;
  }
  return <span>{item.width} x {item.height}</span>;
}

function formatBytes(bytes: number) {
  if (bytes >= 1024 * 1024) {
    return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
  }
  if (bytes >= 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${bytes} B`;
}
