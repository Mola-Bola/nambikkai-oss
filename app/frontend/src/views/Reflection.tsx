import { useEffect, useState } from "react";
import {
  Entry,
  Persona,
  RelatedEntry,
  getRelated,
  getRelatedToDraft,
  saveEntry,
} from "../api";
import { EntryCard } from "./Journal";

// The reflection surface (ADR 003).
//
// Two rules decide everything in this file, and both are testable:
//
//   1. NOTHING HERE WRITES A SENTENCE ABOUT ANYONE'S INNER LIFE. What gets
//      rendered is EntryCard, the same component the journal uses, showing the
//      user's own words verbatim. There is no summary, no theme, no label and
//      no score on screen. If there is nothing to show, this renders nothing.
//   2. IT IS PULLED, NEVER PUSHED. A quiet line says something is there. It
//      opens when clicked and not before. Nothing pops up mid-sentence.
//
// The question layer below is off unless the user turned it on, asks rather
// than tells, and only ever says one of the sentences in QUESTIONS.

// A fixed, reviewed set. Not generated, not assembled from parts, not per
// entry: every sentence a user can see here was written by a person and read
// by a person. They ask about the pairing on screen, never about a feeling.
const QUESTIONS = [
  "Does this still sound right to you?",
  "Is this the same thing, or does it only look like it?",
  "Would you write it the same way now?",
  "Has anything changed since then?",
  "Is there anything you would add to it now?",
];

// Stable choice per entry, so the question does not shuffle while it is read.
function questionFor(key: string): string {
  let sum = 0;
  for (let i = 0; i < key.length; i += 1) sum = (sum * 31 + key.charCodeAt(i)) % 100000;
  return QUESTIONS[sum % QUESTIONS.length];
}

function countWord(n: number): string {
  return n === 1 ? "One earlier entry" : `${n} earlier entries`;
}

export default function Reflection({
  entryId,
  draft,
  people,
  questionsOn,
  onAnswered,
}: {
  // Exactly one of these. entryId reflects on something kept; draft reflects
  // on something still being written and is never stored by looking at it.
  entryId?: string;
  draft?: string;
  people: Persona[];
  questionsOn: boolean;
  onAnswered?: () => void;
}) {
  const [related, setRelated] = useState<RelatedEntry[]>([]);
  const [matching, setMatching] = useState("shared words only");
  const [open, setOpen] = useState(false);
  const [answer, setAnswer] = useState("");
  const [dismissed, setDismissed] = useState(false);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    let live = true;
    const text = draft ?? "";

    async function look() {
      try {
        const result = entryId ? await getRelated(entryId) : await getRelatedToDraft(text);
        if (!live) return;
        setRelated(result.related);
        setMatching(result.matching);
      } catch {
        // A lookup that fails is a lookup that found nothing. It is never an
        // error a writer has to read.
        if (live) setRelated([]);
      }
    }

    if (entryId) {
      look();
    } else if (text.trim().length > 40) {
      // Only after a pause, and only once there is something to match on.
      // Writing must never be interrupted by the app thinking out loud.
      const timer = setTimeout(look, 1200);
      return () => {
        live = false;
        clearTimeout(timer);
      };
    } else {
      setRelated([]);
    }

    return () => {
      live = false;
    };
  }, [entryId, draft]);

  // Silence is the default and the most common state. Render nothing at all.
  if (related.length === 0) return null;

  const question = questionFor(entryId ?? related[0].entry.id);

  async function keepAnswer() {
    if (!answer.trim()) return;
    setSaving(true);
    try {
      // Only the user's words are kept. The question that prompted them is not
      // stored anywhere: it was an offer, and an offer is not a record.
      await saveEntry({
        kind: "free",
        feeling: "",
        why: "",
        cause: "",
        helps: "",
        body: answer.trim(),
        persona_ids: [],
      });
      setAnswer("");
      setDismissed(true);
      onAnswered?.();
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="reflect">
      <button className="reflect-hint" onClick={() => setOpen((o) => !o)}>
        <i className="reflect-dot" />
        {countWord(related.length)} {related.length === 1 ? "sits" : "sit"} near this one
        <span className="reflect-more">{open ? "hide" : "read"}</span>
      </button>

      {open && (
        <div className="reflect-body">
          <p className="whisper">
            Your own words, exactly as you wrote them. Nothing here has been rewritten.
            {matching === "shared words only" &&
              " These were found by shared words only, so the matching is basic for now."}
          </p>

          <div className="reflect-cards">
            {related.map((r: RelatedEntry) => (
              <div className="reflect-card" key={r.entry.id}>
                <EntryCard entry={r.entry as Entry} people={people} />
              </div>
            ))}
          </div>

          {questionsOn && !dismissed && (
            <div className="reflect-ask">
              <b>{question}</b>
              <p className="whisper">
                Only your answer is kept, as an entry of your own. The question is not
                saved, and skipping it costs nothing.
              </p>
              <textarea
                rows={3}
                value={answer}
                placeholder="However it comes. Or leave it."
                onChange={(e) => setAnswer(e.target.value)}
              />
              <div className="choices">
                <button onClick={keepAnswer} disabled={!answer.trim() || saving}>
                  {saving ? "Keeping…" : "Keep this"}
                </button>
                <button className="ghost small" onClick={() => setDismissed(true)}>
                  Not now
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
