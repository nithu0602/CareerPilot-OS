type LogContext = Record<string, unknown>;
const isDevelopment = process.env.NODE_ENV === "development";
function write(level: "info" | "warn" | "error" | "debug", message: string, context?: LogContext) { if (level === "debug" && !isDevelopment) return; const payload = context ? { message, ...context } : { message }; if (isDevelopment) console[level](payload); else console[level](message); }
export const logger = { info: (message: string, context?: LogContext) => write("info", message, context), warn: (message: string, context?: LogContext) => write("warn", message, context), error: (message: string, context?: LogContext) => write("error", message, context), debug: (message: string, context?: LogContext) => write("debug", message, context) };
