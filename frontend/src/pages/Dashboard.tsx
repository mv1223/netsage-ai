import { useEffect, useState } from "react";
import { api, DashboardData } from "../api";

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .dashboard()
      .then(setData)
      .catch((err: Error) => setError(err.message));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!data) return <p>Loading dashboard…</p>;

  const maxType = Math.max(1, ...Object.values(data.by_issue_type));

  return (
    <section>
      <h1 className="page-title">Lab overview</h1>
      <p className="lede">
        Counts come from the 30 practice cases in the dataset. Agreement is calculated
        only from real Accepted / Edited / Rejected reviews stored in SQLite.
      </p>

      <div className="grid-stats">
        <article className="card">
          <h3>Total cases</h3>
          <p className="big">{data.total_cases}</p>
        </article>
        <article className="card">
          <h3>Critical</h3>
          <p className="big">{data.critical}</p>
        </article>
        <article className="card">
          <h3>High</h3>
          <p className="big">{data.high}</p>
        </article>
        <article className="card">
          <h3>Medium</h3>
          <p className="big">{data.medium}</p>
        </article>
      </div>
      <p className="lede">
        {Object.entries(data.by_issue_type)
          .map(([type, count]) => `${type}: ${count}`)
          .join(" · ")}
      </p>

      <div className="split">
        <article className="card">
          <h3>Cases by topic</h3>
          <div className="bars" style={{ marginTop: "0.7rem" }}>
            {Object.entries(data.by_issue_type).map(([name, count]) => (
              <div className="bar-row" key={name}>
                <span>{name}</span>
                <div className="bar-track">
                  <div className="bar-fill" style={{ width: `${(count / maxType) * 100}%` }} />
                </div>
                <strong>{count}</strong>
              </div>
            ))}
          </div>
        </article>
        <article className="card">
          <h3>AI vs human agreement</h3>
          <p className="big">{data.agreement_label}</p>
          <p className="lede" style={{ marginTop: "0.6rem" }}>
            Formula: Accepted reviews ÷ all reviewed cases × 100. Edited and Rejected
            count as disagreement with the raw suggestion.
          </p>
          <p>
            Accepted {data.accepted} · Edited {data.edited} · Rejected {data.rejected} ·
            Reviewed {data.reviewed}
          </p>
        </article>
      </div>
    </section>
  );
}
