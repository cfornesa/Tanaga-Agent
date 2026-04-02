import cors from "cors";
import express from "express";
import fs from "fs";
import path from "path";
import { getEnv } from "./config/env";
import { generateTanagaRouter } from "./routes/generateTanaga";
import { ragRouter } from "./routes/rag";

const env = getEnv();

export function buildApp() {
  const app = express();
  const publicDir = path.resolve(process.cwd(), "public");
  const staticDir = fs.existsSync(path.join(publicDir, "static"))
    ? path.join(publicDir, "static")
    : path.resolve(process.cwd(), "static");
  const indexFile = fs.existsSync(path.join(publicDir, "index.html"))
    ? path.join(publicDir, "index.html")
    : path.resolve(process.cwd(), "templates", "index.html");

  app.use(
    cors({
      origin: env.NODE_ENV === "production" ? env.APP_URL : true,
      methods: ["GET", "POST", "OPTIONS"],
    }),
  );

  app.use(express.json({ limit: "2mb" }));

  app.use("/static", express.static(staticDir));

  app.get("/", (_req, res) => {
    res.sendFile(indexFile);
  });

  app.get("/health", (_req, res) => {
    return res.json({
      status: "online",
      version: "10.0",
      env: env.NODE_ENV,
      appUrl: env.APP_URL,
      features: [
        "strict_meter_enforcement",
        "cultural_authenticity",
        "deterministic_generation",
        "local_doc_embeddings",
      ],
    });
  });

  app.use(generateTanagaRouter);
  app.use(ragRouter);

  return app;
}
