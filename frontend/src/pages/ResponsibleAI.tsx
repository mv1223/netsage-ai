import { useEffect, useState } from "react";
import { api, RaiRecord } from "../api";

export default function ResponsibleAI() {
  const [items, setItems] = useState<RaiRecord[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    api
      .rai()
      .then((res) => setItems(res.items))
      .catch((err: Error) => setError(err.message));
  }, []);

  return (
    <section>
      <h1 className="page-title">Responsible AI log</h1>
      <p className="lede">
        Rows marked TEMPLATE are placeholders. Replace them with notes from your own Packet
        Tracer session. Edited and Rejected reviews also append real rows here.
      </p>
      {error && <p className="error">{error}</p>}
      <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Case</th>
            <th>Initial helper note</th>
            <th>Human correction</th>
            <th>Why it was wrong</th>
            <th>Evidence</th>
            <th>Decision</th>
            <th>Approved text</th>
          </tr>
        </thead>
        <tbody>
          {items.map((r) => (
            <tr key={r.id}>
              <td>
                {r.case_id}
                {r.is_template && (
                  <>
                    <br />
                    <span className="template-tag">TEMPLATE</span>
                  </>
                )}
              </td>
              <td>{r.initial_ai_diagnosis}</td>
              <td>{r.human_correction}</td>
              <td>{r.why_incorrect}</td>
              <td>{r.evidence_used}</td>
              <td>{r.final_decision}</td>
              <td>{r.final_approved_diagnosis}</td>
            </tr>
          ))}
        </tbody>
      </table>
      </div>
    </section>
  );
}
