// Every fetch() to the backend lives here. Nothing else talks to the server.
const API = (() => {
  // Served by FastAPI -> same address. Opened with Live Server (port 5500) -> backend on 8000.
  const BASE = location.port === "5500" ? "http://127.0.0.1:8000" : "";
  // Add ?mock=1 to the page address to work without a backend.
  const MOCK = new URLSearchParams(location.search).has("mock");

  async function get(path) {
    let res;
    try {
      res = await fetch(BASE + path);
    } catch (e) {
      throw { error: "backend_unreachable", message: "Cannot reach the MIZAN backend. Is uvicorn running?" };
    }
    const body = await res.json().catch(() => ({}));
    if (!res.ok) throw body.error ? body : { error: "http_" + res.status, message: "The server answered " + res.status + "." };
    return body;
  }

  const mockVariables = [
    { code: "T2M", question: "Is it getting hotter?", name: "Average temperature", unit: "°C", definition: "", confidence: "high" },
    { code: "PRECTOTCORR", question: "Is it raining less?", name: "Rainfall", unit: "mm/year", definition: "", confidence: "low" },
  ];

  return {
    mock: MOCK,
    health: () => (MOCK ? Promise.resolve({ status: "ok" }) : get("/api/health")),
    variables: () => (MOCK ? Promise.resolve(mockVariables) : get("/api/variables")),
    presets: () => (MOCK ? Promise.resolve([{ id: "essaouira", name: "Essaouira coast", lat: 31.51, lon: -9.77 }]) : get("/api/presets")),
    analyze: (lat, lon, variable, name) => {
      if (MOCK) return fetch("mock/analyze.json").then((r) => r.json());
      const q = new URLSearchParams({ lat: lat.toFixed(3), lon: lon.toFixed(3), variable });
      if (name) q.set("name", name);
      return get("/api/analyze?" + q);
    },
  };
})();
