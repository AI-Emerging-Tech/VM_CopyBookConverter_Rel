# converters/ebcdic/reader.py
from pathlib import Path

def read_records(file_path: Path, fmt: dict):
    t = fmt.get("type")


    if t == "RDW":
        yield from _read_rdw(file_path)
    elif t == "FIXED":
        yield from _read_fixed(file_path, fmt["record_length"])
    else:
        yield from _read_text(file_path)

def _read_fixed(file_path: Path, L: int):
    with open(file_path, 'rb') as f:
        while True:
            chunk = f.read(L)
            if not chunk:
                break
            if len(chunk) < L:
                break
            yield chunk

def _read_rdw(file_path: Path):
    with open(file_path, 'rb') as f:
        while True:
            rdw = f.read(4)
            if not rdw or len(rdw) < 4:
                break
            rec_len = int.from_bytes(rdw[0:2], byteorder='big')
            if rec_len <= 4:
                break
            data = f.read(rec_len - 4)
            if len(data) < rec_len - 4:
                break
            yield data

def _read_text(file_path: Path):
    with open(file_path, 'rb') as f:
        for line in f:
            yield line.rstrip(b"\r\n")