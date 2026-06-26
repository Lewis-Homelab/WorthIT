"use client";

import {
  INTEREST_OPTIONS,
  type DayPlanPreferences,
} from "@/lib/types";

interface PreferencesFormProps {
  prefs: DayPlanPreferences;
  onChange: (prefs: DayPlanPreferences) => void;
  disabled?: boolean;
}

/** Budget, time, and interest controls — maps to the POST /recommendations body. */
export function PreferencesForm({
  prefs,
  onChange,
  disabled = false,
}: PreferencesFormProps) {
  function toggleInterest(id: string) {
    const next = prefs.interests.includes(id)
      ? prefs.interests.filter((i) => i !== id)
      : [...prefs.interests, id];
    onChange({ ...prefs, interests: next.length ? next : [id] });
  }

  return (
    <section className="prefs" aria-labelledby="prefs-heading">
      <h2 id="prefs-heading" className="prefs__heading">
        Your Saturday
      </h2>
      <p className="prefs__hint">
        Set your constraints — we&apos;ll rank complete day experiences, not
        individual pins.
      </p>

      <div className="prefs__row">
        <label className="prefs__field" htmlFor="budget">
          Budget
          <span className="prefs__value">£{prefs.budget_gbp}</span>
        </label>
        <input
          id="budget"
          type="range"
          min={10}
          max={150}
          step={5}
          value={prefs.budget_gbp}
          disabled={disabled}
          onChange={(e) =>
            onChange({ ...prefs, budget_gbp: Number(e.target.value) })
          }
        />
      </div>

      <div className="prefs__row">
        <label className="prefs__field" htmlFor="hours">
          Time available
          <span className="prefs__value">{prefs.max_hours} hours</span>
        </label>
        <input
          id="hours"
          type="range"
          min={2}
          max={10}
          step={0.5}
          value={prefs.max_hours}
          disabled={disabled}
          onChange={(e) =>
            onChange({ ...prefs, max_hours: Number(e.target.value) })
          }
        />
      </div>

      <fieldset className="prefs__interests" disabled={disabled}>
        <legend>Interests</legend>
        <div className="prefs__chips">
          {INTEREST_OPTIONS.map(({ id, label }) => {
            const active = prefs.interests.includes(id);
            return (
              <button
                key={id}
                type="button"
                className={`chip ${active ? "chip--active" : ""}`}
                aria-pressed={active}
                onClick={() => toggleInterest(id)}
              >
                {label}
              </button>
            );
          })}
        </div>
      </fieldset>
    </section>
  );
}
