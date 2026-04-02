import { getEnv } from "../config/env";
import { MeterReport, PoetryResponse, SupportedLanguage } from "../types";

const env = getEnv();

const PII_PATTERNS: Record<string, RegExp> = {
  EMAIL: /[\w.-]+@[\w.-]+\.\w+/gi,
  PHONE: /\+?\d{1,4}?[-.\s]?\(?\d{1,3}?\)?[-.\s]?\d{1,4}/gi,
};

export function redactPii(text: string): string {
  return Object.entries(PII_PATTERNS).reduce((value, [label, pattern]) => {
    return value.replace(pattern, `[${label}_REDACTED]`);
  }, text);
}

export function heuristicSyllableCount(word: string): number {
  const clean = word.replace(/[^a-zA-Z\u00c0-\u017f]+/g, "");
  if (!clean) {
    return 0;
  }

  const vowels = new Set("aeiouyAEIOUY\u00e1\u00e9\u00ed\u00f3\u00fa\u00c1\u00c9\u00cd\u00d3\u00da".split(""));
  let previousVowel = false;
  let count = 0;

  for (const ch of clean) {
    const isVowel = vowels.has(ch);
    if (isVowel && !previousVowel) {
      count += 1;
    }
    previousVowel = isVowel;
  }

  const lower = clean.toLowerCase();
  if (lower.endsWith("e") && !lower.endsWith("le") && count > 1) {
    count -= 1;
  }

  return Math.max(count, 1);
}

export function countLineSyllables(line: string): number {
  const cleaned = line.replace(/[^\w\s'\u00c0-\u017f-]/g, "");
  return cleaned
    .split(/\s+/)
    .filter(Boolean)
    .reduce((sum, token) => sum + heuristicSyllableCount(token), 0);
}

export function validatePoemMeter(poemText: string, language: SupportedLanguage): MeterReport {
  const target = language === "Tagalog" ? 7 : 8;
  const lines = poemText
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean);

  let allMatch = true;
  const resultLines = lines.map((line, index) => {
    const syllables = countLineSyllables(line);
    const valid = syllables === target;
    if (!valid) {
      allMatch = false;
    }

    return {
      line_index: index,
      text: line,
      syllables,
      target,
      valid,
    };
  });

  return {
    lines: resultLines,
    all_match: allMatch,
    target,
  };
}

async function callMistralAgent(prompt: string): Promise<string> {
  const response = await fetch("https://api.mistral.ai/v1/agents/completions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${env.MISTRAL_API_KEY}`,
    },
    body: JSON.stringify({
      agent_id: env.AGENT_ID,
      messages: [{ role: "user", content: prompt }],
    }),
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(`Mistral API error (${response.status}): ${errorBody}`);
  }

  const data = (await response.json()) as {
    choices?: Array<{ message?: { content?: string | Array<{ text?: string }> } }>;
  };

  const content = data.choices?.[0]?.message?.content;
  if (typeof content === "string") {
    return content.trim();
  }

  if (Array.isArray(content) && typeof content[0]?.text === "string") {
    return content[0].text.trim();
  }

  return "";
}

export async function generatePoem(
  userInput: string,
  language: SupportedLanguage,
  retrievalContext?: string,
): Promise<PoetryResponse> {
  if (!env.MISTRAL_API_KEY || !env.AGENT_ID) {
    return { reply: "Error: API configuration missing" };
  }

  const safeInput = redactPii(userInput);
  const syllableCount = language === "Tagalog" ? "7" : "8";
  const contextBlock = retrievalContext
    ? `\nUse this local context when relevant:\n${retrievalContext}\n`
    : "";

  let replyText = "";
  let meterReport: MeterReport | null = null;

  for (let attempt = 0; attempt < 2; attempt += 1) {
    const prompt = [
      `Language: ${language}.`,
      `Write ONE ${language} poem about: ${safeInput}.`,
      `Each line MUST be exactly ${syllableCount} syllables.`,
      "Output ONLY the 4 lines of the poem. No title, no explanation.",
      contextBlock,
    ].join(" ");

    replyText = await callMistralAgent(prompt);
    if (!replyText) {
      continue;
    }

    meterReport = validatePoemMeter(replyText, language);
    if (meterReport.all_match) {
      break;
    }
  }

  if (!replyText) {
    return { reply: "Error: Empty response from poetry engine" };
  }

  return {
    reply: replyText,
    metadata: {
      language,
      status: "success",
      meter: meterReport,
      retrieval: {
        used: Boolean(retrievalContext),
        hits: retrievalContext ? 1 : 0,
      },
    },
  };
}
