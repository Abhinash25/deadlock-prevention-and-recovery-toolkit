import express from "express";
import { createServer as createViteServer } from "vite";
import { 
  bankersSafetyCheck, 
  detectDeadlock, 
  recoverDeadlock, 
  runSimulation 
} from "./src/lib/algorithms";

async function startServer() {
  const app = express();
  const PORT = 3000;

  app.use(express.json());

  // API Routes
  app.post("/api/bankers/safety-check", (req, res) => {
    try {
      const result = bankersSafetyCheck(req.body);
      res.json(result);
    } catch (error: any) {
      res.status(400).json({ error: error.message });
    }
  });

  app.post("/api/deadlock/detect", (req, res) => {
    try {
      const result = detectDeadlock(req.body);
      res.json(result);
    } catch (error: any) {
      res.status(400).json({ error: error.message });
    }
  });

  app.post("/api/deadlock/recover", (req, res) => {
    try {
      const result = recoverDeadlock(req.body);
      res.json(result);
    } catch (error: any) {
      res.status(400).json({ error: error.message });
    }
  });

  app.post("/api/simulation/run", (req, res) => {
    try {
      const result = runSimulation(req.body);
      res.json(result);
    } catch (error: any) {
      res.status(400).json({ error: error.message });
    }
  });

  // Vite middleware for development
  if (process.env.NODE_ENV !== "production") {
    const vite = await createViteServer({
      server: { middlewareMode: true },
      appType: "spa",
    });
    app.use(vite.middlewares);
  } else {
    app.use(express.static("dist"));
  }

  app.listen(PORT, "0.0.0.0", () => {
    console.log(`Server running on http://localhost:${PORT}`);
  });
}

startServer();
