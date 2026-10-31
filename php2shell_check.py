!/usr/bin/env python3
"""
PHP2SHELL - Detección responsable (No weaponized)
Fingerprint de versión y veredicto de exposición para CVE-2026-109618 y CVE-2026-109619.
"""
import re
import sys
import urllib.request
import argparse

FIXED = {
    (8,5): (8,5,12),
    (8,4): (8,4,27),
    (8,3): (8,3,36),
    (8,2): (8,2,35),
}

def parse_version(s):
    m = re.search(r'PHP[\s/](\d+)\.(\d+)\.(\d+)', s, re.I)
    if not m:
        return None
    return tuple(map(int, m.groups()))

def verdict(ver):
    if not ver:
        return "desconocido"
    major_minor = (ver[0], ver[1])
    if major_minor in FIXED:
        if ver >= FIXED[major_minor]:
            return "parcheado"
        else:
            return "vulnerable"
    if ver[0] < 8 or (ver[0]==8 and ver[1]<=1):
        return "vulnerable (EOL, sin parches)"
    if ver >= (8,5,12):
        return "parcheado"
    return "vulnerable"

def check_url(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "PHP2SHELL-Checker/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            headers = str(r.headers)
            body = r.read(2048).decode(errors="ignore")
            combined = headers + body
            ver = parse_version(combined)
            if not ver:
                # heurística PHP presente
                if "PHPSESSID" in combined or "X-Powered-By: PHP" in combined:
                    return {"url": url, "version": None, "verdict": "desconocido (PHP present, version hidden)"}
            return {"url": url, "version": ver, "verdict": verdict(ver)}
    except Exception as e:
        return {"url": url, "version": None, "verdict": f"error: {e}"}

def main():
    ap = argparse.ArgumentParser(description="Análisis de PHP2Shell (solo detección)")
    ap.add_argument("urls", nargs="*")
    ap.add_argument("-i", "--input")
    args = ap.parse_args()
    urls = list(args.urls)
    if args.input:
        with open(args.input) as f:
            urls += [l.strip() for l in f if l.strip()]
    for u in urls:
        res = check_url(u)
        print(f"{res['url']} -> {res['version']} : {res['veredicto']}")

if __name__ == "__main__":
    main()
