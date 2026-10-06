# resume-pipeline-scripts

Small helper scripts for an automated resume pipeline. A scheduled job downloads these files, writes the resume content as JSON, and runs one command to check and render it.

- `render_pdf.py`: renders `resume.json` or `letter.json` to a single-column, ATS-friendly PDF that uses only standard PDF fonts and no compression, so the file is plain ASCII text. Personal header details are read from `profile.json` (not stored in this repo).
- `check.py`: content checks (keyword coverage, keyword stuffing, banned words and characters, stale or forbidden facts, numbers not on an approved list).
- `build.py`: runs both, then checks page count, page fill, and stranded section headings. Prints `BUILD: PASS <bytes>` or `BUILD: FAIL` with reasons.

Requires Python 3, `reportlab`, and poppler-utils (`pdfinfo`, `pdftotext`, `pdftoppm`).
