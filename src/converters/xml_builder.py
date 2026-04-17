# xml_builder.py - Helper functions to build XML from dictionaries,
# ensuring valid XML element names and sanitized text

from lxml import etree
from converters.ebcdic.utils import sanitize_xml_text
import re


def xml_safe(name):
    name = re.sub(r'[^A-Za-z0-9_-]', '_', name)
    if not name:
        return "_"
    if not re.match(r'[A-Za-z_]', name[0]):
        name = "_" + name
    return name


def singularize(name: str) -> str:
    """
    Convert plural field names to singular for OCCURS items.
    Example:
        PROPERTY-DETAILS -> PROPERTY-DETAIL
    """
    if name.endswith("IES"):
        return name[:-3] + "Y"
    if name.endswith("S"):
        return name[:-1]
    return name + "_ITEM"


def dict_to_xml(parent, data):
    # -------------------------
    # Dictionary → normal nodes
    # -------------------------
    if isinstance(data, dict):
        for k, v in data.items():
            child = etree.SubElement(parent, xml_safe(k))
            dict_to_xml(child, v)

    # -------------------------
    # List → OCCURS handling
    # -------------------------
    elif isinstance(data, list):
        item_tag = xml_safe(singularize(parent.tag))

        for item in data:
            child = etree.SubElement(parent, item_tag)
            dict_to_xml(child, item)

    # -------------------------
    # Leaf value
    # -------------------------
    else:
        if data is None:
            parent.text = ""
        else:
            if isinstance(data, bytes):
                text = data.decode("cp037", errors="ignore")
            else:
                text = data if isinstance(data, str) else str(data)

            parent.text = sanitize_xml_text(text)