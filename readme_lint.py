#!/usr/bin/env python3
"""readme-lint: score a README (0-100) and report what is missing, including broken relative links."""
import argparse, json, os, re, sys

__version__ = "0.1.0"
# (code, points, message, regex over headings OR body)
HEADING = re.compile(r"^#{1,6}\s+(.+?)\s*#*$", re.M)
RULES = [
    ("title", 10, "no top-level title (# …)", None),
    ("description", 15, "no description paragraph right after the title", None),
    ("install", 15, "no Install / Getting started section", r"install|getting started|setup|set up|quick ?start|導入|インストール|セットアップ"),
    ("usage", 20, "no Usage / Example section", r"usage|example|how to|使い方|使用方法|例"),
    ("license", 10, "no License section or mention", r"licen[sc]e|ライセンス"),
    ("code", 10, "no code block (``` … ```)", None),
    ("contributing", 5, "no Contributing section", r"contribut|貢献|コントリビュート"),
]
LINK = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)|!\[[^\]]*\]\(([^)\s]+)\)")


def strip_code(text):
    return re.sub(r"```.*?```", "", text, flags=re.S)


def anchors(text):
    out = set()
    for h in HEADING.findall(strip_code(text)):
        a = re.sub(r"[^\w\- 　]", "", h.strip().lower()).replace(" ", "-")
        out.add(a)
    return out


def broken_links(text, base_dir):
    bad = []
    body = strip_code(text)
    heads = anchors(text)
    for m in LINK.finditer(body):
        url = m.group(1) or m.group(2)
        if re.match(r"^[a-z][a-z0-9+.-]*:", url, re.I) or url.startswith("//"):
            continue
        path, _, frag = url.partition("#")
        if not path:
            if frag and frag.lower() not in heads:
                bad.append(url)
        elif not os.path.exists(os.path.join(base_dir, path.split("?")[0])):
            bad.append(url)
    return bad


def lint(text, base_dir="."):
    """Return (score, findings)."""
    body = strip_code(text)
    headings = " | ".join(HEADING.findall(body)).lower()
    findings, score = [], 0
    lines = [l for l in body.splitlines()]
    first = next((i for i, l in enumerate(lines) if l.startswith("# ")), None)
    for code, pts, msg, rx in RULES:
        if code == "title":
            ok = first is not None
        elif code == "description":
            after = lines[first + 1:] if first is not None else []
            para = next((l for l in after if l.strip() and not l.startswith(("#", "[", "!", "<", "```", "|", "-", "*", ">"))), "")
            ok = len(para.strip()) >= 10
        elif code == "code":
            ok = "```" in text
        else:
            ok = bool(re.search(rx, headings, re.I))
            if code == "license" and not ok:
                ok = bool(re.search(r"licen[sc]e|ライセンス", body, re.I))
        if ok:
            score += pts
        else:
            findings.append({"code": code, "points": pts, "message": msg})
    bad = broken_links(text, base_dir)
    if not bad:
        score += 15
    else:
        findings.append({"code": "broken-links", "points": 15, "message": "broken relative links: " + ", ".join(bad)})
    return score, findings


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("file", nargs="?", default="README.md")
    p.add_argument("--min-score", type=int, default=0, help="exit 1 if score is below this (for CI)")
    p.add_argument("--json", action="store_true")
    p.add_argument("--version", action="version", version=__version__)
    a = p.parse_args(argv)
    try:
        with open(a.file, encoding="utf-8") as fh:
            text = fh.read()
    except OSError as e:
        print(f"readme-lint: {e}", file=sys.stderr)
        return 2
    score, findings = lint(text, os.path.dirname(os.path.abspath(a.file)))
    if a.json:
        print(json.dumps({"score": score, "findings": findings}, indent=2, ensure_ascii=False))
    else:
        for f in findings:
            print(f"✗ -{f['points']:<3} {f['message']}")
        print(f"\nscore: {score}/100")
    return 1 if score < a.min_score else 0


if __name__ == "__main__":
    sys.exit(main())
