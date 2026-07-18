import { YouResult } from "../api";
import { friendlyDate } from "./Journal";

const KIND_WORDS: Record<string, string> = {
  entry: "you wrote",
  persona: "joined your map",
  truth: "a truth recorded",
  "truth-revised": "a truth changed",
};

export default function You({ you }: { you: YouResult | null }) {
  if (!you) return <p className="empty">Gathering the bigger picture…</p>;
  const o = you.overview;

  return (
    <>
      <h1>You</h1>
      <p className="sub">The bigger picture, from your own words. Nambikkai offers, you decide.</p>

      <section className="card">
        <div className="stat">
          <div>
            <b>{o.entries_kept}</b>
            <span>entries kept</span>
          </div>
          <div>
            <b>{o.days_written}</b>
            <span>days written on</span>
          </div>
          <div>
            <b>{o.people_mapped}</b>
            <span>people &amp; things mapped</span>
          </div>
          <div>
            <b>{o.truths_revisited}</b>
            <span>truths revisited</span>
          </div>
          <div>
            <b>{o.returns_after_quiet}</b>
            <span>returns after a quiet spell</span>
          </div>
        </div>
        <p className="whisper">
          Coming back counts here. There is no streak to break, and a gap is not a failure.
        </p>
      </section>

      <section className="card">
        <div className="spread">
          <strong>The thread of your year</strong>
        </div>
        <p className="whisper" style={{ marginBottom: "0.9rem" }}>
          What happened, in the order it happened. Your words only, no reading between the lines.
        </p>
        {you.timeline.length === 0 ? (
          <p className="empty">Nothing on the thread yet.</p>
        ) : (
          <ol className="thread">
            {you.timeline.slice(0, 60).map((row) => (
              <li key={`${row.kind}-${row.id}`} className={`thread-row ${row.kind}`}>
                <span className="when">{friendlyDate(row.at).split(" at ")[0]}</span>
                <span className="what">{KIND_WORDS[row.kind] ?? row.kind}</span>
                <span className="line">
                  {row.headline}
                  {row.feeling && <em> · {row.feeling}</em>}
                </span>
                {row.demo && <span className="badge demo">demo</span>}
              </li>
            ))}
          </ol>
        )}
      </section>

      <section className="card">
        <strong>Alongside your words</strong>
        <p className="whisper">
          Apps you already use could add their piece one day: runs, walks, sleep, screen time. None
          of this is built yet, and all of it would be off until you turned it on.
        </p>
      </section>
    </>
  );
}
