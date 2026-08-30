import { FormEvent, useEffect, useState } from "react";
import { useSearchParams } from "react-router-dom";
import { api, DiagnosisRecord } from "../api";

export default function Troubleshoot() {
  const [params] = useSearchParams();
  const preset = params.get("case") || "";
  const [caseId, setCaseId] = useState(preset);
  const [symptom, setSymptom] = useState("");
  const [topology, setTopology] = useState("");
  const [showOut, setShowOut] = useState("");
  const [diag, setDiag] = useState<DiagnosisRecord | null>(null);
  const [decision, setDecision] = useState<"Accepted" | "Edited" | "Rejected" | "">("");
  const [comment, setComment] = useState("");
  const [correction, setCorrection] = useState("");
  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    if (!preset) return;
    api
      .case(preset)
      .then((c) => {
        setCaseId(c.case_id);
        setSymptom(c.symptom);
        setTopology(c.topology_note);
        setShowOut(c.show_outputs);
        setDiag(c.latest_diagnosis);
      })
      .catch((err: Error) => setError(err.message));
  }, [preset]);

  async function analyze(e: FormEvent) {
    e.preventDefault();
    setError("");
    setNotice("");
    setBusy(true);
    try {
      const result = await api.analyze({
        case_id: caseId || undefined,
        symptom,
        topology_note: topology,
        show_outputs: showOut,
      });
      setDiag(result);
      setDecision("");
      setComment("");
      setCorrection("");
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setBusy(false);
    }
  }

  async function submitReview(e: FormEvent) {
    e.preventDefault();
    if (!diag) return;
    setError("");
    setNotice("");
    if (!decision) {
      setError("Choose Accepted, Edited, or Rejected.");
      return;
    }
    try {
      await api.review({
        diagnosis_id: diag.id,
        decision,
        reviewer_comment: comment,
        human_correction: correction,
      });
      setNotice("Review saved. The helper suggestion is no longer pending.");
      if (caseId) {
        const c = await api.case(caseId);
        setDiag(c.latest_diagnosis);
      } else {
        setDiag({ ...diag, review_status: decision.toUpperCase() });
      }
    } catch (err) {
      setError((err as Error).message);
    }
  }

  const r = diag?.result;
  const pending = diag?.review_status === "PENDING";

  return (
    <section>
      <h1 className="page-title">Troubleshoot</h1>
      <p className="lede">
        Paste what you see in Packet Tracer. The helper only reads this page. It does not
        log into Packet Tracer or push commands.
      </p>
      {error && <p className="error">{error}</p>}
      {notice && <p className="banner">{notice}</p>}

      <form className="form-grid" onSubmit={analyze}>
        <div className="row-2">
          <label>
            Case ID (optional)
            <input value={caseId} onChange={(e) => setCaseId(e.target.value)} placeholder="NS-VLAN-01" />
          </label>
          <label>
            What's wrong?
            <input value={symptom} onChange={(e) => setSymptom(e.target.value)} required />
          </label>
        </div>
        <label>
          Topology note
          <textarea value={topology} onChange={(e) => setTopology(e.target.value)} />
        </label>
        <label>
          Network evidence (show output)
          <textarea value={showOut} onChange={(e) => setShowOut(e.target.value)} required />
        </label>
        <div>
          <button className="btn btn-primary" disabled={busy} type="submit">
            {busy ? "Working…" : "Analyze Problem"}
          </button>
        </div>
      </form>

      {r && diag && (
        <>
          <div className="diag-box">
            <h2>NetSage AI diagnosis</h2>
            <p className="banner">
              Status: {diag.review_status}. Engine: {diag.engine}. This is not an approved fix.
            </p>
            <div className="kv">
              <strong>Likely cause</strong>
              {r.root_cause}
            </div>
            <div className="kv">
              <strong>Confidence</strong>
              {r.confidence.toFixed(2)} ({confidenceWords(r.confidence)})
            </div>
            <div className="kv">
              <strong>OSI layer</strong>
              {r.osi_layer}
            </div>
            <div className="kv">
              <strong>Why we think this</strong>
            </div>
            <ul className="plain">
              {r.evidence.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
            <div className="kv">
              <strong>What should I check next?</strong>
            </div>
            <ul className="plain">
              {r.next_command.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
            <div className="kv">
              <strong>Suggested fix</strong>
            </div>
            <ul className="plain">
              {r.fix_steps.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
            <div className="kv">
              <strong>Verify after fixing</strong>
            </div>
            <ul className="plain">
              {r.verification.map((line) => (
                <li key={line}>{line}</li>
              ))}
            </ul>
          </div>

          <form className="review-box" onSubmit={submitReview}>
            <h2>Human review required</h2>
            {!pending && <p className="banner">This diagnosis already has a review ({diag.review_status}).</p>}
            <div className="btn-row">
              <button
                type="button"
                className={`btn btn-accept${decision === "Accepted" ? " is-selected" : ""}`}
                onClick={() => setDecision("Accepted")}
                disabled={!pending}
              >
                Accept
              </button>
              <button
                type="button"
                className={`btn btn-edit${decision === "Edited" ? " is-selected" : ""}`}
                onClick={() => setDecision("Edited")}
                disabled={!pending}
              >
                Edit
              </button>
              <button
                type="button"
                className={`btn btn-reject${decision === "Rejected" ? " is-selected" : ""}`}
                onClick={() => setDecision("Rejected")}
                disabled={!pending}
              >
                Reject
              </button>
            </div>
            <p>Selected: {decision || "none"}</p>
            {decision === "Edited" && (
              <label>
                Corrected diagnosis
                <textarea value={correction} onChange={(e) => setCorrection(e.target.value)} />
              </label>
            )}
            <label>
              Review comment
              <textarea value={comment} onChange={(e) => setComment(e.target.value)} />
            </label>
            <button className="btn btn-primary" type="submit" disabled={!pending}>
              Submit review
            </button>
          </form>
        </>
      )}
    </section>
  );
}

function confidenceWords(value: number): string {
  if (value >= 0.9) return "strong evidence";
  if (value >= 0.7) return "good evidence";
  if (value >= 0.5) return "moderate uncertainty";
  return "insufficient evidence";
}
