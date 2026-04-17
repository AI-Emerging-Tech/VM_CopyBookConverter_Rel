# converters/ebcdic/detector.py
from pathlib import Path
COMMON_FIXED_LENGTHS = [80, 120, 256, 300, 400, 512, 1024]

def _looks_like_rdw(data: bytes) -> bool:
    if len(data) < 8:
        return False
    # RDW: first two bytes = record length (big endian)
    rec_len = int.from_bytes(data[0:2], byteorder='big')
    # bytes 2-3 typically zero
    if data[2:4] != b"\x00\x00":
        return False
    # sanity check
    return 8 <= rec_len <= 32760

def detect_record_format(file_path: Path) -> dict:
    size = file_path.stat().st_size
    with open(file_path, 'rb') as f:
        sample = f.read(8192)

    # 1) RDW (variable-length)
    if _looks_like_rdw(sample):
        return {"type": "RDW"}

    # 2) Fixed-length (try common lengths)
    for L in COMMON_FIXED_LENGTHS:
        if size % L == 0:
            return {"type": "FIXED", "record_length": L}

    # 3) Fallback: line-delimited (text)
    return {"type": "TEXT"}