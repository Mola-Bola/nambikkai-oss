// Typed client for the local API. Everything talks to 127.0.0.1 — nothing else.

export type EntryKind = "guided" | "free";

export interface Entry {
  id: string;
  at: string; // UTC ISO
  kind: EntryKind;
  feeling?: string;
  why?: string;
  cause?: string;
  helps?: string;
  body?: string;
  blurred: boolean;
}

export interface ChainState {
  ok: boolean;
  count: number;
  broken_at: number | null;
}

export interface EntryDraft {
  kind: EntryKind;
  feeling: string;
  why: string;
  cause: string;
  helps: string;
  body: string;
  privacy_choice?: "keep" | "blur";
}

export type SaveResult =
  | { saved: true; entry: Entry; chain: ChainState }
  | { saved: false; needs_choice: true; found: string[] };

export async function saveEntry(draft: EntryDraft): Promise<SaveResult> {
  const res = await fetch("/api/entries", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(draft),
  });
  if (!res.ok) {
    const detail = (await res.json().catch(() => null))?.detail;
    throw new Error(detail ?? "Couldn't save — is the app still running?");
  }
  return res.json();
}

export async function listEntries(): Promise<{ entries: Entry[]; chain: ChainState }> {
  const res = await fetch("/api/entries");
  if (!res.ok) throw new Error("Couldn't load your journal.");
  return res.json();
}
