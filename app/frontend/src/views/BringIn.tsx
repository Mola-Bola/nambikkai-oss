import { useRef, useState } from "react";
import { importText } from "../api";

export default function BringIn({ onImported }: { onImported: () => void }) {
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const fileInput = useRef<HTMLInputElement>(null);

  async function readFiles(files: FileList | null) {
    if (!files?.length) return;
    // Read in the browser: the file never goes anywhere but this page.
    const parts = await Promise.all(Array.from(files).map((f) => f.text()));
    setText((t) => [t, ...parts].filter(Boolean).join("\n\n"));
  }

  async function go() {
    setBusy(true);
    setError(null);
    setResult(null);
    try {
      const r = await importText(text);
      const undated = r.undated ? `, ${r.undated} without a date we could read` : "";
      const asks = r.questions?.length ?? 0;
      setResult(
        `Kept ${r.kept} ${r.kept === 1 ? "entry" : "entries"}${undated}.` +
          (asks ? ` ${asks} ${asks === 1 ? "question is" : "questions are"} waiting, whenever you want them.` : "")
      );
      setText("");
      onImported();
    } catch (e) {
      setError((e as Error).message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <>
      <h1>Bring in what you already wrote</h1>
      <p className="sub">
        Old journals, notes, exports. Nambikkai reads them and starts your map. Nothing is
        deleted, and nothing leaves this device.
      </p>

      <div
        className="drop"
        onClick={() => fileInput.current?.click()}
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          e.preventDefault();
          readFiles(e.dataTransfer.files);
        }}
      >
        Drop files here, or click to choose
        <br />
        <span className="whisper">plain text and markdown for now</span>
        <input
          ref={fileInput}
          type="file"
          multiple
          accept=".txt,.md,.markdown,text/plain"
          hidden
          onChange={(e) => readFiles(e.target.files)}
        />
      </div>

      <section className="card">
        <label className="prompt">
          <span>Or paste it straight in</span>
          <textarea
            rows={10}
            value={text}
            placeholder={"2024-03-02\nWrote nothing for weeks. Today the kitchen smelled like home again."}
            onChange={(e) => setText(e.target.value)}
          />
          <span className="whisper">
            Dates on their own line start a new entry. Anything undated is kept as today.
          </span>
        </label>
        <button className="keep" onClick={go} disabled={busy || !text.trim()}>
          {busy ? "Reading…" : "Bring it in"}
        </button>
        {result && <p className="toast">{result}</p>}
        {error && <p className="error">{error}</p>}
      </section>

      <p className="footnote">
        Nambikkai reads your words to sort them by date and notice names that come up often. It
        never decides how you felt.
      </p>
    </>
  );
}
