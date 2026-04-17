# converters/utils/xsd_validator.py
from lxml import etree
import re

XSD_NS = "http://www.w3.org/2001/XMLSchema"
DEFAULT_NS = "http://example.com/records"

def extract_xsd(text: str) -> str:
    # Remove markdown fences
    text = re.sub(r"```xml", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)

    start = text.find("<")
    end = text.rfind(">")

    if start == -1 or end == -1:
        raise ValueError("No XML content found in LLM output")

    return text[start:end + 1]


def normalize_prefixes(xsd: str) -> str:
    """
    - Ensure xs namespace exists if xs: is used
    - Normalize mixed xs:/xsd: usage
    """
    if "xs:" in xsd and "xmlns:xs=" not in xsd:
        xsd = xsd.replace(
            "<xsd:schema",
            f'<xsd:schema xmlns:xs="{XSD_NS}"',
            1
        )
    return xsd

def normalize_target_namespace(xsd: str) -> str:
    if "tns:" not in xsd:
        return xsd

    if "xmlns:tns=" in xsd:
        return xsd

    return xsd.replace(
        "<xsd:schema",
        f'<xsd:schema xmlns:tns="{DEFAULT_NS}" targetNamespace="{DEFAULT_NS}"',
        1
    )

def validate_xsd(xsd_text: str) -> str:
    """
    Validate XSD syntax without modifying structure.
    Only ensures it is well-formed XML.
    """
    try:
        parser = etree.XMLParser(remove_blank_text=True)
        root = etree.XML(xsd_text.encode("utf-8"), parser)
        return etree.tostring(root, pretty_print=True, encoding="unicode")

    except etree.XMLSyntaxError as e:
        print("\nXSD SYNTAX ERROR:\n", e)
        raise

