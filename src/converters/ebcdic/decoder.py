# converters/ebcdic/decoder.py
from typing import Dict
from converters.copybook.model import Field
from converters.ebcdic.numeric import decode_comp3, decode_comp
from decimal import Decimal

def debug_dump(raw_bytes, model, indent=0):
    prefix = " " * indent

    for field in model.children:
        start = field.offset
        end = start + field.length
        raw = raw_bytes[start:end]

        print(f"{prefix}{field.name}")
        print(f"{prefix}  offset={start} length={field.length}")
        print(f"{prefix}  raw(hex)={raw.hex().upper()}")

        if field.usage == "COMP-3":
            try:
                val = decode_comp3(raw, field.digits, field.scale)
            except Exception as e:
                val = f"ERROR: {e}"
        elif field.usage == "COMP":
            val = int.from_bytes(raw, byteorder="big", signed=True)
        else:
            val = raw.decode("cp037", errors="ignore")

        print(f"{prefix}  decoded={val}")
        print()

        if field.children:
            debug_dump(raw_bytes, field, indent + 2)


def decode_record(raw_bytes: bytes, model: Field) -> dict:
    result = {}

    for field in model.children:

        # OCCURS
        if field.occurs > 1:
            result[field.name] = _decode_occurs(raw_bytes, field)
            continue

        # GROUP (CRITICAL FIX: DO NOT SLICE)
        if field.is_group:
            result[field.name] = decode_record(raw_bytes, field)
            continue

        # FIELD
        start = field.offset
        end = start + field.length
        raw = raw_bytes[start:end]

        if field.usage == "COMP-3":
            value = decode_comp3(raw, field.digits, field.scale)

        elif field.usage == "COMP":
            value = decode_comp(raw, field.scale)

        else:
            text = raw.decode("cp037", errors="ignore")

            if field.pic and field.digits > 0:
                digits_only = "".join(ch for ch in text if ch.isdigit())

                if field.scale > 0:
                    if digits_only == "":
                        value = "0." + ("0" * field.scale)
                    else:
                        digits_only = digits_only.zfill(field.digits)
                        whole = digits_only[:-field.scale] or "0"
                        frac = digits_only[-field.scale:]
                        value = f"{int(whole)}.{frac}"
                else:
                    value = digits_only.lstrip("0") or "0"
            else:
                value = text.strip()

        result[field.name] = value

    return result


def _decode_occurs(raw_bytes: bytes, field: Field):
    items = []

    group_len = field.total_length() // field.occurs

    for i in range(field.occurs):
        offset = field.offset + i * group_len

        if field.redefines:
            continue

        if field.is_group:
            sub = {}

            for child in field.children:
                start = offset + (child.offset - field.offset)
                end = start + child.length
                raw = raw_bytes[start:end]

                if child.usage == "COMP-3":
                    value = decode_comp3(raw, child.digits, child.scale)
                elif child.usage == "COMP":
                    value = decode_comp(raw, child.scale)
                else:
                    value = raw.decode("cp037", errors="ignore").strip()

                if isinstance(value, Decimal):
                    sub[child.name] = format(value, 'f')
                else:
                    sub[child.name] = str(value)

            items.append(sub)

        else:
            start = offset
            end = start + field.length
            raw = raw_bytes[start:end]

            if field.usage == "COMP-3":
                value = decode_comp3(raw, field.digits, field.scale)
            elif field.usage == "COMP":
                value = decode_comp(raw, field.scale)
            else:
                value = raw.decode("cp037", errors="ignore").strip()

            items.append(value)

    return items