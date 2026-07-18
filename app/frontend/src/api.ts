// Typed client for the local API. Everything talks to 127.0.0.1, nothing else.
//
// The types below are DERIVED from api-types.ts, which is generated from
// FastAPI's OpenAPI schema (`make api-types`). Don't hand-edit shapes here: if
// the backend renames a field, regenerating makes this file fail to compile,
// which is the entire point (FOUNDATIONS item 6).
import type { components } from "./api-types";

export type Entry = components["schemas"]["EntryOut"];
export type ChainState = components["schemas"]["ChainState"];
export type EntryDraft = components["schemas"]["EntryIn"];
export type SaveResult = components["schemas"]["SaveOut"];
export type EntriesResult = components["schemas"]["EntriesOut"];
export type EntryKind = EntryDraft["kind"];

async function readError(res: Response, fallback: string): Promise<string> {
  const detail = (await res.json().catch(() => null))?.detail;
  return typeof detail === "string" ? detail : fallback;
}

export async function saveEntry(draft: EntryDraft): Promise<SaveResult> {
  const res = await fetch("/api/entries", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(draft),
  });
  if (!res.ok) {
    throw new Error(await readError(res, "Couldn't save. Is the app still running?"));
  }
  return res.json();
}

export async function listEntries(): Promise<EntriesResult> {
  const res = await fetch("/api/entries");
  if (!res.ok) {
    throw new Error(await readError(res, "Couldn't load your journal."));
  }
  return res.json();
}
