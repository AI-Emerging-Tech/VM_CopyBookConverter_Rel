from converters.ebcdic.numeric import encode_display_numeric
from converters.ebcdic.numeric import encode_comp3, encode_comp, encode_display_numeric
from converters.ebcdic.utils import encode_ebcdic
from converters.ebcdic.utils import encode_display
import converters.ebcdic.utils as U

from converters.copybook.model import Field

def write_record(data: dict, model: Field) -> bytes:
    buf = bytearray()

    # ROOT has no data → process its children
    for child in model.children:
        child_data = data.get(child.name, {})
        _write_field(buf, child_data, child)

    return bytes(buf)

def _write_field(buf, data, field):

    # GROUP FIELD
    if field.is_group:
        if field.occurs > 1:
            items = data if isinstance(data, list) else []
            for i in range(field.occurs):
                item_data = items[i] if i < len(items) else {}
                for child in field.children:
                    _write_field(buf, item_data, child)
        else:
            group_data = data if isinstance(data, dict) else {}
            for child in field.children:
                _write_field(buf, group_data, child)
        return

    # ELEMENTARY FIELD
    if isinstance(data, dict):
        value = data.get(field.name, "")
    else:
        # IMPORTANT: when data itself is the value (int/float/string)
        value = data

    raw = encode_field(value, field)
    buf.extend(raw)

def encode_field(value, field):
    if field.usage in ("COMP", "COMP-3") and (field.digits == 0 and field.scale == 0):
        return encode_ebcdic(str(value), field.length)
    
    if field.usage == "COMP-3":
        return encode_comp3(value, field.digits, field.scale)

    if field.usage == "COMP":
        return encode_comp(value, field.length, field.scale)

    # DISPLAY numeric with implied decimals
    if field.scale > 0 and field.digits > 0:
        return encode_display_numeric(value, field.length, field.scale)

    # DISPLAY string
    return encode_ebcdic(str(value), field.length)

