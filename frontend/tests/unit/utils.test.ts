import { describe, expect, it } from "vitest";
import { formatScore, safeParseJSON } from "@/lib/utils";

describe("shared utilities", () => {
  it("formats a score consistently", () => { expect(formatScore(72.4)).toBe("72/100"); });
  it("returns a fallback for invalid JSON", () => { expect(safeParseJSON("not-json", { ready: false })).toEqual({ ready: false }); });
});
