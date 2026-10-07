#!/usr/bin/env python3
"""One command per document: quality checks + render + layout checks.
  python3 build.py resume resume.json keywords.txt extra_numbers.txt   -> resume.pdf
resume.json may be a short EDIT file: {"base": "data_bi" | "ai_ml" | "supply_chain", then only what changes:
  "tagline", "summary", "skills", "certifications" (replace whole field),
  "bullets": {"<role index 0-3>": ["...", ...]} (replace that role's bullets),
  "projects": ["<name from projects.json>" or a full project object, ...]}
It is merged with bases/<base>.json and projects.json into resume.full.json before checking.
  python3 build.py letter letter.json                                  -> letter.pdf
Prints a short report ending in 'BUILD: PASS <bytes>' or 'BUILD: FAIL'. Exit code 1 on failure.
Add --show to also write page images (pg-1.jpg, ...) for a visual check."""
import sys, subprocess, re, os
HERE = os.path.dirname(os.path.abspath(__file__))
kind, src = sys.argv[1], sys.argv[2]
show = "--show" in sys.argv
out = f"{kind}.pdf"
fail = []
if kind == "resume":
    import json
    d = json.load(open(src))
    if "base" in d:
        full = json.load(open(os.path.join(HERE, "bases", d["base"] + ".json")))
        for k in ("tagline", "summary", "skills", "certifications", "experience", "projects"):
            if k in d: full[k] = d[k]
        for i, b in d.get("bullets", {}).items(): full["experience"][int(i)]["bullets"] = b
        lib = json.load(open(os.path.join(HERE, "projects.json")))
        full["projects"] = [lib[p] if isinstance(p, str) else p for p in full.get("projects", [])]
        src = "resume.full.json"; json.dump(full, open(src, "w"), indent=1)
def run(*a):
    r = subprocess.run(a, capture_output=True, text=True); return r.returncode, (r.stdout + r.stderr).strip()
if kind == "resume":
    rest = [x for x in sys.argv[3:] if x != "--show"]
    code, txt = run(sys.executable, os.path.join(HERE, "check.py"), src, *rest)
    print(txt)
    if code: fail.append("content checks failed (see above)")
code, txt = run(sys.executable, os.path.join(HERE, "render_pdf.py"), kind, src, out)
if code: print(txt); fail.append("render failed or produced non-ASCII bytes")
else:
    pages = int(re.search(r"Pages:\s+(\d+)", run("pdfinfo", out)[1]).group(1))
    want = 2 if kind == "resume" else 1
    if pages != want: fail.append(f"{pages} pages (need exactly {want}): shorten or lengthen bullets")
    xml = run("pdftotext", "-bbox", out, "-")[1]
    pgs = xml.split("<page")[1:]
    h = float(re.search(r'height="([\d.]+)"', pgs[0]).group(1))
    fills = [round(100 * max(float(m) for m in re.findall(r'yMax="([\d.]+)"', p)) / h) for p in pgs]
    print("page fill %:", fills)
    if kind == "resume" and len(fills) == 2 and fills[1] < 62: fail.append(f"page 2 only {fills[1]}% full (need 62%+): add a bullet or project detail")
    if kind == "resume" and fills and fills[0] < 80: fail.append(f"page 1 only {fills[0]}% full: content is jumping to page 2, trim the block that moved")
    last = [l for l in run("pdftotext", "-layout", "-f", "1", "-l", "1", out, "-")[1].splitlines() if l.strip()]
    if last and re.fullmatch(r"\s*[A-Z &]{4,}\s*", last[-1]): fail.append("section heading stranded at bottom of page 1")
    if show: run("pdftoppm", "-jpeg", "-r", "70", out, "pg"); print("page images: pg-*.jpg")
size = os.path.getsize(out) if os.path.exists(out) else 0
if fail:
    print("BUILD: FAIL"); [print(" -", f) for f in fail]; sys.exit(1)
print(f"BUILD: PASS {size}")
