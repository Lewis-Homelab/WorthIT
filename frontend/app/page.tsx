const API_URL = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

async function getApiStatus(): Promise<string> {
  try {
    const res = await fetch(`${API_URL}/health`, { cache: "no-store" });
    if (!res.ok) return "unreachable";
    const data = (await res.json()) as { status?: string };
    return data.status ?? "unknown";
  } catch {
    return "unreachable";
  }
}

export default async function Home() {
  const apiStatus = await getApiStatus();

  return (
    <main>
      <span className="badge">Phase 1</span>
      <h1>WorthIT</h1>
      <p>
        Plan high-value adventures — rank experiences by joy per pound, not
        just cost or popularity.
      </p>

      <div className="card">
        <h2>Stack</h2>
        <ul>
          <li>PostgreSQL — attractions, restaurants, hikes, viewpoints</li>
          <li>FastAPI — places API + health checks</li>
          <li>Next.js — web UI (you are here)</li>
          <li>Google Places API + OpenStreetMap — data sources (next)</li>
        </ul>
      </div>

      <p className={`status ${apiStatus === "ok" ? "ok" : "error"}`}>
        API status: {apiStatus} ({API_URL})
      </p>

      <div className="links">
        <a href={`${API_URL}/docs`}>API docs</a>
        <a href={`${API_URL}/places`}>Places endpoint</a>
      </div>
    </main>
  );
}
