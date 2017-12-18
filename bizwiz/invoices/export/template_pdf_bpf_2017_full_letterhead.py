"""Derived PDF template for preprinted letter heads (all details on all pages)."""
from bizwiz.invoices.export.template_pdf_bpf_2017 import BpfPageTemplate, BpfFirstPageTemplate, \
    BpfInvoiceDocTemplate


class BpfFullLetterheadFirstPageTemplate(BpfFirstPageTemplate):
    PAGE_BG_IMAGE_PATH = None


class BpfFullLetterheadPageTemplate(BpfPageTemplate):
    PAGE_BG_IMAGE_PATH = None
    BORDER_TOP = BpfFullLetterheadFirstPageTemplate.BORDER_TOP


class BpfFullLetterheadDocTemplate(BpfInvoiceDocTemplate):
    PAGE_TEMPLATES = [
        BpfFullLetterheadFirstPageTemplate(id='bpf.first', autoNextPageTemplate='bpf.next'),
        BpfFullLetterheadPageTemplate(id='bpf.next')
    ]
