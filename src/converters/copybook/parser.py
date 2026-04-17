# converters/copybook/parser.py
import re
from pathlib import Path
from typing import List

from .model import Field
from .pic import parse_pic

LINE_RE = re.compile(
    r'^(\d{2})\s+([A-Z0-9-]+)'
    r'(?:\s+REDEFINES\s+([A-Z0-9-]+))?'
    r'(?:\s+PIC\s+[^.]+)?'
    r'(?:\s+OCCURS\s+(\d+)\s+TIMES)?'
    r'(?:\s+USAGE\s+([A-Z0-9-]+))?'
    r'\.'
)

PIC_EXTRACT = re.compile(r'PIC\s+([^.]+)', re.IGNORECASE)


def normalize_usage(u: str | None) -> str | None:
    if not u:
        return None
    u = u.strip().upper().replace(".", "")
    if u in ("COMPUTATIONAL-3", "COMP-3"):
        return "COMP-3"
    if u in ("COMPUTATIONAL", "COMP"):
        return "COMP"
    if u in ("DISPLAY",):
        return "DISPLAY"
    return u


def parse_copybook(copybook_path: Path) -> Field:
    root = Field(level=0, name="ROOT")
    stack: List[Field] = [root]

    with copybook_path.open() as f:
        for raw in f:
            line = raw.strip().upper()
            line = line.split("*>", 1)[0].rstrip()

            if not line or line.startswith("*"):
                continue

            m = LINE_RE.match(line)
            if not m:
                continue

            level = int(m.group(1))
            name = m.group(2)
            redefines = m.group(3)
            occurs = int(m.group(4)) if m.group(4) else 1

            pic_match = PIC_EXTRACT.search(line)
            pic = pic_match.group(1).strip() if pic_match else None

            # 🔥 FIX: detect usage from PIC (not full line)
            usage = "DISPLAY"
            if pic:
                pic_upper = pic.upper()

                if "COMP-3" in pic_upper or "COMPUTATIONAL-3" in pic_upper:
                    usage = "COMP-3"
                elif "COMP" in pic_upper or "COMPUTATIONAL" in pic_upper:
                    usage = "COMP"

            if pic:
                length, digits, scale = parse_pic(pic)

                pic_upper = pic.upper()

                # Character fields
                if "X(" in pic_upper:
                    usage = "DISPLAY"
                    digits = 0
                    scale = 0

                # DISPLAY numeric (PIC 9...)
                elif usage == "DISPLAY":
                    length = digits

                # COMP-3 (packed)
                elif usage == "COMP-3":
                    length = (digits + 2) // 2

                # COMP (binary)
                elif usage == "COMP":
                    if digits <= 4:
                        length = 2
                    elif digits <= 9:
                        length = 4
                    else:
                        length = 8

            else:
                length, digits, scale = 0, 0, 0

            field = Field(
                level=level,
                name=name,
                pic=pic,
                length=length,
                occurs=occurs,
                redefines=redefines,
                usage=usage,
                digits=digits,
                scale=scale,
            )

            while stack and stack[-1].level >= level:
                stack.pop()

            parent = stack[-1]
            parent.children.append(field)
            stack.append(field)

    _compute_offsets(root, 0)
    return root


def _compute_offsets(field, start):
    field.offset = start

    if field.children:
        pos = start
        for child in field.children:
            _compute_offsets(child, pos)

            if not child.redefines:
                pos += child.total_length()