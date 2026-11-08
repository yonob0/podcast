#!/usr/bin/env python3
"""Télécharge les flux RSS et met à jour data/<id>.json (fusion, sans doublon).
Pour ajouter un podcast : ajouter une entrée dans PODCASTS (et dans PODCASTS de index.html)."""
import html, json, re, sys, urllib.request
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

DATA = Path(__file__).resolve().parent.parent / "data"

PODCASTS = [
    {
        "id": "barre",
        "feed": "https://podcasts.nova.fr/radio-nova-la-chronique-de-pierre-emmanuel-barre/feed/rss/website.xml",
        "page": "https://podcasts.nova.fr/radio-nova-la-chronique-de-pierre-emmanuel-barre",
        "strip": r"\s*-\s*La (?:chronique|grosse semaine) de Pierre-Emmanuel Barré.*$",
        "dir_re": None,
    },
]


def field(block, tag):
    t = re.escape(tag)
    m = re.search(r"<%s(?:\s[^>]*)?>([\s\S]*?)</%s>" % (t, t), block, re.I)
    if not m:
        return ""
    return html.unescape(re.sub(r"<!\[CDATA\[([\s\S]*?)\]\]>", r"\1", m.group(1)).strip())


def fmt_dur(d):
    try:
        p = [int(x) for x in (d or "").strip().split(":")]
    except ValueError:
        return "1 min"
    if len(p) >= 3:
        return f"{p[0]}h{p[1]:02d}" if p[0] else f"{p[1]} min"
    if len(p) == 2:
        return f"{p[0] // 60}h{p[0] % 60:02d}" if p[0] >= 60 else f"{p[0]} min"
    t = p[0]
    return f"{t // 3600}h{round(t % 3600 / 60):02d}" if t >= 3600 else f"{max(1, round(t / 60))} min"


def parse_feed(text, cfg):
    """Lecture tolérante : le flux de Nova n'est pas du XML valide."""
    if not re.search(r"<item[\s>]", text):
        raise ValueError("ce n'est pas un flux RSS")
    out = []
    for it in re.findall(r"<item[\s>][\s\S]*?</item>", text):
        try:
            d = parsedate_to_datetime(field(it, "pubDate"))
        except Exception:
            continue
        raw = re.sub(r"\s+", " ", field(it, "title"))
        title = raw
        if cfg.get("strip"):
            title = re.sub(cfg["strip"], "", raw, flags=re.I).strip() or raw
        link = (field(it, "voxeus:episode-url") or field(it, "link")).split("?")[0].strip()
        ep_id = link or field(it, "guid")
        if not title or not ep_id:
            continue
        director = ""
        if cfg.get("dir_re"):
            m = re.search(cfg["dir_re"], re.sub(r"<[^>]+>", " ", field(it, "description")), re.I)
            if m:
                director = m.group(1).strip()
        out.append({
            "id": ep_id,
            "date": d.astimezone(timezone.utc).strftime("%Y-%m-%d"),
            "dur": fmt_dur(field(it, "itunes:duration")),
            "title": title,
            "url": link or cfg["page"],
            "dir": director,
        })
    if not out:
        raise ValueError("aucun épisode trouvé")
    return out


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; podcast-search-updater)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8", errors="replace")


def main():
    DATA.mkdir(exist_ok=True)
    failed = False
    for cfg in PODCASTS:
        path = DATA / f"{cfg['id']}.json"
        old = []
        if path.exists():
            try:
                old = json.loads(path.read_text(encoding="utf-8")).get("episodes", [])
            except Exception:
                old = []
        try:
            new = parse_feed(fetch(cfg["feed"]), cfg)
        except Exception as e:
            print(f"[{cfg['id']}] ECHEC : {e}")
            failed = True
            continue
        merged = {e["id"]: e for e in old}
        merged.update({e["id"]: e for e in new})
        eps = sorted(merged.values(), key=lambda e: (e["date"], e["id"]), reverse=True)
        if eps == sorted(old, key=lambda e: (e["date"], e["id"]), reverse=True):
            print(f"[{cfg['id']}] deja a jour ({len(eps)} episodes)")
            continue
        body = ",\n".join("  " + json.dumps(e, ensure_ascii=False) for e in eps)
        stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
        path.write_text('{"generated": "%s",\n"episodes": [\n%s\n]}\n' % (stamp, body), encoding="utf-8")
        print(f"[{cfg['id']}] {len(eps)} episodes ({len(eps) - len(old)} nouveaux)")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
