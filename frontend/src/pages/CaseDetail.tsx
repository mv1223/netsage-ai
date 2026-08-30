import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api, CaseDetail as CaseDetailType } from "../api";

export default function CaseDetail() {
  const { caseId } = useParams();
  const navigate = useNavigate();
  const [item, setItem] = useState<CaseDetailType | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!caseId) return;
    api
      .case(caseId)
      .then(setItem)
      .catch((err: Error) => setError(err.message));
  }, [caseId]);

  async function reset() {
    if (!caseId) return;
    if (!window.confirm("Clear diagnoses and reviews for this case on this computer?")) return;
    try {
      await api.resetCase(caseId);
      const fresh = await api.case(caseId);
      setItem(fresh);
    } catch (err) {
      setError((err as Error).message);
    }
  }

  if (error) return <p className="error">{error}</p>;
  if (!item) return <p>Loading case…</p>;

  return (
    <section>
      <h1 className="page-title">{item.case_id}</h1>
      <p className="lede">
        {item.issue_type} · {item.concept} · {item.osi_layer}
      </p>
      <div className="btn-row" style={{ marginBottom: "1rem" }}>
        <button className="btn btn-primary" onClick={() => navigate(`/troubleshoot?case=${item.case_id}`)}>
          Analyze
        </button>
        <Link className="btn btn-ghost" to={`/troubleshoot?case=${item.case_id}`}>
          Review
        </Link>
        <button className="btn btn-ghost" onClick={reset}>
          Reset
        </button>
      </div>
      <div className="split">
        <article className="card">
          <div className="kv">
            <strong>What's wrong?</strong>
            {item.symptom}
          </div>
          <div className="kv">
            <strong>Topology</strong>
            {item.topology_note}
          </div>
          <div className="kv">
            <strong>Expected fault (teacher key)</strong>
            {item.expected_fault}
          </div>
          <div className="kv">
            <strong>Severity</strong>
            <span className={`pill sev-${item.severity}`}>{item.severity}</span>
          </div>
        </article>
        <article className="card">
          <div className="kv">
            <strong>Network evidence</strong>
          </div>
          <pre className="mono">{item.show_outputs}</pre>
        </article>
      </div>
      {item.latest_diagnosis && (
        <p className="banner">
          Latest helper status: {item.latest_diagnosis.review_status}. This is not an approved fix
          until a reviewer submits Accepted or Edited.
        </p>
      )}
    </section>
  );
}
