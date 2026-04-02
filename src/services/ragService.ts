import fs from "fs/promises";
import path from "path";
import mammoth from "mammoth";
import pdf from "pdf-parse";
import { IndexedChunk, VectorIndex } from "../types";

const DOCUMENTS_DIR = path.resolve(process.cwd(), "documents");
const INDEX_DIR = path.resolve(process.cwd(), ".data");
const INDEX_FILE = path.join(INDEX_DIR, "vector-index.json");
const DIMENSIONS = 256;
const CHUNK_SIZE = 900;
const CHUNK_OVERLAP = 120;

interface ParsedDocument {
  fileName: string;
  text: string;
}

function normalizeText(text: string): string {
  return text.replace(/\s+/g, " ").trim();
}

function chunkText(text: string): string[] {
  const chunks: string[] = [];
  let start = 0;

  while (start < text.length) {
    const end = Math.min(start + CHUNK_SIZE, text.length);
    chunks.push(text.slice(start, end).trim());
    if (end === text.length) {
      break;
    }
    start = Math.max(0, end - CHUNK_OVERLAP);
  }

  return chunks.filter(Boolean);
}

function hashToken(token: string): number {
  let hash = 2166136261;
  for (let i = 0; i < token.length; i += 1) {
    hash ^= token.charCodeAt(i);
    hash +=
      (hash << 1) + (hash << 4) + (hash << 7) + (hash << 8) + (hash << 24);
  }
  return Math.abs(hash >>> 0);
}

function tokenize(text: string): string[] {
  return text
    .toLowerCase()
    .replace(/[^\p{L}\p{N}\s]/gu, " ")
    .split(/\s+/)
    .filter((token) => token.length > 2);
}

function embedText(text: string): number[] {
  const tokens = tokenize(text);
  const vector = Array.from({ length: DIMENSIONS }, () => 0);

  for (const token of tokens) {
    const index = hashToken(token) % DIMENSIONS;
    vector[index] += 1;
  }

  const norm = Math.sqrt(vector.reduce((sum, value) => sum + value * value, 0)) || 1;
  return vector.map((value) => value / norm);
}

function cosineSimilarity(a: number[], b: number[]): number {
  let sum = 0;
  for (let i = 0; i < a.length; i += 1) {
    sum += a[i] * b[i];
  }
  return sum;
}

async function parsePdf(filePath: string): Promise<string> {
  const buffer = await fs.readFile(filePath);
  try {
    const parsed = await pdf(buffer);
    return parsed.text ?? "";
  } catch {
    // pdf-parse may fail for some files depending on parser/runtime compatibility.
    const pdfjs = await import("pdfjs-dist/legacy/build/pdf.mjs");
    const loadingTask = pdfjs.getDocument({ data: new Uint8Array(buffer) });
    const document = await loadingTask.promise;
    const pages: string[] = [];

    for (let pageNum = 1; pageNum <= document.numPages; pageNum += 1) {
      const page = await document.getPage(pageNum);
      const textContent = await page.getTextContent();
      const pageText = textContent.items
        .map((item) => ("str" in item ? item.str : ""))
        .join(" ");
      pages.push(pageText);
    }

    return pages.join("\n");
  }
}

async function parseDocx(filePath: string): Promise<string> {
  const result = await mammoth.extractRawText({ path: filePath });
  return result.value ?? "";
}

async function parseDocuments(): Promise<ParsedDocument[]> {
  const entries = await fs.readdir(DOCUMENTS_DIR, { withFileTypes: true });
  const docs = entries.filter((entry) => entry.isFile());

  const parsedDocs: ParsedDocument[] = [];

  for (const doc of docs) {
    const ext = path.extname(doc.name).toLowerCase();
    const fullPath = path.join(DOCUMENTS_DIR, doc.name);

    try {
      if (ext === ".pdf") {
        const text = normalizeText(await parsePdf(fullPath));
        if (text) {
          parsedDocs.push({ fileName: doc.name, text });
        }
      } else if (ext === ".docx") {
        const text = normalizeText(await parseDocx(fullPath));
        if (text) {
          parsedDocs.push({ fileName: doc.name, text });
        }
      }
    } catch (error) {
      // Parsing errors should not break indexing for the rest of documents.
      console.warn(`Failed to parse ${doc.name}:`, error);
    }
  }

  return parsedDocs;
}

export async function rebuildVectorIndex(): Promise<{ chunks: number; files: number }> {
  await fs.mkdir(INDEX_DIR, { recursive: true });
  const docs = await parseDocuments();

  const chunks: IndexedChunk[] = [];

  for (const doc of docs) {
    const parts = chunkText(doc.text);
    parts.forEach((part, index) => {
      chunks.push({
        id: `${doc.fileName}::${index}`,
        sourceFile: doc.fileName,
        text: part,
        vector: embedText(part),
      });
    });
  }

  const index: VectorIndex = {
    version: 1,
    generatedAt: new Date().toISOString(),
    dimensions: DIMENSIONS,
    chunks,
  };

  await fs.writeFile(INDEX_FILE, JSON.stringify(index, null, 2), "utf8");

  return {
    chunks: chunks.length,
    files: docs.length,
  };
}

export async function getIndexStatus(): Promise<{ exists: boolean; chunks: number; generatedAt: string | null }> {
  try {
    const raw = await fs.readFile(INDEX_FILE, "utf8");
    const parsed = JSON.parse(raw) as VectorIndex;
    return {
      exists: true,
      chunks: parsed.chunks.length,
      generatedAt: parsed.generatedAt,
    };
  } catch {
    return {
      exists: false,
      chunks: 0,
      generatedAt: null,
    };
  }
}

async function loadIndex(): Promise<VectorIndex | null> {
  try {
    const raw = await fs.readFile(INDEX_FILE, "utf8");
    return JSON.parse(raw) as VectorIndex;
  } catch {
    return null;
  }
}

export async function retrieveContext(query: string, topK = 3): Promise<string> {
  const index = await loadIndex();
  if (!index || !index.chunks.length) {
    return "";
  }

  const queryVector = embedText(query);
  const ranked = index.chunks
    .map((chunk) => ({
      chunk,
      score: cosineSimilarity(queryVector, chunk.vector),
    }))
    .sort((a, b) => b.score - a.score)
    .slice(0, topK)
    .filter((result) => result.score > 0.08);

  return ranked
    .map((result, idx) => `Source ${idx + 1} (${result.chunk.sourceFile}): ${result.chunk.text}`)
    .join("\n\n");
}
