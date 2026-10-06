#!/usr/bin/env python3
"""Quality gate for a generated resume.  Usage: python3 check.py resume.json keywords.txt [extra_numbers.txt]
extra_numbers.txt (optional) = numbers that appear in the 0b_Fact_Updates docs, one per line, exactly as written (e.g. 35 or 1,200).
keywords.txt = one lowercase keyword/phrase per line taken from the job description (only ones that are true of the candidate).
Exit code 1 = must fix before uploading."""
import json, re, sys
d = json.load(open(sys.argv[1])); kws = [k.strip().lower() for k in open(sys.argv[2]) if k.strip()]
exp_text = " ".join(j["title"]+" "+j["org"]+" "+" ".join(j["bullets"]) for j in d["experience"])
all_text = " ".join([d["summary"], " ".join(v for _, v in d["skills"]), exp_text,
    " ".join(p["name"]+" "+p.get("tools","")+" "+" ".join(p["bullets"]) for p in d.get("projects", [])),
    d.get("tagline", ""),
    " ".join(d["certifications"]) if isinstance(d.get("certifications"), list) else d.get("certifications", "")])
t = " ".join(all_text.lower().split())
fail = []
# 1 keyword coverage
hit = [k for k in kws if k in t]; miss = [k for k in kws if k not in t]
score = round(100*len(hit)/max(1,len(kws)))
print(f"ATS keyword coverage: {len(hit)}/{len(kws)} = {score}%"); print("missing:", miss)
# 2 stuffing: any multi-word JD phrase used more than twice
TOOLS = {"power bi","power automate","power query","sql server","google tag manager","google analytics","ms office","github actions","data quality","machine learning","data science"}
for k in kws:
    if " " in k and k not in TOOLS and t.count(k) > 2: fail.append(f"stuffing: '{k}' appears {t.count(k)} times (max 2)")
# 3 banned words / punctuation
for pat in ["—","–","leverag","spearhead","passionate","robust","seamless","utiliz","synerg","cutting-edge","delve","meticulous","comprehensive","organis","analys(e|ed|ing) ","behaviour","visualis","colour"]:
    if re.search(pat, t): fail.append(f"banned word/char: {pat}")
# 4 stale or forbidden facts
for pat in ["4.0 gpa","gpa 4.0","gpa: 4.0","data analyst intern","yolov8","capstone","opt","sponsorship","visa","ead","citizen","bigquery","snowflake","dbt","airflow","spark","looker"]:
    if re.search(r"\b"+re.escape(pat)+r"\b", t): fail.append(f"forbidden/stale term: {pat}")
# 5 Criminal Case System Analysis: no dataset sizes and no findings anywhere
for pat in [r"5,800", r"12,200", r"27,700"]:
    if re.search(pat, t): fail.append(f"case-analysis dataset size on the resume: {pat}")
for pat in ["delay driver","2.5x","dominant driver","main driver"]:
    if pat in t: fail.append(f"states a finding from the case analysis: {pat}")
# 6 numbers not on the approved list
allowed = {"3.97","4.0","8.55","10","900","650","30","60","80","94","92","99","98","467","2,894","100","5","20","25","11","48","7","1","2","3","8"}
if len(sys.argv) > 3:
    allowed |= {x.strip() for x in open(sys.argv[3]) if x.strip()}
for n in re.findall(r"(?<![\w.])\d[\d,]*(?:\.\d+)?", all_text):
    if n.rstrip(",") not in allowed and not re.fullmatch(r"(19|20)\d\d", n): fail.append(f"number not on approved list: {n}")
# 7 shape
nb = sum(len(j["bullets"]) for j in d["experience"])
print(f"experience bullets: {nb}; projects: {len(d.get('projects',[]))}")
print("RESULT:", "PASS" if not fail else "FAIL"); [print(" -", f) for f in fail]
sys.exit(1 if fail else 0)