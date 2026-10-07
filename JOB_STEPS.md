# Build ONE job (resume + optional cover letter) for Saketh Dontha

You were given: the job file ID, and a working folder ~/rb/jobN. Work only in that folder. Be brief; do not narrate.
Drive IDs: 2_Ready 1K7xcrPB4KmeXaVxUTi3FBJB_GDhs0M4q | 3_Done 1vP_aCD05XxfvYASxXidPZpPwegjMuOJ3

## Steps
1. read_file_content the job. Header lines: Company, Role, Posting URL, Location, Cover letter (yes/no), Notes; then the posting. If it is not a readable job posting, skip to step 6 with NEEDS_SAKETH.
2. Pick the closest base: `data_bi` (data/BI/reporting/analyst/statistics), `ai_ml` (ML/AI/data science/engineering), `supply_chain` (supply chain/logistics/operations/inventory). Read ~/rb/bases/<base>.json (finished, checked resume), ~/rb/facts.txt (all allowed facts) and ~/rb/updates.txt (newer facts; they win over facts.txt). Project names available: see keys of ~/rb/projects.json.
3. Write keywords.txt: the employer's own terms (tools, duties, qualifications), lowercase, one per line, ONLY ones true of Saketh.
4. Write a SHORT edit file resume.json containing only what should change for this posting:
   `{"base": "data_bi", "tagline": "...", "summary": "...", "skills": [...], "bullets": {"0": [...]}, "projects": ["Name", ...]}`
   Always rewrite tagline and summary for the posting. Change skills, a role's bullets (role index 0 UofM, 1 DA, 2 IFB, 3 NIT), or projects only where it clearly improves the match. Leave everything else out; the base fills it in.
   Run: `PROFILE=~/rb/profile.json python3 ~/rb/build.py resume resume.json keywords.txt ~/rb/extra_numbers.txt`
   It must end `BUILD: PASS <bytes>`. On FAIL fix only what it lists and rerun (max 3 tries, then NEEDS_SAKETH). Aim for 90%+ coverage honestly; never add false claims or repeat phrases to raise it.
   DEEP REWRITE: if the first build shows keyword coverage below 90%, or the posting is outside all three bases (for example healthcare, finance, or marketing analytics), add "bullets" for role 0 (UofM) and role 1 (DA) to resume.json: rewrite every bullet of both roles in the employer's own terms, using only facts from facts.txt (role 1 still leads with the division report automation), and adjust skills rows to the employer's vocabulary. Then rebuild. If coverage is still under 90% after that, accept it and list the missing terms in NOTES.
5. `cat resume.pdf`, then create_file: title `Saketh_Dontha_<Company>_<Role>_Resume.pdf` (letters, digits, underscores), parentId 2_Ready, contentMimeType `application/pdf`, disableConversionToGoogleType true, textContent = the exact full file text. Returned fileSize must equal <bytes>; if not, trash_file and retry once, else NEEDS_SAKETH.
   Only if "Cover letter: yes": write letter.json, run `PROFILE=~/rb/profile.json python3 ~/rb/build.py letter letter.json` (must PASS), upload letter.pdf the same way as `Saketh_Dontha_<Company>_<Role>_Cover_Letter.pdf`, verify fileSize.
6. LAST, create the NOTES (title `Saketh_Dontha_<Company>_<Role>_NOTES`, parentId 2_Ready, contentMimeType text/plain):
   ```
   STATUS: READY  (or NEEDS_SAKETH: reason)
   Company / Role / Posting URL
   Keyword coverage: NN% (missing: ...)
   Honest gaps: requirements Saketh lacks
   Files: <file names>
   ```
7. update_file the job to parentId 3_Done with its original title (remove the `CLAIMED ... | ` prefix).
8. Reply with ONE line: `<Company> | <Role> | NN% | READY` (or NEEDS_SAKETH: reason).

## Rules
- Only facts and numbers in facts.txt, updates.txt, and the bases. Never invent a number, tool, title, or date. GPA 3.97; title "Data Intern"; YOLOv11. Never mention OPT, visa, EAD, sponsorship, or citizenship.
- Criminal Case System Analysis: DA's office work; never "sample/practice"; no dataset sizes; no findings.
- Results first: each bullet opens with the outcome; summary opens with his strongest relevant result. Do not copy the posting's sentences; each employer keyword at most twice.
- US spelling; no em or en dashes; never: leveraged, spearheaded, passionate, robust, seamless, utilize, synergy, cutting-edge, delve, meticulous, comprehensive.
- Tagline: 5-7 true items matching the posting, separated by " | ", starting "MS Data Science".
- letter.json: {"date": "<today, e.g. October 5, 2026>", "recipient": ["Hiring Team", "<Company>", "<City, State or Remote>"], "salutation": "Dear Hiring Team,", "paragraphs": ["...", "...", "..."]}. Under 350 words, 3 paragraphs, plain first person. Open with a specific result (never "I am writing to express"); name the employer and something concrete from the posting; one honest sentence on any key requirement he lacks.
