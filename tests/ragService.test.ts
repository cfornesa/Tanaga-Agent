import assert from "node:assert/strict";
import test, { before } from "node:test";

let ragService: typeof import("../src/services/ragService");

before(async () => {
  ragService = await import("../src/services/ragService");
});

test("rebuilds index from documents", async () => {
  const result = await ragService.rebuildVectorIndex();
  assert.equal(result.files >= 1, true);
  assert.equal(result.chunks >= 1, true);

  const status = await ragService.getIndexStatus();
  assert.equal(status.exists, true);
  assert.equal(status.chunks >= 1, true);
});

test("retrieves relevant context for a query", async () => {
  const context = await ragService.retrieveContext("tanaga guide and syllables");
  assert.equal(typeof context, "string");
  assert.ok(context.length > 0);
});
