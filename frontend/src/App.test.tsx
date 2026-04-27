import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";

import App from "./App";
import * as api from "./api";

describe("App", () => {
  it("requires a URL before extraction", async () => {
    render(<App />);

    fireEvent.click(screen.getByRole("button", { name: "解析媒体" }));

    expect(await screen.findByText("请先输入帖子链接。")).toBeInTheDocument();
  });

  it("renders returned media items", async () => {
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

    fireEvent.change(screen.getByLabelText("帖子链接"), {
      target: { value: "https://x.com/alice/status/1" }
    });
    fireEvent.click(screen.getByRole("button", { name: "解析媒体" }));

    await waitFor(() => {
      expect(screen.getByText("720p")).toBeInTheDocument();
    });
    expect(screen.getByRole("link", { name: "下载" })).toHaveAttribute(
      "href",
      "https://video.twimg.com/demo.mp4"
    );
  });
});
