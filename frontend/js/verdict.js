// Verdict card built only from the JSON verdict and trend.
const Verdict = (() => {
  const LABELS = {
    significant_robust: "Clear change",
    significant_fragile: "Possible change",
    no_clear_trend: "No clear change",
    insufficient_data: "Not enough data",
  };
  const esc = (s) => String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const pText = (p) => (p == null ? "–" : p < 0.001 ? "< 0.001" : p.toFixed(3));
  const sgn = (x) => (x > 0 ? "+" : "") + (Math.abs(x) >= 10 ? x.toFixed(0) : Math.abs(x) >= 1 ? x.toFixed(1) : x.toFixed(2));

  function head(slot, name, closable) {
    const color = slot === "A" ? "var(--place-a)" : "var(--place-b)";
    return `<div class="place"><span class="dot" style="background:${color}"></span>${slot} · ${esc(name)}</div>` +
      (closable ? `<button class="close" data-close="${slot}" aria-label="Remove place">×</button>` : "");
  }

  function loading(slot, name, closable) {
    return `<article class="card loading">${head(slot, name, closable)}<h3>Weighing 45 years of data…</h3></article>`;
  }

  function failed(slot, name, err, closable) {
    return `<article class="card">${head(slot, name, closable)}<h3 class="err">Could not analyse this place</h3>
      <p class="expl">${esc(err.message || "Unknown error")}</p></article>`;
  }

  function card(slot, r, closable) {
    const v = r.verdict, t = r.trend;
    const unit = r.variable.unit.replace("/year", "");
    const stats = t ? `
      <div class="stats">
        <div class="stat"><b>${sgn(t.slope_per_decade)} ${esc(unit)}</b><span>per decade (Sen)</span></div>
        <div class="stat"><b>${sgn(t.ci95[0])} … ${sgn(t.ci95[1])}</b><span>95% range</span></div>
        <div class="stat"><b>p ${pText(t.p_value)}</b><span>${t.robustness.methods_agree ? "3 of 3 methods agree" : "methods differ"}</span></div>
      </div>` : "";
    return `<article class="card ${v.label}">
      ${head(slot, r.location.name, closable)}
      <span class="badge ${v.label}">${LABELS[v.label] || v.label}</span>
      <h3>${esc(v.headline)}</h3>
      <p class="expl">${esc(v.explanation)}</p>
      ${stats}
      <ul class="caveats">${v.caveats.map((c) => `<li>${esc(c)}</li>`).join("")}</ul>
    </article>`;
  }

  return { card, loading, failed };
})();
