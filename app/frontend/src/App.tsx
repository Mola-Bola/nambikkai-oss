import { useCallback, useEffect, useState } from "react";
import {
  ChainState,
  Entry,
  LooseEnd,
  Persona,
  ReflectionSettings,
  Truth,
  YouResult,
  answerLooseEnd,
  getHealth,
  getReflectionSettings,
  getYou,
  listEntries,
  listLooseEnds,
  listPersonas,
  listTruths,
} from "./api";
import BringIn from "./views/BringIn";
import Journal from "./views/Journal";
import People from "./views/People";
import Settings from "./views/Settings";
import Today from "./views/Today";
import Truths from "./views/Truths";
import You from "./views/You";

type Screen = "today" | "journal" | "people" | "truths" | "bring" | "you" | "settings";

const NAV: { id: Screen; label: string }[] = [
  { id: "today", label: "Today" },
  { id: "journal", label: "Journal" },
  { id: "people", label: "People & things" },
  { id: "truths", label: "Truths" },
  { id: "bring", label: "Bring in" },
  { id: "you", label: "You" },
  { id: "settings", label: "Settings" },
];

export default function App() {
  const [screen, setScreen] = useState<Screen>("today");
  const [entries, setEntries] = useState<Entry[]>([]);
  const [people, setPeople] = useState<Persona[]>([]);
  const [truths, setTruths] = useState<Truth[]>([]);
  const [looseEnds, setLooseEnds] = useState<LooseEnd[]>([]);
  const [you, setYou] = useState<YouResult | null>(null);
  const [chain, setChain] = useState<ChainState | null>(null);
  const [demoLoaded, setDemoLoaded] = useState(false);
  const [reflection, setReflection] = useState<ReflectionSettings | null>(null);
  const [error, setError] = useState<string | null>(null);
  // Dismissed for this session only: "later" must never mean "never".
  const [hushed, setHushed] = useState<string[]>([]);

  const refresh = useCallback(async () => {
    try {
      const [e, p, t, l, y, h, r] = await Promise.all([
        listEntries(),
        listPersonas(),
        listTruths(),
        listLooseEnds(),
        getYou(),
        getHealth(),
        getReflectionSettings(),
      ]);
      setEntries(e.entries);
      setChain(e.chain);
      setPeople(p);
      setTruths(t);
      setLooseEnds(l);
      setYou(y);
      setDemoLoaded(h.demo_loaded ?? false);
      setReflection(r);
      setError(null);
    } catch (err) {
      setError((err as Error).message);
    }
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const pending = looseEnds.filter((l) => !hushed.includes(l.id));
  const ask = pending[0];

  return (
    <div className="app">
      <aside className="rail">
        <div className="brand">
          நம்பிக்கை
          <small>a journal that keeps receipts</small>
        </div>
        <nav>
          {NAV.map((n) => (
            <button
              key={n.id}
              className={screen === n.id ? "on" : ""}
              onClick={() => setScreen(n.id)}
            >
              {n.label}
              {n.id === "bring" && pending.length > 0 && <i className="dot" />}
            </button>
          ))}
        </nav>
        <div className="foot">Your words never leave this device.</div>
      </aside>

      <main className="main">
        {demoLoaded && (
          <div className="demo-banner">
            Demo data is loaded. Anything marked <span className="badge demo">demo</span> is
            made up, not yours. Remove it any time in Settings.
          </div>
        )}
        {error && <p className="error">{error}</p>}

        {screen === "today" && (
          <Today
            people={people}
            onSaved={refresh}
            questionsOn={reflection?.questions_on ?? false}
          />
        )}
        {screen === "journal" && (
          <Journal
            entries={entries}
            people={people}
            chain={chain}
            writtenDays={you?.written_days ?? []}
            truthDays={you?.truth_days ?? []}
            yearAgo={you?.year_ago ?? []}
            questionsOn={reflection?.questions_on ?? false}
            onChanged={refresh}
          />
        )}
        {screen === "people" && <People people={people} onChanged={refresh} />}
        {screen === "truths" && <Truths truths={truths} people={people} onChanged={refresh} />}
        {screen === "bring" && <BringIn onImported={refresh} />}
        {screen === "you" && <You you={you} />}
        {screen === "settings" && (
          <Settings demoLoaded={demoLoaded} reflection={reflection} onChanged={refresh} />
        )}
      </main>

      {/* A loose end is an offer, never a gate. "Later" is always a real answer. */}
      {ask && (
        <div className="pop" role="dialog" aria-label="A loose end">
          <b>A loose end, when you are ready</b>
          <p>
            You mention “{ask.name}” {ask.mentions} times in {ask.source || "your writing"}. Someone
            or something you'd like on your map?
          </p>
          <div className="choices">
            <button
              onClick={async () => {
                setLooseEnds(await answerLooseEnd(ask.id, "added"));
                refresh();
              }}
            >
              Add {ask.name}
            </button>
            <button className="ghost small" onClick={() => setHushed((h) => [...h, ask.id])}>
              Later
            </button>
            <button
              className="ghost small"
              onClick={async () => setLooseEnds(await answerLooseEnd(ask.id, "dismissed"))}
            >
              Not someone
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
