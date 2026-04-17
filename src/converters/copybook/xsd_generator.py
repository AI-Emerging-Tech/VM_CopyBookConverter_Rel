# converters/copybook/xsd_generator.py
from lxml import etree
from .model import Field

XS_NS = "http://www.w3.org/2001/XMLSchema"
XS = f"{{{XS_NS}}}"


def generate_xsd(root: Field) -> etree.ElementTree:
    schema = etree.Element(
        XS + "schema",
        nsmap={"xs": XS_NS}
    )

    # Root: Records
    records_elem = etree.SubElement(schema, XS + "element", name="Records")
    records_ct = etree.SubElement(records_elem, XS + "complexType")
    records_seq = etree.SubElement(records_ct, XS + "sequence")

    # Repeating Record
    record_elem = etree.SubElement(
        records_seq,
        XS + "element",
        name="Record",
        minOccurs="0",
        maxOccurs="unbounded"
    )

    record_ct = etree.SubElement(record_elem, XS + "complexType")
    _build_complex_type(root, record_ct)

    return etree.ElementTree(schema)

def _build_complex_type(field: Field, complex_type_elem):
    seq = etree.SubElement(complex_type_elem, XS + "sequence")

    for child in field.children:
        elem = etree.SubElement(
            seq,
            XS + "element",
            name=child.name,
            minOccurs="0",
            maxOccurs=str(child.occurs) if child.occurs > 1 else "1",
        )

        if child.is_group():
            ct = etree.SubElement(elem, XS + "complexType")
            _build_complex_type(child, ct)
        else:
            simple = etree.SubElement(elem, XS + "simpleType")
            restr = etree.SubElement(
                simple,
                XS + "restriction",
                base="xs:string",
            )
            etree.SubElement(
                restr,
                XS + "maxLength",
                value=str(child.length)
            )
