// Wires everything together: state and flow.
const state = {
  variables: [],
  variable: "T2M",
  places: { A: null, B: null },     // {lat, lon, name}
  results: { A: null, B: null },    // API answers or {error}
  picking: "A",                     // which slot the next map click fills
  view: "annual",
};

const $ = (id) => document.getElementById(id);

function renderQuestions() {
  const conf = { high: "good confidence", medium: "medium confidence", low: "lower confidence" };
  $("questions").innerHTML = state.variables.map((v) =>
    `<button class="q ${v.code === state.variable ? "on" : ""}" role="radio" aria-checked="${v.code === state.variable}" data-code="${v.code}">
       <span>${v.question}</span><span class="conf">${conf[v.confidence] || ""}</span></button>`).join("");
  const cur = state.variables.find((v) => v.code === state.variable);
  $("definition").textContent = cur ? `${cur.name} (${cur.unit}): ${cur.definition}` : "";
}

function renderCards() {
  const slots = ["A", "B"].filter((s) => state.places[s]);
  if (!slots.length) {
    $("cards").innerHTML = `<div class="empty">Choose a question and a place to see the verdict.</div>`;
  } else {
    $("cards").innerHTML = slots.map((s) => {
      const p = state.places[s], r = state.results[s], closable = s === "B";
      const name = p.name || `${p.lat.toFixed(2)}, ${p.lon.toFixed(2)}`;
      if (!r) return Verdict.loading(s, name, closable);
      if (r.error) return Verdict.failed(s, name, r, closable);
      return Verdict.card(s, r, closable);
    }).join("");
  }
  const ok = Object.fromEntries(Object.entries(state.results).filter(([, r]) => r && !r.error));
  const first = Object.values(ok)[0];
  $("chartTitle").textContent = first ? `${first.variable.name}, ${state.view === "annual" ? "year by year" : "month by month vs. normal"}` : "Year by year";
  $("source").textContent = first ? first.source : "";
  Charts.draw(ok, state.view);
}

async function load(slot) {
  const p = state.places[slot];
  if (!p) return;
  state.results[slot] = null;
  renderCards();
  const asked = { ...p, variable: state.variable };
  let result;
  try {
    result = await API.analyze(p.lat, p.lon, state.variable, p.name);
  } catch (err) {
    result = err.error ? err : { error: "unknown", message: String(err) };
  }
  // Ignore stale answers if the user changed something meanwhile.
  const now = state.places[slot];
  if (!now || now.lat !== asked.lat || now.lon !== asked.lon || state.variable !== asked.variable) return;
  state.results[slot] = result;
  renderCards();
}

function pickPlace(place) {
  const slot = state.picking;
  state.places[slot] = place;
  MapView.setMarker(slot, place);
  if (slot === "B") setPicking("A");
  load(slot);
}

function setPicking(slot) {
  state.picking = slot;
  $("compareBtn").classList.toggle("active", slot === "B");
  $("compareHint").hidden = slot !== "B";
}

function removeB() {
  state.places.B = null;
  state.results.B = null;
  MapView.setMarker("B", null);
  setPicking("A");
  renderCards();
}

async function start() {
  MapView.init(pickPlace);

  $("questions").addEventListener("click", (e) => {
    const b = e.target.closest(".q");
    if (!b || b.dataset.code === state.variable) return;
    state.variable = b.dataset.code;
    renderQuestions();
    load("A"); load("B");
  });

  $("compareBtn").addEventListener("click", () => setPicking(state.picking === "B" ? "A" : "B"));
  $("cards").addEventListener("click", (e) => { if (e.target.dataset.close === "B") removeB(); });

  document.querySelectorAll(".seg button").forEach((b) => b.addEventListener("click", () => {
    document.querySelectorAll(".seg button").forEach((x) => x.classList.toggle("on", x === b));
    state.view = b.dataset.view;
    renderCards();
  }));

  try {
    await API.health();
    $("status").textContent = API.mock ? "mock data" : "backend online";
    $("status").className = "status ok";
  } catch (e) {
    $("status").textContent = "backend offline";
    $("status").className = "status bad";
    $("cards").innerHTML = `<div class="empty">${e.message}</div>`;
    return;
  }

  const [vars, presets] = await Promise.all([API.variables(), API.presets()]);
  state.variables = vars;
  if (!vars.some((v) => v.code === state.variable)) state.variable = vars[0].code;
  renderQuestions();

  $("presets").innerHTML = presets.map((p, i) => `<button class="chip" data-i="${i}">${p.name}</button>`).join("");
  $("presets").addEventListener("click", (e) => {
    const b = e.target.closest(".chip");
    if (!b) return;
    const p = presets[+b.dataset.i];
    MapView.flyTo(p);
    pickPlace({ lat: p.lat, lon: p.lon, name: p.name });
  });

  // Start with the home case so the page is never empty.
  const home = presets[0];
  pickPlace({ lat: home.lat, lon: home.lon, name: home.name });
}

start();
