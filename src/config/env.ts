import dotenv from "dotenv";
import { z } from "zod";

dotenv.config();

const envSchema = z.object({
  NODE_ENV: z.enum(["development", "production"]).default("development"),
  PORT: z.coerce.number().int().positive().default(5000),
  MISTRAL_API_KEY: z.string().min(1, "MISTRAL_API_KEY is required"),
  AGENT_ID: z.string().min(1, "AGENT_ID is required"),
  APP_URL: z
    .string()
    .url("APP_URL must be a valid URL")
    .refine((url) => url.startsWith("https://"), "APP_URL must start with https://"),
});

export type AppEnv = z.infer<typeof envSchema>;

export function getEnv(): AppEnv {
  const parsed = envSchema.safeParse(process.env);

  if (parsed.success) {
    return parsed.data;
  }

  const isProd = process.env.NODE_ENV === "production";

  if (!isProd) {
    const devFallback = {
      NODE_ENV: "development" as const,
      PORT: Number(process.env.PORT ?? 5000),
      MISTRAL_API_KEY: process.env.MISTRAL_API_KEY ?? "",
      AGENT_ID: process.env.AGENT_ID ?? "",
      APP_URL: process.env.APP_URL ?? "https://localhost.localdomain",
    };

    return devFallback;
  }

  const errors = parsed.error.issues
    .map((issue) => `${issue.path.join(".")}: ${issue.message}`)
    .join("; ");
  throw new Error(`Invalid environment configuration: ${errors}`);
}
