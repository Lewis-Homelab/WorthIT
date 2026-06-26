"use client";

import type { DayPlanCard as DayPlanCardType } from "@/lib/types";

interface PlanCardProps {
  plan: DayPlanCardType;
  className?: string;
}

/** Single swipe card — a complete half-day itinerary with ExperienceRank score. */
export function PlanCard({ plan, className = "" }: PlanCardProps) {
  return (
    <article className={`plan-card ${className}`.trim()} aria-label={plan.title}>
      <header className="plan-card__header">
        <span className="plan-card__emoji" aria-hidden>
          {plan.emoji}
        </span>
        <div>
          <h2 className="plan-card__title">{plan.title}</h2>
          <p className="plan-card__weather">{plan.weather_summary}</p>
        </div>
        <div className="plan-card__score" title="ExperienceRank score">
          <span className="plan-card__score-value">{Math.round(plan.score)}</span>
          <span className="plan-card__score-label">/ 100</span>
        </div>
      </header>

      <ul className="plan-card__stats">
        <li>
          <span className="plan-card__stat-label">Time</span>
          <span className="plan-card__stat-value">{plan.total_hours}h</span>
        </li>
        <li>
          <span className="plan-card__stat-label">Cost</span>
          <span className="plan-card__stat-value">
            {plan.cost_gbp != null ? `£${plan.cost_gbp.toFixed(0)}` : "—"}
          </span>
        </li>
        <li>
          <span className="plan-card__stat-label">Walking</span>
          <span className="plan-card__stat-value">
            {plan.walk_minutes != null ? `${Math.round(plan.walk_minutes)} min` : "—"}
          </span>
        </li>
      </ul>

      <section className="plan-card__stops">
        <h3 className="plan-card__stops-heading">Your day</h3>
        <ol className="plan-card__stop-list">
          {plan.stops.map((stop, index) => (
            <li key={`${stop.name}-${index}`} className="plan-card__stop">
              <span className="plan-card__stop-time">
                {index === 0 ? "Start" : `+${stop.dwell_minutes}m`}
              </span>
              <div className="plan-card__stop-body">
                <strong>{stop.name}</strong>
                <span className="plan-card__stop-meta">
                  {stop.category}
                  {stop.hygiene_rating != null && (
                    <> · FHRS {stop.hygiene_rating}/5</>
                  )}
                  <> · £{stop.estimated_cost_gbp.toFixed(0)}</>
                </span>
              </div>
              <span className="plan-card__stop-score" title="Stop score">
                {Math.round(stop.experience_score)}
              </span>
            </li>
          ))}
        </ol>
      </section>
    </article>
  );
}
