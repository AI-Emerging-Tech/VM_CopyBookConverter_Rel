import re

RE_X = re.compile(r"X\((\d+)\)")
RE_9 = re.compile(r"9\((\d+)\)")
RE_DECIMAL_V99 = re.compile(r"9\((\d+)\)\s*V\s*9\((\d+)\)")   # 9(7)V9(2)
RE_DECIMAL_V_99 = re.compile(r"9\((\d+)\)\s*V\s*(9+)")       # 9(7)V99

def normalize_pic(pic: str) -> str:
    """
    Convert PIC like 99V99 into 9(2)V9(2)
    """
    def repl(match):
        part = match.group(0)
        return f"9({len(part)})"

    # replace sequences of 9s with 9(n)
    pic = re.sub(r'9+', repl, pic)
    return pic


import re

def parse_pic(pic: str):
    pic = pic.upper().strip()

    digits = 0
    scale = 0

    # Remove usage keywords if present
    pic = re.sub(r'\b(COMP-3|COMP|COMPUTATIONAL-3|COMPUTATIONAL)\b', '', pic).strip()

    # ---- Character fields ----
    m = re.search(r'X\((\d+)\)', pic)
    if m:
        length = int(m.group(1))
        return length, 0, 0

    # ---- 9(n)V9(m) ----
    m = re.search(r'9\((\d+)\)\s*V\s*9\((\d+)\)', pic)
    if m:
        int_part = int(m.group(1))
        frac_part = int(m.group(2))
        digits = int_part + frac_part
        scale = frac_part
        length = digits
        return length, digits, scale

    # ---- 9(n)V99 style ----
    m = re.search(r'9\((\d+)\)\s*V(9+)', pic)
    if m:
        int_part = int(m.group(1))
        frac_part = len(m.group(2))
        digits = int_part + frac_part
        scale = frac_part
        length = digits
        return length, digits, scale

    # ---- simple 9(n) ----
    m = re.search(r'9\((\d+)\)', pic)
    if m:
        digits = int(m.group(1))
        length = digits
        return length, digits, 0

    # ---- fallback ----
    total_9 = len(re.findall(r'9', pic))
    length = total_9
    digits = total_9
    return length, digits, scale
