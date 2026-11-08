// Plotly chart drawn only from the JSON series.
const Charts = (() => {
  const css = (v) => getComputedStyle(document.documentElement).getPropertyValue(v).trim();

  function draw(results, view) {
    const el = document.getElementById("chart");
    const entries = Object.entries(results).filter(([, r]) => r && r.series);
    if (!entries.length) { Plotly.purge(el); return Promise.resolve(); }

    const traces = [];
    for (const [slot, r] of entries) {
      const color = css(slot === "A" ? "--place-a" : "--place-b");
      const label = r.location.name;
      if (view === "annual") {
        traces.push({
          x: r.series.annual.map((d) => d.year), y: r.series.annual.map((d) => d.value),
          name: label, mode: "lines+markers", line: { color, width: 2 }, marker: { size: 4 },
          hovertemplate: `%{x}: %{y:.2f} ${r.variable.unit}<extra>${label}</extra>`,
        });
        if (r.trend && r.trend.line) {
          const sig = r.verdict.label.startsWith("significant");
          traces.push({
            x: r.trend.line.map((d) => d.year), y: r.trend.line.map((d) => d.value),
            name: `Trend (${label})`, mode: "lines", hoverinfo: "skip",
            line: { color, width: sig ? 3 : 2, dash: sig ? "solid" : "dot" },
          });
        }
      } else {
        traces.push({
          x: r.series.monthly_anomaly.map((d) => d.date + "-15"), y: r.series.monthly_anomaly.map((d) => d.value),
          name: label, mode: "lines", line: { color, width: 1 }, opacity: entries.length > 1 ? 0.7 : 0.9,
          hovertemplate: `%{x|%b %Y}: %{y:+.2f}<extra>${label}</extra>`,
        });
      }
    }

    const r0 = entries[0][1];
    const unit = view === "annual" ? r0.variable.unit : r0.variable.unit.replace("/year", "/month") + " vs. normal";
    const ink = css("--ink"), muted = css("--muted"), line = css("--line");
    return Plotly.react(el, traces, {
      margin: { l: 56, r: 12, t: 8, b: 40 },
      paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)",
      font: { color: ink, family: "system-ui, sans-serif", size: 12 },
      xaxis: { gridcolor: line, color: muted, type: view === "annual" ? "linear" : "date" },
      yaxis: { gridcolor: line, color: muted, title: { text: unit }, zeroline: view !== "annual", zerolinecolor: muted },
      legend: { orientation: "h", y: -0.18 },
      hovermode: "x unified",
    }, { responsive: true, displaylogo: false, modeBarButtonsToRemove: ["lasso2d", "select2d"] });
  }

  // Plotly fails if a redraw starts before the previous one finished: queue them.
  let queue = Promise.resolve();
  const drawQueued = (results, view) => {
    queue = queue.then(() => draw(results, view)).catch((e) => console.warn("chart:", e));
    return queue;
  };

  return { draw: drawQueued };
})();
