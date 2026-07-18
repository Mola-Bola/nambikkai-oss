// Typed client for the local API. Everything talks to 127.0.0.1, nothing else.
//
// The types below are DERIVED from api-types.ts, which is generated from
// FastAPI's OpenAPI schema (`make api-types`). Don't hand-edit shapes here: if
// the backend renames a field, regenerating makes this file fail to compile,
// which is the entire point (FOUNDATIONS item 6).
import type { components } from "./api-types";

type S = components["schemas"];

export type Entry = S["EntryOut"];
export type Persona = S["PersonaOut"];
export type Truth = S["TruthOut"];
export type LooseEnd = S["LooseEndOut"];
export type TimelineRow = S["TimelineRow"];
export type ChainState = S["ChainState"];
export type EntryDraft = S["EntryIn"];
export type PersonaDraft = S["PersonaIn"];
export type TruthDraft = S["TruthIn"];
export type SaveResult = S["SaveOut"];
export type EntriesResult = S["EntriesOut"];
export type ThreadResult = S["ThreadOut"];
export type YouResult = S["YouOut"];
export type ImportResult = S["ImportOut"];
export type HealthResult = S["HealthOut"];
export type EntryKind = EntryDraft["kind"];
export type RelatedResult = S["RelatedOut"];
export type RelatedEntry = S["RelatedEntry"];
export type ReflectionSettings = S["ReflectionSettings"];
export type Diary = S["DiaryOut"];
export type DiaryLoadResult = S["DiaryLoadOut"];

async function call<T>(url: string, init?: RequestInit, fallback = "Something didn't work."): Promise<T> {
  const res = await fetch(url, {
    ...init,
    headers: init?.body ? { "Content-Type": "application/json", ...init?.headers } : init?.headers,
  });
  if (!res.ok) {
    const detail = (await res.json().catch(() => null))?.detail;
    throw new Error(typeof detail === "string" ? detail : fallback);
  }
  return res.json();
}

const post = (body?: unknown): RequestInit => ({
  method: "POST",
  body: body === undefined ? undefined : JSON.stringify(body),
});

export const getHealth = () => call<HealthResult>("/api/health");

export const listEntries = () =>
  call<EntriesResult>("/api/entries", undefined, "Couldn't load your journal.");

export const saveEntry = (draft: EntryDraft) =>
  call<SaveResult>("/api/entries", post(draft), "Couldn't save. Is the app still running?");

export const listPersonas = () => call<Persona[]>("/api/personas");

export const createPersona = (p: PersonaDraft) => call<Persona>("/api/personas", post(p));

export const updatePersona = (id: string, p: PersonaDraft) =>
  call<Persona>(`/api/personas/${id}`, { method: "PUT", body: JSON.stringify(p) });

export const getThread = (id: string) => call<ThreadResult>(`/api/personas/${id}/thread`);

export const listTruths = () => call<Truth[]>("/api/truths");

export const createTruth = (t: TruthDraft) => call<Truth>("/api/truths", post(t));

export const listLooseEnds = () => call<LooseEnd[]>("/api/loose-ends");

export const answerLooseEnd = (id: string, action: "added" | "dismissed") =>
  call<LooseEnd[]>(`/api/loose-ends/${id}`, post({ action }));

export const importText = (text: string) =>
  call<ImportResult>("/api/import", post({ text }), "Couldn't read that.");

export const getYou = () => call<YouResult>("/api/you");

export const loadDemo = () => call<{ loaded: boolean }>("/api/demo/load", post());

export const wipeDemo = () => call<{ removed: number }>("/api/demo/wipe", post());

// The optional real-diary demo set. Empty until `make demo-diary` has been run,
// because the source text is gitignored and converted at build time.
export const listDiaries = () => call<Diary[]>("/api/demo/diaries");

export const loadDiary = (name: string) =>
  call<DiaryLoadResult>(`/api/demo/diaries/${name}`, post());

// --- reflection (ADR 003) ---------------------------------------------------
// These return the user's own records and a score. There is no endpoint here
// that returns a generated sentence, because none exists to call.

export const getRelated = (entryId: string) =>
  call<RelatedResult>(`/api/reflection/related/${entryId}`);

export const getRelatedToDraft = (text: string) =>
  call<RelatedResult>("/api/reflection/related", post({ text }));

export const getReflectionSettings = () =>
  call<ReflectionSettings>("/api/reflection/settings");

export const setQuestionsOn = (questionsOn: boolean) =>
  call<ReflectionSettings>("/api/reflection/settings", {
    method: "PUT",
    body: JSON.stringify({ questions_on: questionsOn }),
  });

export async function exportBundle(): Promise<unknown> {
  return call<unknown>("/api/export");
}

// The orientation before the first entry. Marked seen whether it is read or
// skipped: waving it off is a real answer and must stick.
export const markGuideSeen = () => call<{ seen: boolean }>("/api/guide/seen", post());
