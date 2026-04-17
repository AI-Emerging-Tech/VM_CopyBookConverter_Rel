# copybook_to_xsd_v6_9_2_ollama.py — FINAL WITH OLLAMA

import re
import os
import requests

ENABLE_LLM = True

OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "qwen3.5:35b"


# ================= LLM =================

def call_ollama(prompt: str) -> str:
    try:
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0}
        }

        resp = requests.post(OLLAMA_URL, json=payload, timeout=180)

        if resp.status_code != 200:
            print("[WARN] Ollama HTTP:", resp.status_code)
            return ""

        return resp.json().get("response", "").strip()

    except Exception as e:
        print("[WARN] Ollama failed:", e)
        return ""


def call_llm_cleaning(copybook: str) -> str:
    prompt = f"""
You are an expert in COBOL copybooks.

Clean and normalize the following COBOL copybook:
- Remove noise (user IDs, dates, sequence numbers)
- Preserve ALL field names EXACTLY
- Preserve levels (01, 05, 10, etc.)
- Do NOT invent or remove fields

Return ONLY cleaned copybook text.

COPYBOOK:
{copybook}
"""
    return call_ollama(prompt)


def call_llm_xsd(copybook: str) -> str:
    prompt = f"""
You are an expert in COBOL and XML Schema.

Convert the following COBOL copybook into XSD:
- Preserve structure exactly
- OCCURS → maxOccurs
- REDEFINES → xsd:choice
- PIC mapping to correct types

Return ONLY valid XSD.

COPYBOOK:
{copybook}
"""
    return call_ollama(prompt)


# ================= CLEANING =================

LEVEL_REGEX = r'(^|\s)(0[1-9]|[1-4][0-9]|66|77|88)\s+'


def clean_copybook_text(text):
    lines = text.splitlines()
    cleaned = []

    for line in lines:
        if re.search(LEVEL_REGEX, line):
            cleaned.append(line.strip())
        elif line.strip().startswith("*>") or not line.strip():
            cleaned.append(line)
        else:
            cleaned.append(f"*> [INVALID] {line}")

    return "\n".join(cleaned)


# ================= PARSER =================

def parse_copybook(text):
    lines = text.splitlines()
    root = {"level": 0, "children": []}
    stack = []
    last_node = None
    filler_count = 0

    for line in lines:
        line = line.strip()

        if not line or line.startswith("*>"):
            continue

        if line.startswith("88") and last_node:
            enum_name = re.match(r"88\s+([A-Za-z0-9\-]+)", line).group(1)
            values = re.findall(r"'([^']+)'", line)

            for v in values:
                last_node.setdefault("enum", []).append({"name": enum_name, "value": v})
            continue

        m = re.match(r"^(\d+)\s+([A-Za-z0-9\-]+)", line)
        if not m:
            continue

        level = int(m.group(1))
        name = m.group(2)

        if name.upper() == "FILLER":
            filler_count += 1
            name = f"FILLER_{filler_count}"

        node = {"name": name, "level": level, "children": []}

        if "REDEFINES" in line:
            redef = re.search(r"REDEFINES\s+([A-Za-z0-9\-]+)", line)
            if redef:
                node["redefines"] = redef.group(1)

        pic = re.search(r"PIC\s+([A-Za-z0-9\(\)V\.\-]+)", line)
        if pic:
            node["pic"] = pic.group(1)

        occ = re.search(r"OCCURS\s+(\d+)", line)
        if occ:
            node["occurs"] = int(occ.group(1))

        while stack and stack[-1]["level"] >= level:
            stack.pop()

        parent = stack[-1] if stack else root
        parent["children"].append(node)

        stack.append(node)
        last_node = node

    return root["children"]


# ================= BUILD =================

def build_xsd(nodes):

    def build(n):
        attrs = f'name="{n["name"]}"'

        if "occurs" in n:
            attrs += f' minOccurs="0" maxOccurs="{n["occurs"]}"'

        if n.get("children"):
            inner = "\n".join(build(c) for c in n["children"])
            return f"<xsd:element {attrs}><xsd:complexType><xsd:sequence>{inner}</xsd:sequence></xsd:complexType></xsd:element>"

        return f'<xsd:element {attrs} type="xsd:string"/>'

    body = "\n".join(build(n) for n in nodes)

    return f'<xsd:schema xmlns:xsd="http://www.w3.org/2001/XMLSchema">{body}</xsd:schema>'


# ================= CLI =================

if __name__ == "__main__":
    import argparse
    from xml.dom import minidom

    parser = argparse.ArgumentParser()
    parser.add_argument("--inputcopybook", required=True)
    parser.add_argument("--outputxsd", required=True)
    parser.add_argument("--no-llm", action="store_true")
    parser.add_argument("--no-pretty", action="store_true")

    args = parser.parse_args()

    if args.no_llm:
        ENABLE_LLM = False

    with open(args.inputcopybook) as f:
        raw = f.read()

    print("[INFO] Cleaning...")
    cleaned = clean_copybook_text(raw)

    if ENABLE_LLM and "*> [INVALID]" in cleaned:
        print("[INFO] LLM cleaning fallback...")
        improved = call_llm_cleaning(raw)
        if improved:
            cleaned = improved

    print("[INFO] Parsing...")
    nodes = parse_copybook(cleaned)

    print("[INFO] Building XSD...")
    xsd = build_xsd(nodes)

    if ENABLE_LLM and len(xsd) < 200:
        print("[INFO] LLM XSD fallback...")
        xsd = call_llm_xsd(cleaned)

    if not args.no_pretty:
        try:
            xsd = minidom.parseString(xsd).toprettyxml(indent="  ")
        except:
            pass

    with open(args.outputxsd, "w") as f:
        f.write(xsd)

    print("[DONE] XSD generated:", args.outputxsd)