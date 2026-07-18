import { ChainState, Entry, Persona } from "../api";

const PROMPT_LABELS: Record<string, string> = {
  feeling: "How are you feeling?",
  why: "Why, do you think?",
  cause: "Who or what brought it on?",
  helps: "What helps, now or before?",
};

export function friendlyDate(utcIso: string): string {
  if (!utcIso) return "";
  return new Date(utcIso).toLocaleString(undefined, {
    day: "numeric",
    month: "long",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}

export function EntryCard({ entry, people }: { entry: Entry; people: Persona[] }) {
  const tags = people.filter((p) => (entry.persona_ids ?? []).includes(p.id));
  const guided = ["feeling", "why", "cause", "helps"] as const;
  return (
    <article className="entry">
      <div className="entry-head">
        <time>{friendlyDate(entry.at)}</time>
        <span className="badge">{entry.kind === "guided" ? "Guided" : "Free"}</span>
        {entry.blurred && <span className="badge soft">blurred before saving</span>}
        {entry.demo && <span className="badge demo">demo</span>}
      </div>
      {entry.kind === "guided" ? (
        <dl>
          {guided
            .filter((f) => entry[f])
            .map((f) => (
              <div key={f}>
                <dt>{PROMPT_LABELS[f]}</dt>
                <dd>{entry[f]}</dd>
              </div>
            ))}
        </dl>
      ) : (
        <p className="body">{entry.body}</p>
      )}
      {tags.length > 0 && <div className="tags">{tags.map((t) => t.name).join(" · ")}</div>}
    </article>
  );
}

// A month of squares. Colour means only "you wrote" or "a truth changed" —
// never a guess at how the day went. Quiet days are quiet, not missing.
function Month({ written, truths }: { written: string[]; truths: string[] }) {
  const now = new Date();
  const year = now.getFullYear();
  const month = now.getMonth();
  const days = new Date(year, month + 1, 0).getDate();
  const written_ = new Set(written);
  const truths_ = new Set(truths);

  return (
    <section className="card">
      <div className="spread">
        <strong>
          {now.toLocaleString(undefined, { month: "long" })} {year}
        </strong>
        <span className="whisper">each square is a day</span>
      </div>
      <div className="pixels">
        {Array.from({ length: days }, (_, i) => {
          const iso = `${year}-${String(month + 1).padStart(2, "0")}-${String(i + 1).padStart(2, "0")}`;
          const cls = truths_.has(iso) ? "px gold" : written_.has(iso) ? "px on" : "px";
          return <div key={iso} className={cls} title={iso} />;
        })}
      </div>
      <span className="whisper">
        filled: a day you wrote · gold: a day a truth changed · empty days are just quiet
      </span>
    </section>
  );
}

export default function Journal({
  entries,
  people,
  chain,
  writtenDays,
  truthDays,
  yearAgo,
}: {
  entries: Entry[];
  people: Persona[];
  chain: ChainState | null;
  writtenDays: string[];
  truthDays: string[];
  yearAgo: Entry[];
}) {
  return (
    <>
      <h1>Journal</h1>
      <p className="sub">Your days, kept. Quiet days are just quiet, not missing.</p>

      <Month written={writtenDays} truths={truthDays} />

      {yearAgo.length > 0 && (
        <section className="card">
          <div className="whisper" style={{ marginBottom: "0.75rem" }}>
            One year ago this week
          </div>
          {yearAgo.slice(0, 2).map((e) => (
            <EntryCard key={e.id} entry={e} people={people} />
          ))}
        </section>
      )}

      <h2>Your entries</h2>
      {entries.length === 0 ? (
        <p className="empty">Nothing here yet. The first word is the hard one.</p>
      ) : (
        entries.map((e) => (
          <div className="card" key={e.id}>
            <EntryCard entry={e} people={people} />
          </div>
        ))
      )}

      {chain &&
        (chain.ok ? (
          <p className="footnote">
            {chain.count === 0
              ? "A blank book, ready."
              : `${chain.count} ${chain.count === 1 ? "entry" : "entries"} · record unbroken`}
            {" · nothing is ever sent anywhere"}
          </p>
        ) : (
          <p className="error">
            The seal on your record looks broken. Your words are still here, but something changed
            the file outside the app.
          </p>
        ))}
    </>
  );
}
