import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";

import App from "./App";
import * as api from "./api";

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
});

describe("App", () => {
  it("requires a URL before extraction", async () => {
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: "解析" }));

    expect(await screen.findByText("请先输入帖子链接。")).toBeInTheDocument();
  });

  it("shows guidance while extraction is loading", async () => {
    vi.spyOn(api, "extractMedia").mockReturnValue(new Promise(() => {}));

    render(<App />);

    fireEvent.change(screen.getByLabelText("X/Twitter 链接"), {
      target: { value: "https://x.com/alice/status/1" }
    });
    fireEvent.click(screen.getByRole("button", { name: "解析" }));

    expect(
      await screen.findByText("正在解析，Render 免费服务首次唤醒可能需要几十秒。")
    ).toBeInTheDocument();
  });

  it("renders returned media items with download and open actions", async () => {
    vi.spyOn(api, "extractMedia").mockResolvedValue({
      title: "Demo",
      author: "alice",
      thumbnail: null,
      source_url: "https://x.com/alice/status/1",
      items: [
        {
          type: "video",
          url: "https://video.twimg.com/demo.mp4",
          quality: "720p",
          ext: "mp4",
          width: 1280,
          height: 720,
          filesize: null
        }
      ]
    });

    render(<App />);

    fireEvent.change(screen.getByLabelText("X/Twitter 链接"), {
      target: { value: "https://x.com/alice/status/1" }
    });
    fireEvent.click(screen.getByRole("button", { name: "解析" }));

    await waitFor(() => {
      expect(screen.getByText("720p")).toBeInTheDocument();
    });
    expect(screen.getByRole("link", { name: "下载 720p MP4" })).toHaveAttribute(
      "href",
      "https://video.twimg.com/demo.mp4"
    );
    expect(screen.getByRole("link", { name: "打开 720p MP4" })).toHaveAttribute(
      "href",
      "https://video.twimg.com/demo.mp4"
    );
  });
});
