import type { ApiErrorBody, ExtractResponse } from "./types";

interface FetchResponseLike {
  ok: boolean;
  json: () => Promise<unknown>;
}

type FetchLike = (
  input: string,
  init: {
    method: string;
    headers: Record<string, string>;
    body: string;
  }
) => Promise<FetchResponseLike>;

export class ApiError extends Error {
  code: string;

  constructor(code: string, message: string) {
    super(message);
    this.name = "ApiError";
    this.code = code;
  }
}

function buildApiUrl(path: string): string {
  const baseUrl = import.meta.env.VITE_API_BASE_URL?.replace(/\/+$/, "") ?? "";
  return `${baseUrl}${path}`;
}

export async function extractMedia(
  url: string,
  fetcher: FetchLike = fetch
): Promise<ExtractResponse> {
  const response = await fetcher(buildApiUrl("/api/extract"), {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url })
  });

  const payload = (await response.json()) as ExtractResponse | ApiErrorBody;
  if (!response.ok) {
    const error = (payload as ApiErrorBody).error;
    throw new ApiError(
      error?.code ?? "REQUEST_FAILED",
      error?.message ?? "请求失败，请稍后重试。"
    );
  }

  return payload as ExtractResponse;
}
