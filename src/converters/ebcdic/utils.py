# utils.py - Utility functions for EBCDIC encoding/decoding and XML sanitization
import re

def decode_ebcdic(raw: bytes, codepage: str = "cp037") -> str:
    return raw.decode(codepage, errors="ignore").rstrip()

def encode_display(value: str, length: int) -> bytes:
    txt = (value or "").ljust(length)[:length]
    return txt.encode("cp037")

# XML 1.0 valid character range
_XML_INVALID = re.compile(
    r"[^\x09\x0A\x0D\x20-\uD7FF\uE000-\uFFFD]"
)

def sanitize_xml_text(text: str) -> str:
    if not text:
        return ""
    # Remove NULLs explicitly
    text = text.replace("\x00", "")
    # Strip EBCDIC padding
    text = text.strip()
    # Remove invalid XML chars
    return _XML_INVALID.sub("", text)

def encode_ebcdic(text: str, length: int, codepage: str = "cp037") -> bytes:
    """
    Encode a string into EBCDIC bytes padded/truncated to fixed length.
    """
    if text is None:
        text = ""
    text = str(text)

    b = text.encode(codepage, errors="ignore")
    if len(b) > length:
        b = b[:length]

    # pad with EBCDIC spaces (0x40)
    return b.ljust(length, b"\x40")
