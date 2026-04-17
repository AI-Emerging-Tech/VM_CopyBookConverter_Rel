# numeric.py - Encode/decode COBOL numeric types (COMP-3, COMP, DISPLAY)
from decimal import Decimal


# =========================
# COMP-3 (Packed Decimal)
# =========================

def decode_comp3(raw: bytes, digits: int, scale: int) -> str:
    if not raw:
        return f"0.{('0'*scale)}" if scale else "0"

    hexstr = raw.hex().upper()

    # Last nibble = sign
    sign_nibble = hexstr[-1]
    sign = -1 if sign_nibble in ("D", "B") else 1

    # Extract digit part (exclude sign)
    digit_str = hexstr[:-1]

    # Remove leading padding nibble if present
    if len(digit_str) > digits:
        digit_str = digit_str[-digits:]

    # Ensure numeric (strip any non-digit safely)
    clean_digits = []
    for ch in digit_str:
        if ch.isdigit():
            clean_digits.append(ch)
        else:
            # padding nibble like F → treat as 0
            clean_digits.append('0')

    digit_str = ''.join(clean_digits).zfill(digits)

    number = int(digit_str) * sign

    if scale:
        value = Decimal(number) / (Decimal(10) ** scale)
        return f"{value:.{scale}f}"
    else:
        return str(number)


def encode_comp3(value, digits: int, scale: int) -> bytes:
    """
    Encode COBOL COMP-3 packed decimal.
    digits = total digits (excluding sign)
    scale  = decimal places
    """
    if value in ("", None):
        value = 0

    scaled = int(round(float(value) * (10 ** scale)))

    # absolute digits
    digit_str = f"{abs(scaled):0{digits}d}"

    # sign nibble
    sign = "C" if scaled >= 0 else "D"

    packed = digit_str + sign

    # pad left if odd number of nibbles
    if len(packed) % 2 != 0:
        packed = "0" + packed

    return bytes.fromhex(packed)


# =========================
# COMP (Binary)
# =========================

def decode_comp(raw: bytes, scale: int) -> str:
    value = int.from_bytes(raw, byteorder="big", signed=True)

    if scale:
        d = Decimal(value) / (Decimal(10) ** scale)
        return f"{d:.{scale}f}"

    return str(value)


def encode_comp(value, length: int, scale: int = 0) -> bytes:
    """
    Encode COBOL COMP (binary).
    Length is 2/4/8 bytes depending on PIC digits.
    """
    if value in ("", None):
        value = 0

    scaled = int(round(float(value) * (10 ** scale)))

    return int(scaled).to_bytes(length, byteorder="big", signed=True)


# =========================
# DISPLAY Numeric
# =========================

def encode_display_numeric(value, length, scale=0):
    """
    Encode PIC 9(n)V9(m) DISPLAY numeric.
    Example: 550000.00 -> '055000000'
    """
    if value in ("", None):
        return b"\x40" * length  # spaces

    scaled = int(round(float(value) * (10 ** scale)))
    fmt = f"{{:0{length}d}}"
    text = fmt.format(scaled)

    return text.encode("cp037")


# =========================
# TEST
# =========================

if __name__ == "__main__":
    raw = encode_comp3("550000.00", digits=9, scale=2)
    print("HEX:", raw.hex().upper())
    print("DECODE:", decode_comp3(raw, digits=9, scale=2))