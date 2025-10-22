"""Public API for the CopySvgTranslate package."""

from CopySvgTranslate.extraction import extract
from CopySvgTranslate.injection import generate_unique_id, inject, start_injects
from CopySvgTranslate.text_utils import normalize_text
from CopySvgTranslate.workflows import svg_extract_and_inject, svg_extract_and_injects

__all__ = [
    "extract",
    "generate_unique_id",
    "inject",
    "normalize_text",
    "start_injects",
    "svg_extract_and_inject",
    "svg_extract_and_injects",
]
