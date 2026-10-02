from io import BytesIO
import re

from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.section import WD_SECTION
from docx.oxml import OxmlElement
from docx.oxml.ns import qn

from reportlab.lib.pagesizes import letter
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Image
)
from reportlab.lib.styles import (
    getSampleStyleSheet,
    ParagraphStyle
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.units import inch
from xml.sax.saxutils import escape


# =========================================================
# Common helpers
# =========================================================

def _lines(text):
    """Return non-empty document lines."""
    return [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]


def _is_heading(line):
    """
    Detect common legal-document headings:
    1. PARTIES
    1.1 CONFIDENTIALITY
    # PARTIES
    PARTIES
    """
    clean = line.strip().lstrip("# ").strip()

    numbered = re.match(
        r"^\d+(?:\.\d+)*[.)]?\s+.+",
        clean
    )

    markdown = line.strip().startswith("#")

    uppercase_heading = (
        len(clean) >= 5
        and clean.upper() == clean
        and any(char.isalpha() for char in clean)
    )

    return numbered or markdown or uppercase_heading


def _clean_heading(line):
    return line.strip().lstrip("# ").strip()


# =========================================================
# DOCX
# =========================================================

def make_docx(
    text,
    title="LegalEase Draft",
    logo_bytes=None
):
    doc = Document()

    section = doc.sections[0]

    # Professional margins
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.75)
    section.left_margin = Inches(0.85)
    section.right_margin = Inches(0.85)

    # -----------------------------------------------------
    # Default font
    # -----------------------------------------------------

    styles = doc.styles

    normal_style = styles["Normal"]
    normal_style.font.name = "Times New Roman"
    normal_style.font.size = Pt(11)

    # -----------------------------------------------------
    # Logo
    # -----------------------------------------------------

    if logo_bytes:
        try:
            logo_paragraph = doc.add_paragraph()
            logo_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

            logo_run = logo_paragraph.add_run()
            logo_run.add_picture(
                BytesIO(logo_bytes),
                width=Inches(1.35)
            )

        except Exception:
            pass

    # -----------------------------------------------------
    # Title
    # -----------------------------------------------------

    title_paragraph = doc.add_paragraph()
    title_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

    title_run = title_paragraph.add_run(
        title.upper()
    )

    title_run.bold = True
    title_run.font.name = "Times New Roman"
    title_run.font.size = Pt(17)

    title_paragraph.paragraph_format.space_after = Pt(18)

    # -----------------------------------------------------
    # Document content
    # -----------------------------------------------------

    for line in _lines(text):

        if _is_heading(line):

            paragraph = doc.add_paragraph()

            paragraph.paragraph_format.space_before = Pt(10)
            paragraph.paragraph_format.space_after = Pt(5)

            run = paragraph.add_run(
                _clean_heading(line)
            )

            run.bold = True
            run.font.name = "Times New Roman"
            run.font.size = Pt(12)

        else:

            paragraph = doc.add_paragraph()

            paragraph.paragraph_format.space_after = Pt(7)
            paragraph.paragraph_format.line_spacing = 1.15

            run = paragraph.add_run(line)

            run.font.name = "Times New Roman"
            run.font.size = Pt(11)

    # -----------------------------------------------------
    # Signature section
    # -----------------------------------------------------

    signature_keywords = [
        "SIGNATURE",
        "SIGNATURES"
    ]

    has_signature = any(
        keyword in text.upper()
        for keyword in signature_keywords
    )

    if not has_signature:

        doc.add_paragraph()
        signature_heading = doc.add_paragraph()

        run = signature_heading.add_run(
            "SIGNATURES"
        )

        run.bold = True
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)

        doc.add_paragraph()
        doc.add_paragraph(
            "Party 1: ______________________________"
        )
        doc.add_paragraph(
            "Name: _________________________________"
        )
        doc.add_paragraph(
            "Date: __________________________________"
        )

        doc.add_paragraph()

        doc.add_paragraph(
            "Party 2: ______________________________"
        )
        doc.add_paragraph(
            "Name: _________________________________"
        )
        doc.add_paragraph(
            "Date: __________________________________"
        )

    # -----------------------------------------------------
    # Footer
    # -----------------------------------------------------

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER

    footer_run = footer.add_run(
        "LegalEase | AI-assisted draft — "
        "review with a qualified legal professional"
    )

    footer_run.font.name = "Times New Roman"
    footer_run.font.size = Pt(8)

    # -----------------------------------------------------
    # Page number
    # -----------------------------------------------------

    footer.add_run("    |    Page ")

    page_field = OxmlElement("w:fldSimple")
    page_field.set(qn("w:instr"), "PAGE")

    footer._p.append(page_field)

    # -----------------------------------------------------
    # Save
    # -----------------------------------------------------

    output = BytesIO()
    doc.save(output)

    return output.getvalue()


# =========================================================
# PDF
# =========================================================

def make_pdf(
    text,
    title="LegalEase Draft",
    logo_bytes=None
):
    output = BytesIO()

    document = SimpleDocTemplate(
        output,
        pagesize=letter,
        rightMargin=65,
        leftMargin=65,
        topMargin=60,
        bottomMargin=60
    )

    styles = getSampleStyleSheet()

    # -----------------------------------------------------
    # Styles
    # -----------------------------------------------------

    title_style = ParagraphStyle(
        "LegalTitle",
        parent=styles["Title"],
        alignment=TA_CENTER,
        fontName="Times-Bold",
        fontSize=17,
        leading=21,
        spaceAfter=18
    )

    heading_style = ParagraphStyle(
        "LegalHeading",
        parent=styles["Heading2"],
        alignment=TA_LEFT,
        fontName="Times-Bold",
        fontSize=12,
        leading=15,
        spaceBefore=10,
        spaceAfter=5
    )

    body_style = ParagraphStyle(
        "LegalBody",
        parent=styles["BodyText"],
        alignment=TA_LEFT,
        fontName="Times-Roman",
        fontSize=10.5,
        leading=15,
        spaceAfter=7
    )

    signature_style = ParagraphStyle(
        "SignatureHeading",
        parent=heading_style,
        spaceBefore=15,
        spaceAfter=8
    )

    # -----------------------------------------------------
    # Story
    # -----------------------------------------------------

    story = []

    # -----------------------------------------------------
    # Logo
    # -----------------------------------------------------

    if logo_bytes:

        try:

            img = Image(
                BytesIO(logo_bytes)
            )

            img.drawHeight = 0.7 * inch
            img.drawWidth = 1.3 * inch

            story.append(img)
            story.append(
                Spacer(1, 8)
            )

        except Exception:
            pass

    # -----------------------------------------------------
    # Title
    # -----------------------------------------------------

    story.append(
        Paragraph(
            escape(title.upper()),
            title_style
        )
    )

    # -----------------------------------------------------
    # Document content
    # -----------------------------------------------------

    for line in _lines(text):

        clean = _clean_heading(line)

        if _is_heading(line):

            story.append(
                Paragraph(
                    escape(clean),
                    heading_style
                )
            )

        else:

            # Preserve simple line breaks
            clean_text = escape(line)

            story.append(
                Paragraph(
                    clean_text,
                    body_style
                )
            )

    # -----------------------------------------------------
    # Signature section
    # -----------------------------------------------------

    has_signature = any(
        keyword in text.upper()
        for keyword in [
            "SIGNATURE",
            "SIGNATURES"
        ]
    )

    if not has_signature:

        story.append(
            Paragraph(
                "SIGNATURES",
                signature_style
            )
        )

        story.append(
            Spacer(1, 10)
        )

        story.append(
            Paragraph(
                "Party 1: ______________________________",
                body_style
            )
        )

        story.append(
            Paragraph(
                "Name: _________________________________",
                body_style
            )
        )

        story.append(
            Paragraph(
                "Date: __________________________________",
                body_style
            )
        )

        story.append(
            Spacer(1, 12)
        )

        story.append(
            Paragraph(
                "Party 2: ______________________________",
                body_style
            )
        )

        story.append(
            Paragraph(
                "Name: _________________________________",
                body_style
            )
        )

        story.append(
            Paragraph(
                "Date: __________________________________",
                body_style
            )
        )

    # -----------------------------------------------------
    # Footer
    # -----------------------------------------------------

    def footer(canvas, doc):

        canvas.saveState()

        width, height = letter

        canvas.setFont(
            "Helvetica",
            8
        )

        canvas.drawCentredString(
            width / 2,
            30,
            "LegalEase | AI-assisted draft — "
            "review with a qualified legal professional"
        )

        canvas.drawRightString(
            width - 45,
            30,
            f"Page {doc.page}"
        )

        canvas.restoreState()

    # -----------------------------------------------------
    # Build PDF
    # -----------------------------------------------------

    document.build(
        story,
        onFirstPage=footer,
        onLaterPages=footer
    )

    return output.getvalue()