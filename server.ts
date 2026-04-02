import { buildApp } from "./src/app";
import { getEnv } from "./src/config/env";

const env = getEnv();
const app = buildApp();

app.listen(env.PORT, "0.0.0.0", () => {
  console.log(`Tanaga Agent running on port ${env.PORT} in ${env.NODE_ENV} mode`);
});
