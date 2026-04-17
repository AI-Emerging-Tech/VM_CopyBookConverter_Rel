# ebcdic_to_xml.py - Convert EBCDIC data files to XML using a copybook definition
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from converters.ebcdic.reader import read_records
from converters.ebcdic.decoder import decode_record, debug_dump   # ✅ import debug
from converters.copybook.parser import parse_copybook

import argparse
from lxml import etree

from converters.xml_builder import dict_to_xml


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", required=True)
    p.add_argument("--copybook", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--xsd", required=False)
    p.add_argument("--debug", action="store_true")   # ✅ optional debug flag
    args = p.parse_args()

    model = parse_copybook(Path(args.copybook))

    data_dir = Path(args.data_dir)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for dat in data_dir.glob('*'):
        if not dat.is_file():
            continue

        fmt = {"type": "FIXED", "record_length": model.total_length()}

        root = etree.Element("Records")

        for raw in read_records(dat, fmt):

            # 🔥 DEBUG DUMP (before decoding)
            if args.debug:
                print("\n===== DEBUG RECORD DUMP =====")
                debug_dump(raw, model)
                print("===== END DEBUG =====\n")

            # Normal decode
            record_data = decode_record(raw, model)

            rec_elem = etree.SubElement(root, "Record")
            dict_to_xml(rec_elem, record_data)

        tree = etree.ElementTree(root)

        # Optional XSD validation
        if args.xsd:
            try:
                etree.XML(Path(args.xsd).read_bytes())
            except Exception as e:
                raise RuntimeError(f"Invalid XSD file (not well-formed XML): {e}")

        out_xml = out_dir / f"{dat.stem}.xml"
        tree.write(out_xml, pretty_print=True, xml_declaration=True, encoding="utf-8")
        print(f"Generated {out_xml}")


if __name__ == '__main__':
    main()