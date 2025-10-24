"""Utilities for extracting translation data from SVG files."""

from pathlib import Path
import logging

from lxml import etree

from ..text_utils import normalize_text, extract_text_from_node

logger = logging.getLogger(__name__)


def extract(svg_file_path, case_insensitive: bool = True):
    """Extract translations from an SVG file and return them as a dictionary."""
    svg_file_path = Path(svg_file_path)

    if not svg_file_path.exists():
        logger.error(f"SVG file not found: {svg_file_path}")
        return None

    logger.debug(f"Extracting translations from {svg_file_path}")

    parser = etree.XMLParser(remove_blank_text=True)
    try:
        tree = etree.parse(str(svg_file_path), parser)
    except (etree.XMLSyntaxError, OSError) as exc:
        logger.error(f"Failed to parse SVG file {svg_file_path}: {exc}")
        return None
    root = tree.getroot()

    switches = root.xpath('//svg:switch', namespaces={'svg': 'http://www.w3.org/2000/svg'})
    logger.debug(f"Found {len(switches)} switch elements")

    translations: dict[str, dict] = {"new": {}}
    processed_switches = 0

    for switch in switches:
        text_elements = switch.xpath('./svg:text', namespaces={'svg': 'http://www.w3.org/2000/svg'})
        if not text_elements:
            continue

        default_texts: list[str] | None = None
        for text_elem in text_elements:
            if text_elem.get('systemLanguage'):
                continue

            default_texts = [
                normalize_text(text, case_insensitive)
                for text in extract_text_from_node(text_elem)
            ]
            break

        if not default_texts:
            continue

        switch_translations: dict[str, list[str]] = {}
        for text_elem in text_elements:
            system_lang = text_elem.get('systemLanguage')
            if not system_lang:
                continue

            switch_translations[system_lang] = [
                normalize_text(text)
                for text in extract_text_from_node(text_elem)
            ]

        if not switch_translations:
            continue

        processed_switches += 1
        for lang, translated_texts in switch_translations.items():
            for index, default_text in enumerate(default_texts):
                if not default_text:
                    continue
                if index >= len(translated_texts):
                    logger.debug(
                        "Missing translation for '%s' in language '%s'", default_text, lang
                    )
                    continue

                key = default_text.lower() if case_insensitive else default_text
                translations["new"].setdefault(key, {})[lang] = translated_texts[index]

    title_translations: dict[str, dict[str, str]] = {}
    for key, mapping in list(translations["new"].items()):
        if not key or len(key) < 4 or not key[-4:].isdigit():
            continue

        year = key[-4:]
        if key == year:
            continue

        if all(value.endswith(year) for value in mapping.values() if value):
            title_key = key[:-4]
            title_translations[title_key] = {
                lang: value[:-4] for lang, value in mapping.items()
            }

    if title_translations:
        translations["title"] = title_translations
    else:
        translations["title"] = {}

    if not translations["new"]:
        translations.pop("new")

    logger.debug(f"Extracted translations for {processed_switches} switches")

    all_languages = set()
    for mapping in translations.get("new", {}).values():
        all_languages.update(lang for lang, text in mapping.items() if text)
    logger.debug(
        "Found translations in %d languages: %s",
        len(all_languages),
        ', '.join(sorted(all_languages)),
    )

    return translations
