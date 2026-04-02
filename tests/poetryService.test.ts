import assert from "node:assert/strict";
import test, { before } from "node:test";

process.env.NODE_ENV = process.env.NODE_ENV ?? "development";
process.env.MISTRAL_API_KEY = process.env.MISTRAL_API_KEY ?? "test-key";
process.env.AGENT_ID = process.env.AGENT_ID ?? "test-agent";
process.env.APP_URL = process.env.APP_URL ?? "https://localhost.localdomain";

let poetryService: typeof import("../src/services/poetryService");

before(async () => {
  poetryService = await import("../src/services/poetryService");
});

test("redacts email and phone numbers", () => {
  const output = poetryService.redactPii("Reach me at user@example.com or +1 555 123 4567.");
  assert.match(output, /\[EMAIL_REDACTED\]/);
  assert.match(output, /\[PHONE_REDACTED\]/);
});

test("counts syllables and validates meter", () => {
  assert.equal(poetryService.countLineSyllables("banana"), 3);

  const meter = poetryService.validatePoemMeter(
    "Araw sa Manila Bay\nHangin sa dagat ay malamig\nPusong umaawit pa rin\nSa alaala ng bukas",
    "Tagalog",
  );

  assert.equal(meter.target, 7);
  assert.equal(meter.lines.length, 4);
  assert.equal(typeof meter.all_match, "boolean");
});

test("returns structured metadata from a mocked Mistral response", async () => {
  const originalFetch = globalThis.fetch;

  globalThis.fetch = (async () => ({
    ok: true,
    json: async () => ({
      choices: [
        {
          message: {
            content: "Morning light across the quiet sea\nSoft winds move through the bamboo grove\nCareful hands arrange the day\nThe harbor keeps its patient song",
          },
        },
      ],
    }),
    text: async () => "",
  })) as typeof fetch;

  try {
    const result = await poetryService.generatePoem("test theme", "English");

    assert.equal(typeof result.reply, "string");
    assert.equal(result.metadata?.language, "English");
    assert.equal(result.metadata?.status, "success");
    assert.equal(result.metadata?.retrieval?.used, false);
  } finally {
    globalThis.fetch = originalFetch;
  }
});
