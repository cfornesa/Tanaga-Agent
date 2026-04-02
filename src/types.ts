export type SupportedLanguage = "Tagalog" | "English";

export interface PoetryRequest {
  user_input: string;
  language?: SupportedLanguage;
  history?: Record<string, unknown>[];
}

export interface MeterLineReport {
  line_index: number;
  text: string;
  syllables: number;
  target: number;
  valid: boolean;
}

export interface MeterReport {
  lines: MeterLineReport[];
  all_match: boolean;
  target: number;
}

export interface PoetryResponse {
  reply: string;
  metadata?: {
    language: SupportedLanguage;
    status: "success";
    meter: MeterReport | null;
    retrieval?: {
      used: boolean;
      hits: number;
    };
  };
}

export interface IndexedChunk {
  id: string;
  sourceFile: string;
  text: string;
  vector: number[];
}

export interface VectorIndex {
  version: number;
  generatedAt: string;
  dimensions: number;
  chunks: IndexedChunk[];
}
