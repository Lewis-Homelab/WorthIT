/** Mirrors app/engine/schemas.py — keep in sync with the API. */

export interface DayPlanStop {
  name: string;
  category: string;
  latitude: number;
  longitude: number;
  estimated_cost_gbp: number;
  dwell_minutes: number;
  experience_score: number;
  rating: number;
  hygiene_rating: number | null;
}

export interface DayPlanCard {
  template_id: string;
  title: string;
  emoji: string;
  score: number;
  walk_minutes: number | null;
  dwell_minutes: number | null;
  total_minutes: number | null;
  total_hours: number;
  cost_gbp: number | null;
  weather_summary: string;
  stops: DayPlanStop[];
}

export interface DayPlanResponse {
  area: string;
  plans: DayPlanCard[];
  weather: Record<string, string | number | boolean>;
}

export interface DayPlanPreferences {
  budget_gbp: number;
  max_hours: number;
  interests: string[];
  limit: number;
}

export const INTEREST_OPTIONS = [
  { id: "coffee", label: "Coffee" },
  { id: "museum", label: "Museums" },
  { id: "pub", label: "Pubs" },
  { id: "walk", label: "Walks" },
  { id: "food", label: "Food" },
  { id: "culture", label: "Culture" },
  { id: "library", label: "Libraries" },
  { id: "history", label: "History" },
] as const;
