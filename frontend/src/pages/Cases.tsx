import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api, CaseListItem } from "../api";

const TYPES = ["", "VLAN", "Gateway", "DHCP", "DNS", "Routing", "ACL", "NAT", "Wireless"];
const SEVS = ["", "Critical", "High", "Medium"];
const OSI = ["", "Layer 1", "Layer 2", "Layer 3", "Layer 4", "Layer 7"];
const REV = ["", "NONE", "PENDING", "ACCEPTED", "EDITED", "REJECTED"];

export default function Cases() {
  const [q, setQ] = useState("");
  const [issue, setIssue] = useState("");
  const [severity, setSeverity] = useState("");
  const [osi, setOsi] = useState("");
  const [review, setReview] = useState("");
  const [items, setItems] = useState<CaseListItem[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .cases({ q, issue_type: issue, severity, osi_layer: osi, review_status: review })
      .then((res) => setItems(res.items))
      .catch((err: Error) => setError(err.message));
  }, [q, issue, severity, osi, review]);

  return (
    <section>
      <h1 className="page-title">Practice cases</h1>
      <p className="lede">Thirty Packet Tracer-style faults. Search by case ID or symptom text.</p>
      {error && <p className="error">{error}</p>}
      <div className="filters">
        <input placeholder="Search case ID or symptom" value={q} onChange={(e) => setQ(e.target.value)} />
        <select value={issue} onChange={(e) => setIssue(e.target.value)}>
          {TYPES.map((t) => (
            <option key={t} value={t}>
              {t || "All topics"}
            </option>
          ))}
        </select>
        <select value={severity} onChange={(e) => setSeverity(e.target.value)}>
          {SEVS.map((t) => (
            <option key={t} value={t}>
              {t || "All severities"}
            </option>
          ))}
        </select>
        <select value={osi} onChange={(e) => setOsi(e.target.value)}>
          {OSI.map((t) => (
            <option key={t} value={t}>
              {t || "All OSI layers"}
            </option>
          ))}
        </select>
        <select value={review} onChange={(e) => setReview(e.target.value)}>
          {REV.map((t) => (
            <option key={t} value={t}>
              {t || "All review states"}
            </option>
          ))}
        </select>
      </div>
      <div className="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Case</th>
              <th>Topic</th>
              <th>Symptom</th>
              <th>Layer</th>
              <th>Severity</th>
              <th>Review</th>
            </tr>
          </thead>
          <tbody>
            {items.length === 0 ? (
              <tr>
                <td colSpan={6}>
                  <p className="empty">No cases match those filters. Clear a filter or try another search word.</p>
                </td>
              </tr>
            ) : (
              items.map((c) => (
                <tr key={c.case_id}>
                  <td>
                    <Link to={`/cases/${c.case_id}`}>{c.case_id}</Link>
                  </td>
                  <td>{c.issue_type}</td>
                  <td>{c.symptom}</td>
                  <td>{c.osi_layer}</td>
                  <td>
                    <span className={`pill sev-${c.severity}`}>{c.severity}</span>
                  </td>
                  <td>{c.review_status}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
