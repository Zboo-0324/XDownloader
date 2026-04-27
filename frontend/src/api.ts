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

async function readJsonResponse(response: FetchResponseLike): Promise<unknown> {
  try {
    return await response.json();
  } catch (error) {
    throw new ApiError(
      "INVALID_JSON_RESPONSE",
      "API 没有返回有效 JSON，请检查前端是否配置了正确的后端地址。"
    );
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

  const payload = (await readJsonResponse(response)) as ExtractResponse | ApiErrorBody;
  if (!response.ok) {
    const error = (payload as ApiErrorBody).error;
    throw new ApiError(
      error?.code ?? "REQUEST_FAILED",
      error?.message ?? "请求失败，请稍后重试。"
    );
  }

  return payload as ExtractResponse;
}
