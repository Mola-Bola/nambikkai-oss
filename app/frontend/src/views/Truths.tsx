import { useState } from "react";
import { Persona, Truth, createTruth } from "../api";
import { friendlyDate } from "./Journal";

function dayOnly(iso: string): string {
  const s = friendlyDate(iso);
  return s ? s.split(" at ")[0] : "";
}

// A truth is never edited. Revising appends a new one and the old keeps its
// dates, so "what I believed then" stays readable beside "what I know now".
function ReviseForm({
  onDone,
  onCancel,
}: {
  onDone: (text: string, share: string) => Promise<void>;
  onCancel: () => void;
}) {
  const [text, setText] = useState("");
  const [share, setShare] = useState("");
  const [busy, setBusy] = useState(false);

  return (
    <div className="revise">
      <label className="prompt">
        <span>What do you know now?</span>
        <textarea
          rows={3}
          value={text}
          placeholder="the old line isn't deleted, it keeps its dates"
          onChange={(e) => setText(e.target.value)}
        />
      </label>
      <label className="prompt">
        <span>Anything you'd say to them, if you ever did?</span>
        <textarea
          rows={2}
          value={share}
          placeholder="kept private, just for you. Optional."
          onChange={(e) => setShare(e.target.value)}
        />
      </label>
      <div className="choices">
        <button
          disabled={busy || !text.trim()}
          onClick={async () => {
            setBusy(true);
            await onDone(text, share);
            setBusy(false);
          }}
        >
          Keep what you know now
        </button>
        <button className="ghost" onClick={onCancel}>
          Cancel
        </button>
      </div>
      <p className="whisper">
        Asking never rewrites. A new line is added, and the old one keeps its dates.
      </p>
    </div>
  );
}

function NewTruth({ people, onDone }: { people: Persona[]; onDone: () => void }) {
  const [about, setAbout] = useState("self");
  const [text, setText] = useState("");
  const [share, setShare] = useState("");
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  return (
    <div className="card">
      <label className="prompt">
        <span>Who is this about?</span>
        <select value={about} onChange={(e) => setAbout(e.target.value)}>
          <option value="self">Yourself</option>
          {people.map((p) => (
            <option key={p.id} value={p.id}>
              {p.name}
            </option>
          ))}
        </select>
      </label>
      <label className="prompt">
        <span>What have you come to believe?</span>
        <textarea
          rows={3}
          value={text}
          placeholder="however rough. You can revise it later, and both versions stay."
          onChange={(e) => setText(e.target.value)}
        />
      </label>
      <label className="prompt">
        <span>Anything you'd say to them, if you ever did?</span>
        <textarea
          rows={2}
          value={share}
          placeholder="kept private, just for you. Optional."
          onChange={(e) => setShare(e.target.value)}
        />
      </label>
      <div className="choices">
        <button
          disabled={busy || !text.trim()}
          onClick={async () => {
            setBusy(true);
            setError(null);
            try {
              await createTruth({ about, text, share_draft: share, supersedes: null });
              setText("");
              setShare("");
              onDone();
            } catch (e) {
              setError((e as Error).message);
            } finally {
              setBusy(false);
            }
          }}
        >
          {busy ? "Keeping…" : "Keep this"}
        </button>
      </div>
      {error && <p className="error">{error}</p>}
    </div>
  );
}

export default function Truths({
  truths,
  people,
  onChanged,
}: {
  truths: Truth[];
  people: Persona[];
  onChanged: () => void;
}) {
  const [revising, setRevising] = useState<string | null>(null);
  const [adding, setAdding] = useState(false);

  // Group by who they're about, so a thread reads as one changing view.
  const groups = new Map<string, Truth[]>();
  for (const t of truths) {
    const key = t.about ?? "self";
    groups.set(key, [...(groups.get(key) ?? []), t]);
  }

  return (
    <>
      <h1>Truths</h1>
      <p className="sub">
        What you have come to believe. Kept with dates, so it can change when you do.
      </p>

      {adding ? (
        <NewTruth
          people={people}
          onDone={() => {
            setAdding(false);
            onChanged();
          }}
        />
      ) : (
        <button className="keep" onClick={() => setAdding(true)}>
          Record a truth
        </button>
      )}

      {truths.length === 0 && (
        <p className="empty">
          Nothing recorded yet. A truth is anything you've concluded about someone, or yourself.
        </p>
      )}

      {[...groups.entries()].map(([about, rows]) => {
        const sorted = [...rows].sort((a, b) => (a.valid_from ?? "").localeCompare(b.valid_from ?? ""));
        const current = sorted.filter((t) => t.current);
        return (
          <section className="card" key={about}>
            <div className="spread">
              <h3>{rows[0].about_name}</h3>
              {current.length > 0 && (
                <button className="ghost small" onClick={() => setRevising(current[0].id)}>
                  Still true?
                </button>
              )}
            </div>
            <div className="truth">
              {sorted.map((t) => (
                <div className={t.current ? "knot" : "knot past"} key={t.id}>
                  <div className="when">
                    {t.current
                      ? `what you know now · since ${dayOnly(t.valid_from)}`
                      : `believed from ${dayOnly(t.valid_from)} to ${dayOnly(t.valid_to ?? "")}`}
                  </div>
                  <p className={t.current ? "" : "struck"}>{t.text}</p>
                  {t.current && t.share_draft && (
                    <div className="share">
                      <b>Kept aside, in case you ever want to say it</b>
                      {t.share_draft}
                    </div>
                  )}
                  {t.demo && <span className="badge demo">demo</span>}
                </div>
              ))}
            </div>
            {revising && current.some((t) => t.id === revising) && (
              <ReviseForm
                onCancel={() => setRevising(null)}
                onDone={async (text, share) => {
                  await createTruth({
                    about,
                    text,
                    share_draft: share,
                    supersedes: revising,
                  });
                  setRevising(null);
                  onChanged();
                }}
              />
            )}
          </section>
        );
      })}
    </>
  );
}
