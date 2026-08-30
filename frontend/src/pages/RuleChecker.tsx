import { useState } from "react";
import { api } from "../api";

export default function RuleChecker() {
  const [report, setReport] = useState("");
  const [error, setError] = useState("");
  const [custom, setCustom] = useState("");

  async function run() {
    setError("");
    try {
      let state: object | undefined;
      if (custom.trim()) {
        state = JSON.parse(custom);
      }
      const res = await api.ruleCheck(state);
      setReport(res.report);
    } catch (err) {
      if (err instanceof SyntaxError) {
        setError("That snapshot is not valid JSON. Paste the sample file, or leave the box empty.");
        return;
      }
      setError((err as Error).message);
    }
  }

  return (
    <section>
      <h1 className="page-title">Rule checker</h1>
      <p className="lede">
        These checks are written in Python. They do not call a language model. The sample
        snapshot in data/sample_network_state.json is built so every required check fires.
      </p>
      {error && <p className="error">{error}</p>}
      <label>
        Optional JSON snapshot (leave empty to use the bundled sample)
        <textarea
          value={custom}
          onChange={(e) => setCustom(e.target.value)}
          placeholder='Leave empty, or paste a snapshot like data/sample_network_state.json'
        />
      </label>
      <div style={{ marginTop: "0.75rem" }}>
        <button className="btn btn-primary" onClick={run}>
          Run checker
        </button>
      </div>
      {report && <pre className="mono" style={{ marginTop: "1rem" }}>{report}</pre>}
    </section>
  );
}
