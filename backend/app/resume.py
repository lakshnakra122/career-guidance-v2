"""Resume generation in the university format.

Format (from the user's university resume template):
- Centered UPPERCASE bold name, italic tagline, centered contact lines.
- Bold section headings, each followed by a horizontal rule.
- Education / Projects: bold title with right-aligned dates, italic
  institution/context line, bullets for projects.
- Technical Skills: bold category labels.
Downloads: LaTeX (.tex), PDF (reportlab), DOCX (python-docx).
"""
import io
import re

# ---------------------------------------------------------------------------
# shared helpers
# ---------------------------------------------------------------------------

def _clean(s) -> str:
    return (s or "").strip()


def _split_bold(text: str):
    """Split **bold** markers into (text, is_bold) segments."""
    parts = re.split(r"(\*\*.+?\*\*)", text or "")
    out = []
    for p in parts:
        if not p:
            continue
        if p.startswith("**") and p.endswith("**"):
            out.append((p[2:-2], True))
        else:
            out.append((p, False))
    return out


# ---------------------------------------------------------------------------
# LaTeX
# ---------------------------------------------------------------------------

_TEX_ESCAPES = {
    "\\": r"\textbackslash{}", "&": r"\&", "%": r"\%", "$": r"\$",
    "#": r"\#", "_": r"\_", "{": r"\{", "}": r"\}",
    "~": r"\textasciitilde{}", "^": r"\textasciicircum{}",
}


def _tex(text: str) -> str:
    return "".join(_TEX_ESCAPES.get(ch, ch) for ch in (text or ""))


def _tex_rich(text: str) -> str:
    """Escape text but convert **bold** to \\textbf{}."""
    out = []
    for seg, bold in _split_bold(text or ""):
        out.append(r"\textbf{" + _tex(seg) + "}" if bold else _tex(seg))
    return "".join(out)


def build_tex(d: dict) -> str:
    name = _tex(_clean(d.get("name")).upper() or "YOUR NAME")
    lines = []
    lines.append(r"\documentclass[11pt,a4paper]{article}")
    lines.append(r"\usepackage[margin=0.75in]{geometry}")
    lines.append(r"\usepackage[hidelinks]{hyperref}")
    lines.append(r"\usepackage{enumitem}")
    lines.append(r"\pagestyle{empty}")
    lines.append(r"\setlength{\parindent}{0pt}")
    lines.append(r"\begin{document}")
    lines.append(r"\begin{center}")
    lines.append(r"{\Large \textbf{" + name + r"}}\\[2pt]")
    if _clean(d.get("tagline")):
        lines.append(r"{\textit{" + _tex(d["tagline"]) + r"}}\\[6pt]")
    contact1 = []
    if _clean(d.get("email")):
        contact1.append(r"\href{mailto:" + _tex(d["email"]) + "}{" + _tex(d["email"]) + "}")
    if _clean(d.get("phone")):
        contact1.append(r"\href{tel:" + _tex(d["phone"].replace(" ", "")) + "}{" + _tex(d["phone"]) + "}")
    if _clean(d.get("location")):
        contact1.append(_tex(d["location"]))
    contact2 = []
    if _clean(d.get("linkedin")):
        url = d["linkedin"] if d["linkedin"].startswith("http") else "https://" + d["linkedin"]
        contact2.append(r"\href{" + _tex(url) + "}{" + _tex(d["linkedin"]) + "}")
    if _clean(d.get("github")):
        url = d["github"] if d["github"].startswith("http") else "https://" + d["github"]
        contact2.append(r"\href{" + _tex(url) + "}{" + _tex(d["github"]) + "}")
    if contact1:
        lines.append(" --- ".join(contact1) + r"\\")
    if contact2:
        lines.append(" --- ".join(contact2))
    lines.append(r"\end{center}")

    def section(title: str):
        lines.append("")
        lines.append(r"\section*{" + title + "}")
        lines.append(r"\hrule\vspace{6pt}")

    if _clean(d.get("summary")):
        section("Professional Summary")
        lines.append(_tex_rich(d["summary"]))

    edu = [e for e in d.get("education", []) if _clean(e.get("degree")) or _clean(e.get("institution"))]
    if edu:
        section("Education")
        for i, e in enumerate(edu):
            suffix = r"\\[4pt]" if i < len(edu) - 1 else ""
            lines.append(r"\noindent\textbf{" + _tex(e.get("degree", "")) + r"} \hfill " + _tex(e.get("dates", "")) + r"\\")
            inst = _tex(e.get("institution", ""))
            if _clean(e.get("score")):
                inst += " --- " + _tex(e["score"])
            lines.append(r"\textit{" + inst + "}" + suffix)

    projects = [p for p in d.get("projects", []) if _clean(p.get("title"))]
    if projects:
        section("Projects")
        for p in projects:
            lines.append("")
            lines.append(r"\noindent\textbf{" + _tex(p["title"]) + r"} \hfill " + _tex(p.get("dates", "")) + r"\\")
            if _clean(p.get("context")):
                lines.append(r"\textit{" + _tex(p["context"]) + r"}\\")
            if _clean(p.get("tech")):
                lines.append(r"\textit{Tech Stack: " + _tex(p["tech"]) + "}")
            bullets = [b for b in p.get("bullets", []) if _clean(b)]
            if bullets:
                lines.append(r"\begin{itemize}[leftmargin=*,nosep]")
                for b in bullets:
                    lines.append(r"\item " + _tex_rich(b))
                lines.append(r"\end{itemize}")

    skills = [s for s in d.get("skills", []) if _clean(s.get("category")) and _clean(s.get("items"))]
    if skills:
        section("Technical Skills")
        for i, s in enumerate(skills):
            suffix = r"\\[2pt]" if i < len(skills) - 1 else ""
            lines.append(r"\noindent\textbf{" + _tex(s["category"]) + ":} " + _tex(s["items"]) + suffix)

    certs = [c for c in d.get("certifications", []) if _clean(c)]
    if certs:
        section("Certifications \\& Training")
        lines.append(r"\begin{itemize}[leftmargin=*,nosep]")
        for c in certs:
            lines.append(r"\item " + _tex_rich(c))
        lines.append(r"\end{itemize}")

    lines.append("")
    lines.append(r"\end{document}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# PDF (reportlab)
# ---------------------------------------------------------------------------

def build_pdf(d: dict) -> bytes:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import (HRFlowable, Paragraph, SimpleDocTemplate,
                                    Spacer, Table, TableStyle)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=0.75 * inch, rightMargin=0.75 * inch,
                            topMargin=0.7 * inch, bottomMargin=0.7 * inch,
                            title=f"Resume - {_clean(d.get('name'))}", author=_clean(d.get("name")))

    def esc(t: str) -> str:
        return (t or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

    def rich(t: str) -> str:
        return "".join(f"<b>{esc(seg)}</b>" if bold else esc(seg) for seg, bold in _split_bold(t or ""))

    name_style = ParagraphStyle("name", fontName="Helvetica-Bold", fontSize=16, alignment=1, spaceAfter=2)
    tag_style = ParagraphStyle("tag", fontName="Helvetica-Oblique", fontSize=10.5, alignment=1, spaceAfter=6)
    center = ParagraphStyle("center", fontName="Helvetica", fontSize=10, alignment=1, leading=14)
    h2 = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=12, spaceBefore=12, spaceAfter=4)
    body = ParagraphStyle("body", fontName="Helvetica", fontSize=10.5, leading=14.5)
    ital = ParagraphStyle("ital", fontName="Helvetica-Oblique", fontSize=10.5, leading=14)
    bullet = ParagraphStyle("bullet", parent=body, leftIndent=14, bulletIndent=4, spaceAfter=2)
    right = ParagraphStyle("right", fontName="Helvetica", fontSize=10.5, alignment=2)

    story = [Paragraph(esc(_clean(d.get("name")).upper() or "YOUR NAME"), name_style)]
    if _clean(d.get("tagline")):
        story.append(Paragraph(esc(d["tagline"]), tag_style))
    c1 = " &nbsp;---&nbsp; ".join(esc(x) for x in [d.get("email"), d.get("phone"), d.get("location")] if _clean(x))
    c2 = " &nbsp;---&nbsp; ".join(esc(x) for x in [d.get("linkedin"), d.get("github")] if _clean(x))
    if c1:
        story.append(Paragraph(c1, center))
    if c2:
        story.append(Paragraph(c2, center))

    def section(title):
        story.append(Paragraph(title, h2))
        story.append(HRFlowable(width="100%", thickness=0.8, spaceAfter=6))

    def title_dates(left_html, dates):
        t = Table([[Paragraph(f"<b>{left_html}</b>", body), Paragraph(esc(dates or ""), right)]],
                  colWidths=[5.1 * inch, 1.9 * inch])
        t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                               ("LEFTPADDING", (0, 0), (-1, -1), 0),
                               ("RIGHTPADDING", (0, 0), (-1, -1), 0)]))
        story.append(t)

    if _clean(d.get("summary")):
        section("Professional Summary")
        story.append(Paragraph(rich(d["summary"]), body))

    edu = [e for e in d.get("education", []) if _clean(e.get("degree")) or _clean(e.get("institution"))]
    if edu:
        section("Education")
        for e in edu:
            title_dates(esc(e.get("degree", "")), e.get("dates", ""))
            inst = esc(e.get("institution", ""))
            if _clean(e.get("score")):
                inst += " --- " + esc(e["score"])
            story.append(Paragraph(f"<i>{inst}</i>", ital))
            story.append(Spacer(1, 4))

    projects = [p for p in d.get("projects", []) if _clean(p.get("title"))]
    if projects:
        section("Projects")
        for p in projects:
            title_dates(esc(p["title"]), p.get("dates", ""))
            if _clean(p.get("context")):
                story.append(Paragraph(f"<i>{esc(p['context'])}</i>", ital))
            if _clean(p.get("tech")):
                story.append(Paragraph(f"<i>Tech Stack: {esc(p['tech'])}</i>", ital))
            for b in [b for b in p.get("bullets", []) if _clean(b)]:
                story.append(Paragraph(rich(b), bullet, bulletText="•"))
            story.append(Spacer(1, 4))

    skills = [s for s in d.get("skills", []) if _clean(s.get("category")) and _clean(s.get("items"))]
    if skills:
        section("Technical Skills")
        for s in skills:
            story.append(Paragraph(f"<b>{esc(s['category'])}:</b> {esc(s['items'])}", body))

    certs = [c for c in d.get("certifications", []) if _clean(c)]
    if certs:
        section("Certifications &amp; Training")
        for c in certs:
            story.append(Paragraph(rich(c), bullet, bulletText="•"))

    doc.build(story)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# DOCX (python-docx)
# ---------------------------------------------------------------------------

def build_docx(d: dict) -> bytes:
    from docx import Document
    from docx.enum.text import WD_ALIGN_PARAGRAPH
    from docx.oxml import OxmlElement
    from docx.oxml.ns import qn
    from docx.shared import Inches, Pt

    doc = Document()
    for sec in doc.sections:
        sec.left_margin = sec.right_margin = Inches(0.75)
        sec.top_margin = Inches(0.7)
        sec.bottom_margin = Inches(0.7)

    def add_runs(par, text, size=10.5, italic=False):
        for seg, bold in _split_bold(text or ""):
            r = par.add_run(seg)
            r.bold = bold
            r.italic = italic
            r.font.size = Pt(size)
        return par

    def ruled_heading(text):
        par = doc.add_paragraph()
        par.paragraph_format.space_before = Pt(12)
        par.paragraph_format.space_after = Pt(4)
        r = par.add_run(text)
        r.bold = True
        r.font.size = Pt(12)
        pPr = par._p.get_or_add_pPr()
        borders = OxmlElement("w:pBdr")
        bottom = OxmlElement("w:bottom")
        bottom.set(qn("w:val"), "single")
        bottom.set(qn("w:sz"), "8")
        bottom.set(qn("w:space"), "4")
        bottom.set(qn("w:color"), "000000")
        borders.append(bottom)
        pPr.append(borders)
        return par

    def title_dates(left, dates):
        table = doc.add_table(rows=1, cols=2)
        table.autofit = True
        c0, c1 = table.rows[0].cells
        c0.width, c1.width = Inches(5.1), Inches(1.9)
        p0 = c0.paragraphs[0]
        r0 = p0.add_run(left)
        r0.bold = True
        r0.font.size = Pt(10.5)
        p1 = c1.paragraphs[0]
        p1.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        r1 = p1.add_run(dates or "")
        r1.font.size = Pt(10.5)
        for cell in (c0, c1):
            tcPr = cell._tc.get_or_add_tcPr()
            borders = OxmlElement("w:tcBorders")
            for edge in ("top", "left", "bottom", "right"):
                el = OxmlElement(f"w:{edge}")
                el.set(qn("w:val"), "nil")
                borders.append(el)
            tcPr.append(borders)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(_clean(d.get("name")).upper() or "YOUR NAME")
    r.bold = True
    r.font.size = Pt(16)

    if _clean(d.get("tagline")):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        r = p.add_run(d["tagline"])
        r.italic = True
        r.font.size = Pt(10.5)

    for line in (" --- ".join(x for x in [d.get("email"), d.get("phone"), d.get("location")] if _clean(x)),
                 " --- ".join(x for x in [d.get("linkedin"), d.get("github")] if _clean(x))):
        if line:
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(line)
            r.font.size = Pt(10)

    if _clean(d.get("summary")):
        ruled_heading("Professional Summary")
        add_runs(doc.add_paragraph(), d["summary"])

    edu = [e for e in d.get("education", []) if _clean(e.get("degree")) or _clean(e.get("institution"))]
    if edu:
        ruled_heading("Education")
        for e in edu:
            title_dates(e.get("degree", ""), e.get("dates", ""))
            inst = e.get("institution", "")
            if _clean(e.get("score")):
                inst += " --- " + e["score"]
            par = doc.add_paragraph()
            add_runs(par, inst, italic=True)

    projects = [p for p in d.get("projects", []) if _clean(p.get("title"))]
    if projects:
        ruled_heading("Projects")
        for proj in projects:
            title_dates(proj["title"], proj.get("dates", ""))
            if _clean(proj.get("context")):
                par = doc.add_paragraph()
                add_runs(par, proj["context"], italic=True)
            if _clean(proj.get("tech")):
                par = doc.add_paragraph()
                add_runs(par, "Tech Stack: " + proj["tech"], italic=True)
            for b in [b for b in proj.get("bullets", []) if _clean(b)]:
                par = doc.add_paragraph(style="List Bullet")
                add_runs(par, b)

    skills = [s for s in d.get("skills", []) if _clean(s.get("category")) and _clean(s.get("items"))]
    if skills:
        ruled_heading("Technical Skills")
        for s in skills:
            par = doc.add_paragraph()
            r = par.add_run(s["category"] + ": ")
            r.bold = True
            r.font.size = Pt(10.5)
            r2 = par.add_run(s["items"])
            r2.font.size = Pt(10.5)

    certs = [c for c in d.get("certifications", []) if _clean(c)]
    if certs:
        ruled_heading("Certifications & Training")
        for c in certs:
            par = doc.add_paragraph(style="List Bullet")
            add_runs(par, c)

    buf = io.BytesIO()
    doc.save(buf)
    return buf.getvalue()
