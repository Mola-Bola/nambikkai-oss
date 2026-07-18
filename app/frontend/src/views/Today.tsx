import { useState } from "react";
import { EntryDraft, EntryKind, Persona, saveEntry } from "../api";
import Reflection from "./Reflection";

// All screen copy is layman-first (VISION · Audience & voice): no engine words,
// no em-dashes, plain sentences. Prompt phrasing follows the journaling
// research, not invention (research/2026-07-14-journal-grounding.md).

const PROMPTS: { field: "feeling" | "why" | "cause" | "helps"; label: string; hint: string }[] = [
  { field: "feeling", label: "How are you feeling?", hint: "the closest word you can find, even just one" },
  { field: "why", label: "Why, do you think?", hint: "no need to be sure" },
  { field: "cause", label: "Who or what brought it on?", hint: "a person, a pet, a place, a thing" },
  { field: "helps", label: "What helps, now or before?", hint: "even a small thing counts" },
];

// A wide vocabulary offered as suggestions, never as a fixed menu. Naming a
// feeling precisely is itself the regulating act (affect labelling), so the
// list exists to widen the user's reach, not to constrain it to our options.
const WORDS = [
  "glad", "proud", "excited", "hopeful", "grateful", "light", "free", "tense",
  "frustrated", "anxious", "overwhelmed", "irritated", "wound up", "calm",
  "content", "safe", "settled", "tired", "sad", "lonely", "flat", "resentful",
  "heavy", "homesick", "torn", "relieved", "curious", "numb", "warm", "seen",
  "small", "steady",
];

const EMPTY: EntryDraft = {
  kind: "guided",
  feeling: "",
  why: "",
  cause: "",
  helps: "",
  body: "",
  persona_ids: [],
};

export default function Today({
  people,
  onSaved,
  questionsOn,
}: {
  people: Persona[];
  onSaved: () => void;
  questionsOn: boolean;
}) {
  const [draft, setDraft] = useState<EntryDraft>({ ...EMPTY });
  const [choiceNeeded, setChoiceNeeded] = useState<string[] | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const field = (f: keyof EntryDraft, v: string) => setDraft((d) => ({ ...d, [f]: v }));
  const tagged = draft.persona_ids ?? [];

  const suggestions = (() => {
    const typed = (draft.feeling ?? "").toLowerCase().trim();
    if (!typed) return ["glad", "tense", "calm", "tired", "homesick"];
    return WORDS.filter((w) => w.startsWith(typed) && w !== typed).slice(0, 5);
  })();

  const hasWords =
    draft.kind === "guided"
      ? PROMPTS.some((p) => (draft[p.field] ?? "").trim() !== "")
      : (draft.body ?? "").trim() !== "";

  function togglePerson(id: string) {
    setDraft((d) => {
      const ids = d.persona_ids ?? [];
      return {
        ...d,
        persona_ids: ids.includes(id) ? ids.filter((x) => x !== id) : [...ids, id],
      };
    });
  }

  async function submit(privacy?: "keep" | "blur") {
    setSaving(true);
    setError(null);
    try {
      const result = await saveEntry({ ...draft, privacy_choice: privacy });
      if (!result.saved) {
        setChoiceNeeded(result.found ?? []);
        return;
      }
      setChoiceNeeded(null);
      setDraft({ ...EMPTY, kind: draft.kind });
      setToast("Kept. Your words stay here.");
      setTimeout(() => setToast(null), 3500);
      onSaved();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSaving(false);
    }
  }

  const setMode = (kind: EntryKind) => {
    setChoiceNeeded(null);
    setDraft((d) => ({ ...d, kind }));
  };

  return (
    <>
      <h1>Today</h1>
      <p className="sub">Write it how it comes. Mess is fine.</p>

      <section className="card">
        <div className="tabs" role="tablist">
          <button
            role="tab"
            aria-selected={draft.kind === "guided"}
            className={draft.kind === "guided" ? "tab active" : "tab"}
            onClick={() => setMode("guided")}
          >
            Guided
          </button>
          <button
            role="tab"
            aria-selected={draft.kind === "free"}
            className={draft.kind === "free" ? "tab active" : "tab"}
            onClick={() => setMode("free")}
          >
            Free write
          </button>
        </div>

        <div className="mode-body" key={draft.kind}>
          {draft.kind === "guided" ? (
            <>
              <p className="intro">A few gentle prompts. Follow any that fit, and leave the rest.</p>
              {PROMPTS.map((p) => (
                <label key={p.field} className="prompt">
                  <span>{p.label}</span>
                  <textarea
                    rows={2}
                    value={draft[p.field] ?? ""}
                    placeholder={p.hint}
                    onChange={(e) => field(p.field, e.target.value)}
                  />
                  {p.field === "feeling" && suggestions.length > 0 && (
                    <div className="words">
                      {suggestions.map((w) => (
                        <button key={w} type="button" className="chip" onClick={() => field("feeling", w)}>
                          {w}
                        </button>
                      ))}
                      <span className="whisper">Suggestions, not a menu. Yours wins.</span>
                    </div>
                  )}
                </label>
              ))}
            </>
          ) : (
            <>
              <p className="intro">Write anything, any shape. The mess is fine.</p>
              <textarea
                className="freebox"
                rows={10}
                value={draft.body ?? ""}
                placeholder="It doesn't have to make sense to anyone. Not even you, not yet."
                onChange={(e) => field("body", e.target.value)}
              />
            </>
          )}
        </div>

        {people.length > 0 && (
          <div className="tagrow">
            <span className="whisper">Anyone or anything part of this?</span>
            <div className="words">
              {people.map((p) => (
                <button
                  key={p.id}
                  type="button"
                  className={tagged.includes(p.id) ? "chip on" : "chip"}
                  onClick={() => togglePerson(p.id)}
                >
                  {p.name}
                </button>
              ))}
            </div>
          </div>
        )}

        {choiceNeeded ? (
          <div className="privacy-card" role="alertdialog" aria-label="Before this is kept">
            <p>
              This entry looks like it has {choiceNeeded.join(" and ")} in it. Your journal doesn't
              need that to remember the day, and either way, nothing leaves this computer.
            </p>
            <div className="choices">
              <button onClick={() => submit("blur")} disabled={saving}>
                Blur it
              </button>
              <button className="ghost" onClick={() => submit("keep")} disabled={saving}>
                Keep as written
              </button>
            </div>
          </div>
        ) : (
          <button className="keep" onClick={() => submit()} disabled={!hasWords || saving}>
            {saving ? "Keeping…" : "Keep this"}
          </button>
        )}

        {/* Appears only after a pause in writing, and only as a line to click.
            Nothing here interrupts a sentence in progress. */}
        <Reflection
          draft={
            draft.kind === "guided"
              ? PROMPTS.map((p) => draft[p.field] ?? "").join(" ")
              : draft.body ?? ""
          }
          people={people}
          questionsOn={questionsOn}
          onAnswered={onSaved}
        />

        {toast && <p className="toast">{toast}</p>}
        {error && <p className="error">{error}</p>}
      </section>
    </>
  );
}
