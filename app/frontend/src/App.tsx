import { useCallback, useEffect, useState } from "react";
import {
  ChainState,
  Entry,
  EntryDraft,
  EntryKind,
  listEntries,
  saveEntry,
} from "./api";

// All screen copy is layman-first (VISION · Audience & voice). Engine words —
// ledger, chain, provenance, redaction — never appear below this line.

const GUIDED_PROMPTS: {
  field: "feeling" | "why" | "cause" | "helps";
  label: string;
  hint: string;
}[] = [
  { field: "feeling", label: "How are you feeling?", hint: "the closest word you can find, even just one" },
  { field: "why", label: "Why, do you think?", hint: "no need to be sure" },
  { field: "cause", label: "Who or what brought it on?", hint: "a person, a pet, a place, a thing" },
  { field: "helps", label: "What helps, now or before?", hint: "even a small thing counts" },
];

const EMPTY_DRAFT: EntryDraft = {
  kind: "guided",
  feeling: "",
  why: "",
  cause: "",
  helps: "",
  body: "",
};

function friendlyDate(utcIso: string): string {
  return new Date(utcIso).toLocaleString(undefined, {
    day: "numeric",
    month: "long",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export default function App() {
  const [draft, setDraft] = useState<EntryDraft>({ ...EMPTY_DRAFT });
  const [entries, setEntries] = useState<Entry[]>([]);
  const [chain, setChain] = useState<ChainState | null>(null);
  const [choiceNeeded, setChoiceNeeded] = useState<string[] | null>(null);
  const [toast, setToast] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  const refresh = useCallback(async () => {
    try {
      const { entries, chain } = await listEntries();
      setEntries(entries);
      setChain(chain);
    } catch (e) {
      setError((e as Error).message);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const setField = (field: keyof EntryDraft, value: string) =>
    setDraft((d) => ({ ...d, [field]: value }));

  const setMode = (kind: EntryKind) => {
    setChoiceNeeded(null);
    setDraft((d) => ({ ...d, kind }));
  };

  const hasWords =
    draft.kind === "guided"
      ? GUIDED_PROMPTS.some((p) => draft[p.field].trim() !== "")
      : draft.body.trim() !== "";

  async function submit(privacyChoice?: "keep" | "blur") {
    setSaving(true);
    setError(null);
    try {
      const result = await saveEntry({ ...draft, privacy_choice: privacyChoice });
      if (!result.saved) {
        setChoiceNeeded(result.found);
        return;
      }
      setChoiceNeeded(null);
      setDraft({ ...EMPTY_DRAFT, kind: draft.kind });
      setToast("Kept. Sealed into your journal.");
      setTimeout(() => setToast(null), 3500);
      await refresh();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="page">
      <header>
        <h1>நம்பிக்கை · Nambikkai</h1>
        <p className="tagline">Your journal, and yours alone. It never leaves this computer.</p>
      </header>

      <main>
        <section className="writer" aria-label="Write an entry">
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
                {GUIDED_PROMPTS.map((p) => (
                  <label key={p.field} className="prompt">
                    <span>{p.label}</span>
                    <textarea
                      rows={2}
                      value={draft[p.field]}
                      placeholder={p.hint}
                      onChange={(e) => setField(p.field, e.target.value)}
                    />
                  </label>
                ))}
              </>
            ) : (
              <>
                <p className="intro">Write anything, any shape. The mess is fine.</p>
                <textarea
                  className="freebox"
                  rows={10}
                  value={draft.body}
                  placeholder="It doesn't have to make sense to anyone. Not even you, not yet."
                  onChange={(e) => setField("body", e.target.value)}
                />
              </>
            )}
          </div>

          {choiceNeeded ? (
            <div className="privacy-card" role="alertdialog" aria-label="Before this is kept">
              <p>
                This entry looks like it has {choiceNeeded.join(" and ")} in it. Your journal
                doesn't need that to remember the day, and either way, nothing leaves this computer.
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

          {toast && <p className="toast">{toast}</p>}
          {error && <p className="error">{error}</p>}
        </section>

        <section className="journal" aria-label="Your entries">
          <h2>Your entries</h2>
          {entries.length === 0 ? (
            <p className="empty">Nothing here yet. The first word is the hard one.</p>
          ) : (
            entries.map((entry) => (
              <article key={entry.id} className="entry">
                <div className="entry-head">
                  <time>{friendlyDate(entry.at)}</time>
                  <span className="badge">{entry.kind === "guided" ? "Guided" : "Free"}</span>
                  {entry.blurred && <span className="badge soft">blurred before saving</span>}
                </div>
                {entry.kind === "guided" ? (
                  <dl>
                    {GUIDED_PROMPTS.filter((p) => entry[p.field]).map((p) => (
                      <div key={p.field}>
                        <dt>{p.label}</dt>
                        <dd>{entry[p.field]}</dd>
                      </div>
                    ))}
                  </dl>
                ) : (
                  <p className="body">{entry.body}</p>
                )}
              </article>
            ))
          )}
        </section>
      </main>

      <footer>
        {chain &&
          (chain.ok ? (
            <p>
              {chain.count === 0
                ? "A blank book, ready."
                : `${chain.count} ${chain.count === 1 ? "entry" : "entries"} · record unbroken`}
              {" · nothing is ever sent anywhere"}
            </p>
          ) : (
            <p className="error">
              The seal on your record looks broken. Your words are still here, but something
              changed the file outside the app.
            </p>
          ))}
      </footer>
    </div>
  );
}
