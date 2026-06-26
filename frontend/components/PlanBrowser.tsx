"use client";

import { useCallback, useEffect, useState } from "react";

import { fetchDayPlans } from "@/lib/api";
import type { DayPlanCard, DayPlanPreferences, DayPlanResponse } from "@/lib/types";

import { PlanCard } from "./PlanCard";
import { PreferencesForm } from "./PreferencesForm";

const DEFAULT_PREFS: DayPlanPreferences = {
  budget_gbp: 50,
  max_hours: 6,
  interests: ["coffee", "museum", "pub", "walk"],
  limit: 8,
};

const SAVED_KEY = "worthit-saved-plans";

type SwipeDirection = "left" | "right";

/** Browse-first day-plan experience — swipe cards like PROJECT_CONTEXT describes. */
export function PlanBrowser() {
  const [prefs, setPrefs] = useState<DayPlanPreferences>(DEFAULT_PREFS);
  const [response, setResponse] = useState<DayPlanResponse | null>(null);
  const [index, setIndex] = useState(0);
  const [saved, setSaved] = useState<DayPlanCard[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [swipe, setSwipe] = useState<SwipeDirection | null>(null);
  const [prefsOpen, setPrefsOpen] = useState(true);

  // Restore saved plans from the browser session (POC — no backend yet).
  useEffect(() => {
    try {
      const raw = sessionStorage.getItem(SAVED_KEY);
      if (raw) setSaved(JSON.parse(raw) as DayPlanCard[]);
    } catch {
      /* ignore corrupt session data */
    }
  }, []);

  const persistSaved = useCallback((plans: DayPlanCard[]) => {
    setSaved(plans);
    sessionStorage.setItem(SAVED_KEY, JSON.stringify(plans));
  }, []);

  async function loadPlans() {
    setLoading(true);
    setError(null);
    setSwipe(null);
    setIndex(0);
    setPrefsOpen(false);

    try {
      const data = await fetchDayPlans(prefs);
      setResponse(data);
      if (data.plans.length === 0) {
        setError("No plans matched your budget and time. Try loosening constraints.");
      }
    } catch (err) {
      setResponse(null);
      setError(err instanceof Error ? err.message : "Failed to load plans");
    } finally {
      setLoading(false);
    }
  }

  const plans = response?.plans ?? [];
  const current = plans[index];

  const advance = useCallback(
    (direction: SwipeDirection) => {
      if (!plans[index]) return;
      const plan = plans[index];

      setSwipe(direction);

      if (direction === "right") {
        const already = saved.some((p) => p.template_id === plan.template_id);
        if (!already) {
          persistSaved([...saved, plan]);
        }
      }

      window.setTimeout(() => {
        setSwipe(null);
        setIndex((i) => i + 1);
      }, 280);
    },
    [index, persistSaved, plans, saved],
  );

  // Keyboard: ← skip, → save & next
  useEffect(() => {
    function onKey(e: KeyboardEvent) {
      if (!plans[index] || loading || swipe) return;
      if (e.key === "ArrowLeft") advance("left");
      if (e.key === "ArrowRight") advance("right");
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [advance, index, loading, plans, swipe]);

  return (
    <div className="browser">
      <header className="browser__header">
        <div>
          <span className="badge">Camden POC</span>
          <h1>WorthIT</h1>
          <p className="browser__tagline">
            What&apos;s the most worthwhile thing you could do today?
          </p>
        </div>
        <button
          type="button"
          className="btn btn--ghost"
          onClick={() => setPrefsOpen((o) => !o)}
        >
          {prefsOpen ? "Hide filters" : "Edit filters"}
        </button>
      </header>

      {prefsOpen && (
        <PreferencesForm prefs={prefs} onChange={setPrefs} disabled={loading} />
      )}

      <div className="browser__actions">
        <button
          type="button"
          className="btn btn--primary"
          disabled={loading}
          onClick={() => void loadPlans()}
        >
          {loading ? "Finding experiences…" : "Show me ideas"}
        </button>
        {response && (
          <span className="browser__area">
            {response.area}
            {response.weather.temperature_c != null && (
              <> · {Number(response.weather.temperature_c).toFixed(0)}°C</>
            )}
          </span>
        )}
      </div>

      {loading && (
        <div className="browser__loading" role="status">
          <div className="spinner" aria-hidden />
          <p>
            Ranking day plans…
            <br />
            <small>First load builds the walking graph — can take 1–2 minutes.</small>
          </p>
        </div>
      )}

      {error && (
        <div className="browser__error" role="alert">
          {error}
        </div>
      )}

      {!loading && current && (
        <div className="browser__deck">
          <p className="browser__counter">
            {index + 1} of {plans.length}
          </p>
          <div className="browser__card-wrap">
            <PlanCard
              plan={current}
              className={swipe ? `plan-card--swipe-${swipe}` : ""}
            />
          </div>
          <div className="browser__swipe-actions">
            <button
              type="button"
              className="swipe-btn swipe-btn--skip"
              aria-label="Skip this plan"
              onClick={() => advance("left")}
            >
              ✕ Skip
            </button>
            <button
              type="button"
              className="swipe-btn swipe-btn--save"
              aria-label="Save this plan"
              onClick={() => advance("right")}
            >
              ♥ Save
            </button>
          </div>
          <p className="browser__hint">← skip · save →</p>
        </div>
      )}

      {!loading && response && !current && plans.length > 0 && (
        <div className="browser__done">
          <h2>That&apos;s everything for now</h2>
          <p>
            You browsed {plans.length} experience{plans.length === 1 ? "" : "s"}.
            {saved.length > 0 && ` You saved ${saved.length}.`}
          </p>
          <button type="button" className="btn btn--primary" onClick={() => void loadPlans()}>
            Refresh ideas
          </button>
        </div>
      )}

      {saved.length > 0 && (
        <section className="saved" aria-labelledby="saved-heading">
          <h2 id="saved-heading">Saved ({saved.length})</h2>
          <ul className="saved__list">
            {saved.map((plan) => (
              <li key={plan.template_id} className="saved__item">
                <span aria-hidden>{plan.emoji}</span>
                <div>
                  <strong>{plan.title}</strong>
                  <span>
                    {plan.total_hours}h · £{plan.cost_gbp?.toFixed(0) ?? "?"} · score{" "}
                    {Math.round(plan.score)}
                  </span>
                </div>
              </li>
            ))}
          </ul>
          <button
            type="button"
            className="btn btn--ghost btn--small"
            onClick={() => {
              persistSaved([]);
              sessionStorage.removeItem(SAVED_KEY);
            }}
          >
            Clear saved
          </button>
        </section>
      )}
    </div>
  );
}
