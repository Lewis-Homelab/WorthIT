import type { DayPlanPreferences, DayPlanResponse } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://homelab:8000";

/** First recommendation request can take 1–2 min while the walking graph loads. */
const FETCH_TIMEOUT_MS = 180_000;

export function getApiUrl(): string {
  return API_URL;
}

export async function fetchHealth(): Promise<"ok" | "unreachable"> {
  try {
    const res = await fetch(`${API_URL}/health`, { cache: "no-store" });
    if (!res.ok) return "unreachable";
    const data = (await res.json()) as { status?: string };
    return data.status === "ok" ? "ok" : "unreachable";
  } catch {
    return "unreachable";
  }
}

export async function fetchDayPlans(
  prefs: DayPlanPreferences,
): Promise<DayPlanResponse> {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);

  try {
    const res = await fetch(`${API_URL}/recommendations/day-plans`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        budget_gbp: prefs.budget_gbp,
        max_hours: prefs.max_hours,
        interests: prefs.interests,
        limit: prefs.limit,
      }),
      signal: controller.signal,
      cache: "no-store",
    });

    if (!res.ok) {
      const detail = await res.text();
      throw new Error(
        res.status === 503
          ? "Recommendation data not available. Ensure data/raw/ is mounted in the API container."
          : `API error ${res.status}: ${detail}`,
      );
    }

    return (await res.json()) as DayPlanResponse;
  } catch (err) {
    if (err instanceof Error && err.name === "AbortError") {
      throw new Error(
        "Request timed out. The first load builds the walking graph and can take a few minutes.",
      );
    }
    throw err;
  } finally {
    clearTimeout(timeout);
  }
}
