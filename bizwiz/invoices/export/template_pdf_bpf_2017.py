"""Reportlab based invoice PDF generation for BPF page template."""
import logging
import os

from reportlab import platypus
from reportlab.lib import colors
from reportlab.lib import enums
from reportlab.lib import pagesizes, styles, units
from reportlab.pdfgen import canvas

IMAGES_DIRPATH = os.path.abspath(os.path.join(os.path.dirname(__file__), 'img'))

PAGESIZE = pagesizes.A4
PAGE_WIDTH = PAGESIZE[0]
PAGE_HEIGHT = PAGESIZE[1]

BORDER_LEFT = 2.236 * units.cm
BORDER_RIGHT = 1.161 * units.cm
BODY_WIDTH = (PAGE_WIDTH - BORDER_LEFT - BORDER_RIGHT)

FONT_NAME = 'Helvetica'
FONT_SIZE = 11

STYLESHEET = styles.StyleSheet1()
STYLESHEET.add(styles.ParagraphStyle(
    name='Normal',
    fontName=FONT_NAME,
    fontSize=FONT_SIZE,
    leading=FONT_SIZE,
))
STYLESHEET.add(styles.ParagraphStyle(
    name='BodyText',
    parent=STYLESHEET['Normal'],
    spaceBefore=FONT_SIZE,
))
STYLESHEET.add(styles.ParagraphStyle(
    name='Date',
    parent=STYLESHEET['Normal'],
    alignment=enums.TA_RIGHT,
    spaceAfter=4 * FONT_SIZE,
))
STYLESHEET.add(styles.ParagraphStyle(
    name='Subject',
    parent=STYLESHEET['Normal'],
    fontName=FONT_NAME + '-Bold',
    spaceAfter=3 * FONT_SIZE,
))

ITEMS_TABLE_STYLE = platypus.TableStyle([
    ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
    ('ALIGN', (2, 0), (2, -1), 'CENTRE'),
    ('ALIGN', (3, 0), (3, -1), 'RIGHT'),
    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ('FONT', (0, 0), (-1, 0), FONT_NAME + '-Bold', FONT_SIZE),
    ('FONT', (0, 1), (-1, -2), FONT_NAME, FONT_SIZE),
    ('FONT', (0, -1), (-1, -1), FONT_NAME + '-Bold', FONT_SIZE),
    ('LINEBELOW', (0, 0), (-1, 0), 0.5, colors.black),
    ('LINEABOVE', (-1, -1), (-1, -1), 0.5, colors.black),
])

ITEMS_TABLE_COL_WIDTHS = (
    0.5 * BODY_WIDTH,
    0.2 * BODY_WIDTH,
    0.1 * BODY_WIDTH,
    0.2 * BODY_WIDTH
)

_logger = logging.getLogger(__name__)


class BpfInvoiceDocTemplate(platypus.BaseDocTemplate):
    def __init__(self, filename, text_blocks, **kwargs):
        self.text_blocks = text_blocks

        pagetemplates = [
            BpfFirstPageTemplate(id='bpf.first', autoNextPageTemplate='bpf.next'),
            BpfPageTemplate(id='bpf.next')
        ]

        super().__init__(
            filename,
            pagesize=PAGESIZE,
            pageTemplates=pagetemplates,
            **kwargs
        )

    @property
    def flowables(self):
        normalstyle = STYLESHEET['Normal']
        bodystyle = STYLESHEET['BodyText']

        # turn long article names into paragraphs to allow linebreaks in cell:
        article_data = [[
                            platypus.Paragraph(row[0], normalstyle) if row[0] else None,
                            row[1],
                            row[2],
                            row[3]
                        ] for row in self.text_blocks.iter_article_rows()]

        return [
            platypus.Paragraph(self.text_blocks.clause_date, STYLESHEET['Date']),
            platypus.Paragraph(self.text_blocks.clause_subject, STYLESHEET['Subject']),
            platypus.Paragraph(self.text_blocks.clause_salutation, bodystyle),
            platypus.Paragraph(self.text_blocks.clause_body_top, bodystyle),
            platypus.Table(
                article_data,
                style=ITEMS_TABLE_STYLE,
                colWidths=ITEMS_TABLE_COL_WIDTHS,
                spaceBefore=FONT_SIZE,
                spaceAfter=FONT_SIZE,
                repeatRows=1,
            ),
            platypus.Paragraph(self.text_blocks.clause_body_bottom, bodystyle),
            platypus.Paragraph(self.text_blocks.clause_taxinfo, bodystyle),
            platypus.Paragraph(self.text_blocks.clause_closing, bodystyle),
            platypus.Paragraph(self.text_blocks.clause_signature, bodystyle),
        ]


class BpfPageTemplate(platypus.PageTemplate):
    BORDER_TOP = 5.5 * units.cm
    BORDER_BOTTOM = 3.7 * units.cm
    PAGE_BG_IMAGE_PATH = os.path.join(IMAGES_DIRPATH, 'page-bg.jpg')

    def __init__(self, **kwargs):
        super().__init__(
            frames=[
                platypus.Frame(
                    BORDER_LEFT,
                    self.BORDER_BOTTOM,
                    PAGE_WIDTH - BORDER_LEFT - BORDER_RIGHT,
                    PAGE_HEIGHT - self.BORDER_BOTTOM - self.BORDER_TOP,
                    topPadding=0,
                    bottomPadding=0,
                    leftPadding=0,
                    rightPadding=0,
                )
            ],
            **kwargs
        )

    def beforeDrawPage(self, canv: canvas.Canvas, doc):
        canv.drawImage(self.PAGE_BG_IMAGE_PATH,
                       0, 0, width=PAGE_WIDTH, height=PAGE_HEIGHT,
                       preserveAspectRatio=True, anchor='s')


class BpfFirstPageTemplate(BpfPageTemplate):
    BORDER_TOP = 9.3 * units.cm
    PAGE_BG_IMAGE_PATH = os.path.join(IMAGES_DIRPATH, 'page-bg-first.jpg')

    def beforeDrawPage(self, canv: canvas.Canvas, doc):
        super().beforeDrawPage(canv, doc)

        style = STYLESHEET['Normal']
        leading = style.leading
        canv.setFont(style.fontName, style.fontSize)

        customer = doc.text_blocks.invoice.invoiced_customer

        ypos = PAGE_HEIGHT - 5.9 * units.cm

        for line in doc.text_blocks.iter_address_field_lines():
            canv.drawString(BORDER_LEFT, ypos, line)
            ypos -= leading
