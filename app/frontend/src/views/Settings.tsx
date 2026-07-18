import { useState } from "react";
import { exportBundle, loadDemo, wipeDemo } from "../api";

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
  onChanged,
}: {
  demoLoaded: boolean;
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
