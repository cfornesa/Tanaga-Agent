import { Router } from "express";
import { z } from "zod";
import { generatePoem } from "../services/poetryService";
import { retrieveContext } from "../services/ragService";

const requestSchema = z.object({
  user_input: z.string().min(1),
  language: z.enum(["Tagalog", "English"]).default("Tagalog"),
  history: z.array(z.record(z.any())).optional(),
});

export const generateTanagaRouter = Router();

generateTanagaRouter.post("/generate-tanaga", async (req, res) => {
  const parsed = requestSchema.safeParse(req.body);

  if (!parsed.success) {
    return res.status(400).json({
      reply: "Error: Invalid request payload",
      details: parsed.error.flatten(),
    });
  }

  try {
    const context = await retrieveContext(parsed.data.user_input);
    const response = await generatePoem(
      parsed.data.user_input,
      parsed.data.language,
      context,
    );

    return res.json(response);
  } catch (error) {
    const message = error instanceof Error ? error.message : "Unknown error";
    return res.status(500).json({ reply: `System Error: ${message}` });
  }
});
