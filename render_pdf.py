#!/usr/bin/env python3
"""Render resume.json / letter.json to an ASCII-only PDF (standard fonts, no compression) so it can be
uploaded to Google Drive as text and stay byte-identical. Single column, ATS-friendly.
Personal header data comes from profile.json (or the file named in $PROFILE).
Usage: python3 render_pdf.py resume resume.json out.pdf
       python3 render_pdf.py letter letter.json out.pdf"""
import json, sys, re
from reportlab.lib.pagesizes import letter as LETTER
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Flowable, KeepTogether
from reportlab.lib.units import inch
from reportlab.lib import colors
from xml.sax.saxutils import escape as X
import reportlab.rl_config as rc
rc.invariant = 1
B, R, I = "Helvetica-Bold", "Helvetica", "Helvetica-Oblique"
import os
P = json.load(open(os.environ.get("PROFILE", "profile.json")))
NAME, CONTACT, LINKS, EDU = P["name"], P["contact"], [tuple(x) for x in P["links"]], P["education"]
INK, GRAY, BLUE, SLATE = colors.HexColor("#1A1A1A"), colors.HexColor("#5F6B7A"), colors.HexColor("#1F5BC6"), colors.HexColor("#4A5A70")
def A(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace("–", "-").replace("—", "-").replace(" ", " ").replace("·", "|")
    return X(s.encode("ascii", "ignore").decode())
S = lambda name, **k: ParagraphStyle(name, **k)
BODY, LEAD = 9.5, 13.6
st = {
 "name": S("n", fontName=B, fontSize=17, leading=21, alignment=TA_CENTER, textColor=INK),
 "tag": S("g", fontName=B, fontSize=7.8, leading=11, alignment=TA_CENTER, textColor=SLATE),
 "contact": S("c", fontName=R, fontSize=8.6, leading=11.5, alignment=TA_CENTER, textColor=GRAY),
 "body": S("b", fontName=R, fontSize=BODY, leading=LEAD, textColor=INK),
 "org": S("o", fontName=R, fontSize=BODY, leading=LEAD - 1, textColor=INK),
 "bullet": S("u", fontName=R, fontSize=BODY, leading=LEAD, leftIndent=12, bulletIndent=2.5, spaceAfter=2.2,
             textColor=INK, bulletFontName="Symbol", bulletFontSize=9),
 "letter": S("l", fontName=R, fontSize=10.5, leading=15, spaceAfter=10, textColor=INK),
}
class Heading(Flowable):
    """Section title with a rule under it; kept on the same page as the content that follows."""
    def __init__(s, text, w): s.text, s.width, s.height = text, w, 16; s.keepWithNext = 1
    def draw(s):
        c = s.canv; c.setFillColor(INK); c.setFont(B, 9.8); c.drawString(0, 5, s.text)
        c.setStrokeColor(colors.HexColor("#333333")); c.setLineWidth(0.6); c.line(0, 1, s.width, 1)
def section(t, w):
    return [Spacer(1, 8), Heading(A(t.upper()), w), Spacer(1, 4)]
def head_block(tagline=None):
    links = "  |  ".join(f'<a href="{u}" color="#1F5BC6">{A(t)}</a>' for t, u in LINKS)
    o = [Paragraph(NAME, st["name"])]
    if tagline: o.append(Paragraph(A(tagline.upper()), st["tag"]))
    return o + [Paragraph(A(CONTACT), st["contact"]), Paragraph(links, st["contact"]), Spacer(1, 2)]
def titled(title, dates):
    return Paragraph(f'<font name="{B}" size="10">{A(title)}</font>&nbsp;&nbsp;<font size="8.2" color="#5F6B7A">{A(dates)}</font>',
                     S("t", fontName=R, fontSize=10, leading=13.5, textColor=INK))
def bullets(items):
    return [Paragraph(A(b), st["bullet"], bulletText="•") for b in items]
def resume(d, w):
    o = head_block(d.get("tagline"))
    o += section(d.get("summary_heading", "Professional Summary"), w) + [Paragraph(A(d["summary"]), st["body"])]
    o += section("Education", w)
    for school, dates, line in d.get("education", EDU):
        o += [KeepTogether([Spacer(1, 2), titled(school, dates), Paragraph(A(line), st["org"]), Spacer(1, 2)])]
    o += section("Technical Skills", w)
    o += [Paragraph(f'<font name="{B}">{A(k)}:</font> {A(v)}', S("k", parent=st["body"], spaceAfter=2)) for k, v in d["skills"]]
    o += section("Experience", w)
    for j in d["experience"]:
        top = [Spacer(1, 3), titled(j["title"], j["dates"]), Paragraph(f'{A(j["org"])}, {A(j["place"])}', st["org"]), Spacer(1, 2)]
        bl = bullets(j["bullets"])
        o += [KeepTogether(top + bl[:1])] + bl[1:]
    if d.get("projects"):
        o += section(d.get("projects_heading", "Projects"), w)
        for p in d["projects"]:
            name = f'<a href="{p["url"]}" color="#1F5BC6"><font name="{B}">{A(p["name"])}</font></a>' if p.get("url") else f'<font name="{B}">{A(p["name"])}</font>'
            t = Paragraph(f'{name}<font name="{B}">  |  {A(p["tools"])}</font>', S("pt", fontName=R, fontSize=10, leading=13.5, textColor=INK))
            bl = bullets(p["bullets"])
            o += [KeepTogether([Spacer(1, 3), t, Spacer(1, 1.5)] + bl[:1])] + bl[1:]
    if d.get("certifications"):
        certs = d["certifications"] if isinstance(d["certifications"], list) else [c.strip() for c in d["certifications"].split("|")]
        o += section("Certifications", w) + bullets(certs)
    return o
def letter(d, w):
    o = head_block() + [Spacer(1, 16), Paragraph(A(d["date"]), st["letter"]),
         Paragraph("<br/>".join(A(x) for x in d["recipient"]), st["letter"]), Paragraph(A(d["salutation"]), st["letter"])]
    o += [Paragraph(A(x), st["letter"]) for x in d["paragraphs"]]
    o += [Paragraph(f"Sincerely,<br/>{A(NAME)}", st["letter"])]
    if d.get("enclosure", True) and P.get("enclosure"):
        o += [Paragraph(A(P.get("enclosure", "")),
                        S("e", fontName=I, fontSize=9, leading=12, textColor=GRAY))]
    return o
kind, src, out = sys.argv[1:4]
d = json.load(open(src))
doc = SimpleDocTemplate(out, pagesize=LETTER, leftMargin=0.62*inch, rightMargin=0.62*inch, topMargin=0.55*inch, bottomMargin=0.5*inch,
                        title=f"{NAME} {'Resume' if kind == 'resume' else 'Cover Letter'}", author=NAME, pageCompression=0)
w = LETTER[0] - 1.24*inch
doc.build(resume(d, w) if kind == "resume" else letter(d, w))
raw = open(out, "rb").read()
raw = re.sub(rb"%[\x80-\xff]{4}", b"%ASCI", raw, count=1)  # same-length ASCII marker keeps offsets valid
open(out, "wb").write(raw)
bad = sum(1 for b in raw if b > 126 or (b < 32 and b not in (9, 10, 13)))
print(f"{out}: {len(raw)} bytes, non-ASCII bytes: {bad}")
sys.exit(1 if bad else 0)
