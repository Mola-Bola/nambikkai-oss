import { markGuideSeen } from "../api";

// The orientation shown before the first entry (VISION · Audience & voice).
//
// IT IS NOT A GATE, and the structure is what guarantees that rather than the
// copy: this renders ABOVE the writing card on the same screen, so the form is
// reachable the whole time it is on screen. No modal, no overlay, no step
// counter, nothing to complete. Skipping is a real answer and it is remembered,
// because an orientation that comes back after being waved off is a gate.

const POINTS = [
  {
    q: "How are you feeling?",
    a: "One word is plenty. The closest one you can find beats the perfect one you cannot.",
  },
  {
    q: "Why, do you think?",
    a: "A guess is fine here. You are not being graded, and you can be wrong about yourself.",
  },
  {
    q: "Who or what brought it on?",
    a: "A person, a pet, a place, a thing. Anything that was part of it counts.",
  },
  {
    q: "What helps, now or before?",
    a: "Something small that worked once is worth more here than advice you have never tried.",
  },
];

export default function Guide({ onDone }: { onDone: () => void }) {
  async function dismiss() {
    try {
      await markGuideSeen();
    } finally {
      // Even if remembering it fails, never trap the reader behind this.
      onDone();
    }
  }

  return (
    <section className="card guide">
      <strong>Before you start, three quick things</strong>

      <p className="guide-lead">
        This is a journal that keeps track of what you write, who turns up in it, and what
        you have decided about them. You can skip all of this and just write.
      </p>

      <ol className="guide-list">
        <li>
          <b>The four questions are a nudge, not a form.</b> Answer one, answer all of them,
          or ignore them and use Free write instead. Nothing is required.
        </li>
        <li>
          <b>Mess is the format.</b> Half a sentence at midnight is a real entry. There is no
          streak to break and no score, and coming back after a long gap is the good part.
        </li>
        <li>
          <b>Nothing you write leaves this device.</b> No account, no cloud copy, no training
          on your words. If you ever export, names are swapped for roles first.
        </li>
      </ol>

      <div className="guide-grid">
        {POINTS.map((p) => (
          <div key={p.q}>
            <b>{p.q}</b>
            <span>{p.a}</span>
          </div>
        ))}
      </div>

      <div className="choices">
        <button onClick={dismiss}>Start writing</button>
        <button className="ghost small" onClick={dismiss}>
          Skip this
        </button>
      </div>
    </section>
  );
}
