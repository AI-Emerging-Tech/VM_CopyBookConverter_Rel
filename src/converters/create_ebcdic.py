from converters.copybook.parser import parse_copybook
from converters.ebcdic.writer import write_record
import yaml
from pathlib import Path

def main():
    root = parse_copybook(Path("HO3-POLICY.cpy"))

    record_model = root.children[0]

    with open("Business_Record.yaml") as f:
        data = yaml.safe_load(f)

    record_model = root.children[0]              # HO3-POLICY-RECORD
    record_data  = data[record_model.name]
    print("MODEL ROOT:", record_model.name)
    print("MODEL CHILDREN:", [c.name for c in record_model.children])
    print("DATA KEYS:", data.keys())

    record = write_record(record_data, record_model)

    expected = root.total_length()
    actual = len(record)

    assert expected == actual, f"Record length mismatch: {expected=} {actual=}"

    out_path = Path("ho3_ebcdic.dat")

    print("WRITER RUN AT:", __import__("datetime").datetime.utcnow())
    out_path.write_bytes(record)
    print("WROTE:", out_path)
    print("SIZE:", len(record))
    print("FIRST 20 BYTES:", record[:20])

    print("EBCDIC file regenerated successfully")

if __name__ == "__main__":
    main()
