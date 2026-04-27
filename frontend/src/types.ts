export type MediaType = "video" | "gif" | "image";

export interface MediaItem {
  type: MediaType;
  url: string;
  quality: string;
  ext: string | null;
  width: number | null;
  height: number | null;
  filesize: number | null;
}

export interface ExtractResponse {
  title: string | null;
  author: string | null;
  thumbnail: string | null;
  source_url: string;
  items: MediaItem[];
}

export interface ApiErrorBody {
  error?: {
    code?: string;
    message?: string;
  };
}
