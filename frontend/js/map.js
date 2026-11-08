// Leaflet map: presets, click -> lat/lon, one marker per place slot.
const MapView = (() => {
  let map;
  const markers = {};
  const colors = () => {
    const s = getComputedStyle(document.documentElement);
    return { A: s.getPropertyValue("--place-a").trim(), B: s.getPropertyValue("--place-b").trim() };
  };

  function init(onPick) {
    map = L.map("map", { worldCopyJump: true }).setView([31.8, -7.5], 6);
    L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 12,
      attribution: "&copy; OpenStreetMap contributors",
    }).addTo(map);
    map.on("click", (e) => onPick({ lat: e.latlng.lat, lon: e.latlng.lng, name: null }));
  }

  function setMarker(slot, place) {
    if (markers[slot]) markers[slot].remove();
    if (!place) { delete markers[slot]; return; }
    const c = colors()[slot];
    markers[slot] = L.circleMarker([place.lat, place.lon], {
      radius: 9, color: c, weight: 3, fillColor: c, fillOpacity: 0.35,
    }).addTo(map).bindTooltip(`${slot}: ${place.name || place.lat.toFixed(2) + ", " + place.lon.toFixed(2)}`);
  }

  function flyTo(place) { map.flyTo([place.lat, place.lon], Math.max(map.getZoom(), 7), { duration: 0.6 }); }

  return { init, setMarker, flyTo };
})();
