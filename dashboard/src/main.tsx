import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import * as Sentry from "@sentry/react";
import "./index.css";
import App from "./App.tsx";

if (import.meta.env.VITE_SENTRY_DSN) {
  Sentry.init({
    dsn: import.meta.env.VITE_SENTRY_DSN,
    integrations: [Sentry.browserTracingIntegration()],
    sendDefaultPii: true,
    tracesSampleRate: 1.0,
    enableLogs: true,
  });
}

const AppWithErrorBoundary = Sentry.withErrorBoundary(App, {
  fallback: <div>Something went wrong while loading the dashboard.</div>,
  onError(error) {
    console.error("Dashboard render error:", error);
  },
});

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <AppWithErrorBoundary />
  </StrictMode>,
);
