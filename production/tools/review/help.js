// A "?" button and an overlay listing the page's hotkeys (Lati, 26 Oct). Each page sets window.HELP = [[keys, what], ...].
(function () {
  const b = document.createElement("button");
  b.textContent = "?"; b.title = "Hotkeys (?)";
  b.style.cssText = "position:fixed;top:8px;right:12px;z-index:20;width:28px;height:28px;border-radius:50%;" +
    "background:#1a1c1f;color:#e8875a;border:1px solid #e8875a;font:700 15px system-ui;cursor:pointer";
  const o = document.createElement("div");
  o.style.cssText = "position:fixed;inset:0;z-index:30;background:rgba(0,0,0,.72);display:none;align-items:center;justify-content:center";
  const p = document.createElement("div");
  p.style.cssText = "background:#1a1c1f;border:1px solid #2b2e33;border-radius:8px;padding:16px 20px;max-width:560px;color:#e6e6e6;font:13px/1.6 system-ui";
  o.appendChild(p);
  function show() {
    p.innerHTML = "<div style='font-weight:600;margin-bottom:8px'>Hotkeys</div><table>" + (window.HELP || []).map(([k, w]) =>
      `<tr><td style="padding:2px 14px 2px 0;white-space:nowrap">${k.split(" ").map(x => `<kbd style="background:#111214;border:1px solid #2b2e33;border-radius:3px;padding:0 5px">${x}</kbd>`).join(" ")}</td><td style="color:#c9ccd1">${w}</td></tr>`).join("") +
      "</table><div style='margin-top:10px;color:#8a8f98'>Esc or click to close</div>";
    o.style.display = "flex";
  }
  b.onclick = show; o.onclick = () => o.style.display = "none";
  window.addEventListener("keydown", e => {
    if (e.key === "?" && !(e.target.tagName === "INPUT" && e.target.type === "text")) { e.preventDefault(); o.style.display === "flex" ? o.style.display = "none" : show(); }
    if (e.key === "Escape") o.style.display = "none";
  });
  document.addEventListener("DOMContentLoaded", () => document.body.append(b, o));
  if (document.body) document.body.append(b, o);
})();
