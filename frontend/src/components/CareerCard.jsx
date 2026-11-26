import { MatchBar } from './ui'

export default function CareerCard({ career, rank }) {
  const salary = career.salary_range_lpa
    ? `₹${career.salary_range_lpa[0]}–${career.salary_range_lpa[1]} LPA`
    : career.salary_min_lpa
      ? `₹${career.salary_min_lpa}–${career.salary_max_lpa} LPA`
      : null
  return (
    <div className="card career-card">
      {rank ? <span className="rank-badge">#{rank} Match</span> : null}
      <h3 style={{ paddingRight: rank ? 70 : 0 }}>{career.career}</h3>
      <p className="muted" style={{ marginTop: 0 }}>{career.tagline}</p>
      {career.match_pct !== undefined && (
        <>
          <div className="match-ring">{career.match_pct}%</div>
          <MatchBar pct={career.match_pct} />
        </>
      )}
      <div className="chip-row">
        {salary && <span className="pill good">{salary} fresher</span>}
        {career.demand && <span className="pill">Demand: {career.demand}</span>}
        {career.growth && <span className="pill warn">{career.growth}</span>}
      </div>
      {(career.required_skills || career.required) && (
        <div className="chip-row">
          {(career.required_skills || career.required).map((s) => (
            <span key={s} className="pill">{s}</span>
          ))}
        </div>
      )}
    </div>
  )
}
