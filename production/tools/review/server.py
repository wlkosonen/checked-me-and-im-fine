#!/usr/bin/env python3
"""The review player's local server (Lati, 26 Oct: frame-exact review with the audio on a zoomable timeline).

    python3 production/tools/review/server.py [--port 8765]      # then open http://127.0.0.1:8765 in the app's browser

Serves index.html and, read-only, the project's media (video with HTTP range requests, so the player can seek) and the
song analysis. /api/list lists the videos to review; /api/meta tells where a clip sits in the song, so the timeline can
show song time, our beats and our words. Markers Lati drops are saved by POST /api/marks to
production/review/marks/<clip>.json, where Kiln reads them. /library is the clip library (library.py's index);
POST /api/use records Lati's pick of a clip for a shot in production/edit/picks-lati.json, which shots.py builds.
POST /api/note records his verdict and note on a clip, from the library or the player (Lati, 26 Oct: "a general note
... right in library"), in production/library/notes.json, verbatim, and updates the library index so "to review" drops
it at once. Listens on 127.0.0.1 only.
"""
import argparse
import json
import mimetypes
import re
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import cutplan  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
MARKS = ROOT / "production/review/marks"
VIDEO_DIRS = ["media/review", "media/board", "media/clips/local", "media/clips/shot", "media/clips/fit",
              "media/clips/preview", "media/clips/grok", "media/reference"]
READABLE = ["media/", "production/board/", "production/edit/", "production/library/"]
PICKS = ROOT / "production/edit/picks-lati.json"
NOTES = ROOT / "production/library/notes.json"
LIB = ROOT / "production/library/clips.json"


def note_for(stem):
    """The verdict library.py would show for a clip: the longest key the file name starts with."""
    notes = json.loads(NOTES.read_text())
    k = max((k for k in notes if k[0] != "_" and stem.startswith(k)), key=len, default=None)
    return dict(notes[k], key=k) if k else None


def save_note(rel, status, text):
    """Lati's own words in quotes, as in the rest of notes.json; any earlier verdict on the clip kept under "earlier"."""
    stem = Path(rel).stem
    notes = json.loads(NOTES.read_text())
    prev = note_for(stem)
    e = {"by": "Lati (review player)", "at": time.strftime("%Y-%m-%d %H:%M")}
    if status or (prev or {}).get("status"):
        e["status"] = status or prev["status"]
    if text.strip():
        e["note"] = f'"{text.strip()}"'
    if not text.strip() and not status:
        e["seen"] = True
    if prev:
        k = prev.pop("key")
        e["earlier"] = prev.pop("earlier", []) + [dict(prev, key=k) if k != stem else prev]
    notes[stem] = e
    NOTES.write_text("{\n" + ",\n".join(f" {json.dumps(k)}: {json.dumps(v, ensure_ascii=False)}"
                                         for k, v in notes.items()) + "\n}\n")
    lib = json.loads(LIB.read_text())
    for c in lib["clips"]:
        if c["id"] == stem:
            st = e.get("status") or c["status"]
            c.update(reviewed=True, verdict=e.get("note") or c["verdict"],
                     status=st if not c["used_by"] or st == "reject" else "in cut")
    LIB.write_text(json.dumps(lib, indent=1) + "\n")
    return e


def song_offset(rel):
    """Song time of the clip's first frame, when known."""
    p = ROOT / rel
    name = p.name
    if re.match(r"(\d\d-)?roughcut", name):
        return 0.0
    if "/clips/fit/" in rel or "/clips/preview/" in rel:
        side = p.with_suffix(".json")
        if side.exists():
            return json.loads(side.read_text())["t0"]
    board = json.loads((ROOT / "production/board/board.json").read_text())
    if "/clips/shot/" in rel:
        s = next((s for s in board["shots"] if s["id"] == p.stem), None)
        return s["t0"] if s else None
    m = re.match(r"(?:\d\d-)?([SM]\d{3}[A-E]?)-", name)
    if m:
        if m.group(1).startswith("S029") and len(m.group(1)) == 5:
            return 65.40  # the "fine" versions
        c = next((c for c in board["clips"] if c["id"] == m.group(1)), None)
        return c["t0"] if c else None
    return None


class H(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def send_json(self, obj, code=200):
        b = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b)))
        self.end_headers()
        self.wfile.write(b)

    def do_GET(self):
        u = urlparse(self.path)
        q = parse_qs(u.query)
        if u.path in ("/", "/index.html"):
            return self.send_file(HERE / "index.html")
        if u.path in ("/library", "/library.html"):
            return self.send_file(HERE / "library.html")
        if u.path == "/help.js":
            return self.send_file(HERE / "help.js")
        if u.path in ("/cut", "/cut.html"):
            return self.send_file(HERE / "cut.html")
        if u.path == "/api/cutplan":
            return self.send_json(cutplan.plan(gfx=q.get("gfx", ["1"])[0] != "0"))
        if u.path == "/api/picks":
            return self.send_json(json.loads(PICKS.read_text()) if PICKS.exists() else [])
        if u.path == "/api/list":
            out = []
            for d in VIDEO_DIRS:
                for f in sorted((ROOT / d).rglob("*.mp4"), key=lambda x: -x.stat().st_mtime):
                    if ".video." not in f.name:
                        out.append({"path": str(f.relative_to(ROOT)), "mtime": f.stat().st_mtime})
            return self.send_json(out)
        if u.path == "/api/meta":
            rel = q.get("path", [""])[0]
            mf = MARKS / (Path(rel).stem + ".json")
            return self.send_json({"offset": song_offset(rel), "note": note_for(Path(rel).stem),
                                   "marks": json.loads(mf.read_text())["marks"] if mf.exists() else []})
        rel = unquote(u.path.lstrip("/"))
        if any(rel.startswith(r) for r in READABLE) and ".." not in rel:
            return self.send_file(ROOT / rel)
        self.send_error(404)

    def do_POST(self):
        path = urlparse(self.path).path
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        if path == "/api/use":  # Lati picks a clip for a shot: shots.py builds it into the next rough cut
            picks = [p for p in (json.loads(PICKS.read_text()) if PICKS.exists() else []) if p["shot"] != body["shot"]]
            if body.get("clip"):
                picks.append({"shot": body["shot"], "clip": body["clip"], "in": body.get("in"), "out": body.get("out"),
                              "offset": song_offset(body["clip"]), "at": time.strftime("%Y-%m-%d %H:%M:%S")})
            PICKS.write_text(json.dumps(sorted(picks, key=lambda p: p["shot"]), indent=1) + "\n")
            return self.send_json({"ok": True, "picks": len(picks)})
        if path == "/api/note":
            return self.send_json({"ok": True, "note": save_note(body["path"], body.get("status") or "",
                                                                 body.get("note") or "")})
        if path == "/api/marks/clear":  # a new cut to review: the notes move to marks/archive, nothing is deleted
            f = MARKS / "cut.json"
            if f.exists():
                (MARKS / "archive").mkdir(exist_ok=True)
                f.rename(MARKS / "archive" / time.strftime("cut-%Y-%m-%d-%H%M%S.json"))
            return self.send_json({"ok": True})
        if path != "/api/marks":
            return self.send_error(404)
        MARKS.mkdir(parents=True, exist_ok=True)
        rel = body["path"]
        (MARKS / (Path(rel).stem + ".json")).write_text(json.dumps(
            {"clip": rel, "song_offset": song_offset(rel), "saved": time.strftime("%Y-%m-%d %H:%M:%S"),
             "marks": body["marks"]}, indent=1) + "\n")
        self.send_json({"ok": True})

    def send_file(self, p):
        if not p.is_file():
            return self.send_error(404)
        size = p.stat().st_size
        ctype = mimetypes.guess_type(p.name)[0] or "application/octet-stream"
        rng = self.headers.get("Range")
        start, end = 0, size - 1
        if rng:
            m = re.match(r"bytes=(\d*)-(\d*)", rng)
            if m.group(1):
                start = int(m.group(1))
                end = int(m.group(2)) if m.group(2) else size - 1
            else:
                start = size - int(m.group(2))
            self.send_response(206)
            self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
        else:
            self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Accept-Ranges", "bytes")
        self.send_header("Content-Length", str(end - start + 1))
        self.end_headers()
        with p.open("rb") as f:
            f.seek(start)
            left = end - start + 1
            while left > 0:
                chunk = f.read(min(1 << 20, left))
                if not chunk:
                    break
                try:
                    self.wfile.write(chunk)
                except (BrokenPipeError, ConnectionResetError):
                    return
                left -= len(chunk)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8765)
    a = ap.parse_args()
    print(f"review player: http://127.0.0.1:{a.port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", a.port), H).serve_forever()
