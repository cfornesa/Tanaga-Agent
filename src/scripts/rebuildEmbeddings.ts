import { rebuildVectorIndex } from "../services/ragService";

async function main() {
  const result = await rebuildVectorIndex();
  console.log(`Indexed ${result.files} files into ${result.chunks} chunks.`);
}

main().catch((error) => {
  console.error("Failed to rebuild index:", error);
  process.exit(1);
});
