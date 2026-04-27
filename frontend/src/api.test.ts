import { afterEach, describe, expect, it, vi } from "vitest";

import { extractMedia } from "./api";

afterEach(() => {
  vi.unstubAllEnvs();
});

describe("extractMedia", () => {
  it("posts the URL and returns media response", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        title: "Demo",
        author: "alice",
        thumbnail: null,
        source_url: "https://x.com/alice/status/1",
        items: []
      })
    });

    const result = await extractMedia("https://x.com/alice/status/1", fetchMock);

    expect(fetchMock).toHaveBeenCalledWith("/api/extract", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: "https://x.com/alice/status/1" })
    });
    expect(result.title).toBe("Demo");
  });

  it("posts to the configured API base URL when provided", async () => {
    vi.stubEnv("VITE_API_BASE_URL", "https://xdownloader-api-cyge.onrender.com");
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        title: "Demo",
        author: "alice",
        thumbnail: null,
        source_url: "https://x.com/alice/status/1",
        items: []
      })
    });

    await extractMedia("https://x.com/alice/status/1", fetchMock);

    expect(fetchMock).toHaveBeenCalledWith(
      "https://xdownloader-api-cyge.onrender.com/api/extract",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: "https://x.com/alice/status/1" })
      }
    );
  });

  it("throws the structured API error message", async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: false,
      json: async () => ({
        error: { code: "NO_MEDIA", message: "没有找到可下载的媒体。" }
      })
    });

    await expect(
      extractMedia("https://x.com/alice/status/1", fetchMock)
    ).rejects.toThrow("没有找到可下载的媒体。");
  });
});
