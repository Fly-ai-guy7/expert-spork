import { describe, it, expect } from "vitest";
import en from "../i18n/en.json";
import ar from "../i18n/ar.json";

type JsonValue = string | { [k: string]: JsonValue };

function flatKeys(obj: { [k: string]: JsonValue }, prefix = ""): Set<string> {
  const out = new Set<string>();
  for (const [k, v] of Object.entries(obj)) {
    const key = prefix ? `${prefix}.${k}` : k;
    if (v !== null && typeof v === "object") {
      for (const child of flatKeys(v, key)) out.add(child);
    } else {
      out.add(key);
    }
  }
  return out;
}

describe("i18n key parity", () => {
  it("every en key has an ar counterpart and vice versa", () => {
    const enKeys = flatKeys(en as { [k: string]: JsonValue });
    const arKeys = flatKeys(ar as { [k: string]: JsonValue });
    const enOnly = [...enKeys].filter((k) => !arKeys.has(k));
    const arOnly = [...arKeys].filter((k) => !enKeys.has(k));
    expect(enOnly, "keys missing from ar.json").toEqual([]);
    expect(arOnly, "keys missing from en.json").toEqual([]);
  });

  it("no value is the empty string", () => {
    const flatValues = (obj: { [k: string]: JsonValue }, path = ""): [string, string][] => {
      const out: [string, string][] = [];
      for (const [k, v] of Object.entries(obj)) {
        const key = path ? `${path}.${k}` : k;
        if (typeof v === "string") out.push([key, v]);
        else if (v !== null && typeof v === "object") out.push(...flatValues(v, key));
      }
      return out;
    };
    const empties = [...flatValues(en as { [k: string]: JsonValue }), ...flatValues(ar as { [k: string]: JsonValue })].filter(
      ([, v]) => v.trim() === "",
    );
    expect(empties).toEqual([]);
  });
});
