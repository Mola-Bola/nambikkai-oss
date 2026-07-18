import { useState } from "react";
import { ReflectionSettings, exportBundle, loadDemo, setQuestionsOn, wipeDemo } from "../api";

const PROMISES = [
  "Your words stay on this device. There is no cloud copy to breach.",
  "Nothing you write is ever used to train anything.",
  "Export everything, any time, in plain files. No paywall on your own life.",
  "Yesterday's entry cannot be silently rewritten. Changes are kept as changes.",
  "No streaks that reset to zero. Coming back is the win here.",
  "Nambikkai never tells you what you feel. It asks.",
];

export default function Settings({
  demoLoaded,
  reflection,
  onChanged,
}: {
  demoLoaded: boolean;
  reflection: ReflectionSettings | null;
  onChanged: () => void;
}) {
  const [busy, setBusy] = useState<string | null>(null);
  const [note, setNote] = useState<string | null>(null);

  async function withBusy(what: string, fn: () => Promise<string>) {
    setBusy(what);
    setNote(null);
    try {
      setNote(await fn());
      onChanged();
    } catch (e) {
      setNote((e as Error).message);
    } finally {
      setBusy(null);
    }
  }

  return (
    <>
      <h1>Settings</h1>
      <p className="sub">Short list, strong promises.</p>

      <section className="card">
        <strong>Our promises</strong>
        <ul className="promise">
          {PROMISES.map((p) => (
            <li key={p}>{p}</li>
          ))}
        </ul>
      </section>

      <section className="card">
        <strong>Looking back</strong>
        <p className="whisper">
          When something you write sits close to something you wrote before, a quiet line
          offers it. You click if you want it. What you see is your own writing, word for
          word, and nothing else.
        </p>
        <label className="toggle">
          <input
            type="checkbox"
            checked={reflection?.questions_on ?? false}
            disabled={busy !== null}
            onChange={(e) => {
              const on = e.target.checked;
              withBusy("questions", async () => {
                await setQuestionsOn(on);
                return on
                  ? "Gentle questions are on. They only ever ask, and you can turn them off here."
                  : "Gentle questions are off.";
              });
            }}
          />
          <span>
            <b>Let it ask me a gentle question</b>
            <small>
              Off unless you turn it on. When it is on, you may see a short question next to
              writing it brought back, like "does this still sound right to you?". It asks,
              it never concludes, and only your answer is kept.
            </small>
          </span>
        </label>
        {reflection && reflection.matching === "shared words only" && (
          <p className="whisper">
            Matching is basic right now: it compares words, not meaning. Running{" "}
            <code>make model</code> once adds the small offline model that does the rest. It
            stays on this device like everything else.
          </p>
        )}
      </section>

      <section className="card">
        <strong>Names</strong>
        <p className="whisper">
          Use real names or nicknames here on your device. If anything ever leaves, like an export
          you choose to share, names become roles first and card or ID numbers are masked.
        </p>
        <button
          className="ghost"
          disabled={busy !== null}
          onClick={() =>
            withBusy("export", async () => {
              const bundle = await exportBundle();
              const blob = new Blob([JSON.stringify(bundle, null, 2)], {
                type: "application/json",
              });
              const url = URL.createObjectURL(blob);
              const a = document.createElement("a");
              a.href = url;
              a.download = "nambikkai-export.json";
              a.click();
              URL.revokeObjectURL(url);
              return "Exported with names swapped for roles. Check the file before sharing it.";
            })
          }
        >
          {busy === "export" ? "Preparing…" : "Export everything"}
        </button>
      </section>

      <section className="card">
        <strong>Try it with made-up data</strong>
        <p className="whisper">
          A small invented life: four people and a cat, a handful of entries, and one truth that
          changed its mind. Every piece is labelled demo, and nothing here is anyone's real journal.
        </p>
        <div className="choices">
          {!demoLoaded && (
            <button
              disabled={busy !== null}
              onClick={() => withBusy("load", async () => {
                await loadDemo();
                return "Demo data loaded. Everything from it is labelled demo.";
              })}
            >
              {busy === "load" ? "Loading…" : "Load demo data"}
            </button>
          )}
          {demoLoaded && (
            <button
              className="ghost"
              disabled={busy !== null}
              onClick={() => withBusy("wipe", async () => {
                const r = await wipeDemo();
                return `Demo data removed (${r.removed} records). Your own writing is untouched.`;
              })}
            >
              {busy === "wipe" ? "Removing…" : "Remove demo data"}
            </button>
          )}
        </div>
      </section>

      {note && <p className="toast">{note}</p>}
    </>
  );
}
