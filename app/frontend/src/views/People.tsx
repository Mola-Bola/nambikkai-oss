import { useState } from "react";
import { Persona, PersonaDraft, Truth, createPersona, getThread, updatePersona } from "../api";
import { EntryCard, friendlyDate } from "./Journal";
import type { Entry } from "../api";

const EMPTY: PersonaDraft = {
  name: "",
  alias: "",
  kind: "",
  thought_then: "",
  think_now: "",
  still_relevant: true,
};

function initials(name: string): string {
  return (name.trim()[0] ?? "?").toUpperCase();
}

function PersonaForm({
  initial,
  submitLabel,
  onDone,
  onCancel,
}: {
  initial: PersonaDraft;
  submitLabel: string;
  onDone: (p: PersonaDraft) => Promise<void>;
  onCancel: () => void;
}) {
  const [draft, setDraft] = useState<PersonaDraft>(initial);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const set = (k: keyof PersonaDraft, v: string | boolean) =>
    setDraft((d) => ({ ...d, [k]: v }));

  async function go() {
    setBusy(true);
    setError(null);
    try {
      await onDone(draft);
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="card">
      <label className="prompt">
        <span>What do you call them?</span>
        <input
          type="text"
          value={draft.name}
          placeholder="a real name or a nickname, whichever you'd use"
          onChange={(e) => set("name", e.target.value)}
        />
      </label>
      <label className="prompt">
        <span>Who or what are they to you?</span>
        <input
          type="text"
          value={draft.kind ?? ""}
          placeholder="mother · partner · the cat · the lake"
          onChange={(e) => set("kind", e.target.value)}
        />
      </label>
      <label className="prompt">
        <span>If this ever leaves your device, call them</span>
        <input
          type="text"
          value={draft.alias ?? ""}
          placeholder="a role, like 'my mother'. Leave blank and we'll use one."
          onChange={(e) => set("alias", e.target.value)}
        />
        <span className="whisper">
          Real names are fine here. They only become roles if you export something.
        </span>
      </label>
      <label className="prompt">
        <span>What you thought, then</span>
        <textarea
          rows={2}
          value={draft.thought_then ?? ""}
          placeholder="leave it blank if nothing has shifted"
          onChange={(e) => set("thought_then", e.target.value)}
        />
      </label>
      <label className="prompt">
        <span>What you think, now</span>
        <textarea
          rows={2}
          value={draft.think_now ?? ""}
          onChange={(e) => set("think_now", e.target.value)}
        />
      </label>
      <label className="checkline">
        <input
          type="checkbox"
          checked={draft.still_relevant ?? true}
          onChange={(e) => set("still_relevant", e.target.checked)}
        />
        <span>Still part of your life</span>
      </label>
      <div className="choices">
        <button onClick={go} disabled={busy || !draft.name.trim()}>
          {busy ? "Saving…" : submitLabel}
        </button>
        <button className="ghost" onClick={onCancel}>
          Cancel
        </button>
      </div>
      {error && <p className="error">{error}</p>}
    </div>
  );
}

function Thread({ personaId, people, onClose }: { personaId: string; people: Persona[]; onClose: () => void }) {
  const [entries, setEntries] = useState<Entry[] | null>(null);
  const [truths, setTruths] = useState<Truth[]>([]);
  const [name, setName] = useState("");

  if (entries === null) {
    getThread(personaId).then((t) => {
      setEntries(t.entries);
      setTruths(t.truths);
      setName(t.persona.name);
    });
    return <p className="empty">Gathering their thread…</p>;
  }

  return (
    <div className="card">
      <div className="spread">
        <h2 style={{ margin: 0 }}>{name}</h2>
        <button className="ghost small" onClick={onClose}>
          Back to everyone
        </button>
      </div>
      {truths.length > 0 && (
        <div className="thread-truths">
          {truths.map((t) => (
            <p key={t.id} className={t.current ? "" : "struck"}>
              {t.text}
              <span className="whisper">
                {t.current
                  ? ` · you believe this since ${friendlyDate(t.valid_from).split(" at ")[0]}`
                  : ` · you believed this until ${friendlyDate(t.valid_to ?? "").split(" at ")[0]}`}
              </span>
            </p>
          ))}
        </div>
      )}
      {entries.length === 0 ? (
        <p className="empty">Nothing mentions them yet. Their thread fills as you write.</p>
      ) : (
        entries.map((e) => <EntryCard key={e.id} entry={e} people={people} />)
      )}
    </div>
  );
}

export default function People({ people, onChanged }: { people: Persona[]; onChanged: () => void }) {
  const [adding, setAdding] = useState(false);
  const [editing, setEditing] = useState<Persona | null>(null);
  const [openThread, setOpenThread] = useState<string | null>(null);

  if (openThread) {
    return (
      <>
        <h1>People &amp; things</h1>
        <p className="sub">Everything they show up in, in your own words.</p>
        <Thread personaId={openThread} people={people} onClose={() => setOpenThread(null)} />
      </>
    );
  }

  return (
    <>
      <h1>People &amp; things</h1>
      <p className="sub">Everyone and everything that shapes your days. Named your way.</p>

      {editing ? (
        <PersonaForm
          initial={{
            name: editing.name,
            alias: editing.alias ?? "",
            kind: editing.kind ?? "",
            thought_then: editing.thought_then ?? "",
            think_now: editing.think_now ?? "",
            still_relevant: editing.still_relevant ?? true,
          }}
          submitLabel="Save changes"
          onCancel={() => setEditing(null)}
          onDone={async (d) => {
            await updatePersona(editing.id, d);
            setEditing(null);
            onChanged();
          }}
        />
      ) : adding ? (
        <PersonaForm
          initial={{ ...EMPTY }}
          submitLabel="Add them"
          onCancel={() => setAdding(false)}
          onDone={async (d) => {
            await createPersona(d);
            setAdding(false);
            onChanged();
          }}
        />
      ) : (
        <button className="keep" onClick={() => setAdding(true)}>
          Add someone or something
        </button>
      )}

      {people.length === 0 ? (
        <p className="empty">
          No one here yet. Anyone can go on this map: people, pets, places, even objects.
        </p>
      ) : (
        <div className="pgrid">
          {people.map((p) => (
            <div className="card persona" key={p.id}>
              <div className="mono">{initials(p.name)}</div>
              <h3>{p.name}</h3>
              <span className="kind">{p.kind}</span>
              {p.demo && <span className="badge demo">demo</span>}
              {p.last_line && <div className="last">“{p.last_line}”</div>}
              {(p.thought_then || p.think_now) && (
                <details>
                  <summary>How your view has moved</summary>
                  <div className="thennow">
                    <b>you thought, then</b>
                    {p.thought_then || "(nothing written)"}
                    <b>you think, now</b>
                    {p.think_now || "(nothing written)"}
                  </div>
                </details>
              )}
              <div className="rel">
                {p.mentions === 0
                  ? "not in your pages yet"
                  : `in your pages ${p.mentions} ${p.mentions === 1 ? "time" : "times"}`}
                {p.still_relevant === false && " · no longer close"}
              </div>
              <div className="choices">
                <button className="ghost small" onClick={() => setOpenThread(p.id)}>
                  Their thread
                </button>
                <button className="ghost small" onClick={() => setEditing(p)}>
                  Edit
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </>
  );
}
