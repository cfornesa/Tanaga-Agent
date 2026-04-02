import { Router } from "express";
import { getIndexStatus, rebuildVectorIndex } from "../services/ragService";

export const ragRouter = Router();

ragRouter.get("/rag/status", async (_req, res) => {
  const status = await getIndexStatus();
  return res.json(status);
});

ragRouter.post("/rag/rebuild", async (_req, res) => {
  try {
    const result = await rebuildVectorIndex();
    return res.json({
      status: "ok",
      message: "Vector index rebuilt successfully",
      ...result,
    });
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    return res.status(500).json({
      status: "error",
      message,
    });
  }
});
