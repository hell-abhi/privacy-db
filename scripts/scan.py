#!/usr/bin/env python3
"""
Scan a Google Play Store app and extract permission + data safety info.
Usage: python3 scan.py <package_name_or_play_store_url>

Outputs JSON to stdout. Redirect to save:
    python3 scan.py com.whatsapp > ../apps/com.whatsapp.json
"""

import sys
import json
import re
import urllib.request
from datetime import datetime


def fetch_play_store(package_name: str) -> str:
    url = f"https://play.google.com/store/apps/details?id={package_name}&hl=en"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (Linux; Android 10)"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return resp.read().decode("utf-8")


def extract_data_block(html: str):
    pattern = r"AF_initDataCallback\(\{key:\s*'ds:5'.*?data:(.*?), sideChannel:"
    match = re.search(pattern, html, re.DOTALL)
    if not match:
        return None
    return json.loads(match.group(1))


def extract_permissions(parsed) -> list:
    groups = []
    try:
        perm_section = parsed[1][2][74][2][0]
        for group in perm_section:
            if not isinstance(group, list) or not group:
                continue
            name = group[0] if isinstance(group[0], str) else None
            if not name:
                continue
            perms = []
            if len(group) > 2 and isinstance(group[2], list):
                for p in group[2]:
                    if isinstance(p, list) and len(p) > 1 and isinstance(p[1], str):
                        perms.append(p[1])
            groups.append({"group": name, "permissions": perms})

        # Also check [1][2][74][2][1] for "Other" group
        try:
            other_section = parsed[1][2][74][2][1]
            for group in other_section:
                if not isinstance(group, list) or not group:
                    continue
                name = group[0] if isinstance(group[0], str) else None
                if not name:
                    continue
                perms = []
                if len(group) > 2 and isinstance(group[2], list):
                    for p in group[2]:
                        if isinstance(p, list) and len(p) > 1 and isinstance(p[1], str):
                            perms.append(p[1])
                groups.append({"group": name, "permissions": perms})
        except (IndexError, TypeError):
            pass
    except (IndexError, TypeError):
        # Try fallback indices
        try:
            inner = parsed[1][2]
            for idx in range(70, 80):
                try:
                    candidate = inner[idx]
                    section = candidate[2][0]
                    first = section[0]
                    if isinstance(first, list) and isinstance(first[0], str):
                        for g in section:
                            if isinstance(g, list) and g:
                                name = g[0]
                                perms = []
                                if len(g) > 2 and isinstance(g[2], list):
                                    for p in g[2]:
                                        if isinstance(p, list) and len(p) > 1:
                                            perms.append(p[1])
                                groups.append({"group": name, "permissions": perms})
                        break
                except (IndexError, TypeError):
                    continue
        except (IndexError, TypeError):
            pass
    return groups


def extract_data_safety(parsed) -> dict:
    safety = {"shared": None, "collected": None, "encrypted": False, "deletable": False}
    try:
        section = parsed[1][2][136][1]
        for item in section:
            if not isinstance(item, list) or len(item) < 2:
                continue
            title = item[1] if isinstance(item[1], str) else ""
            detail = find_summary(item, title)
            if "share" in title.lower():
                safety["shared"] = detail or title
            elif "collect" in title.lower():
                safety["collected"] = detail or title
            elif "encrypted" in title.lower():
                safety["encrypted"] = True
            elif "delet" in title.lower():
                safety["deletable"] = True
    except (IndexError, TypeError):
        pass
    return safety


def find_summary(section, title):
    strings = find_strings(section)
    filtered = [s for s in strings if s != title and "googleusercontent" not in s and len(s) > 5]
    return filtered[0] if filtered else None


def find_strings(obj, depth=0):
    if depth > 4:
        return []
    results = []
    if isinstance(obj, str) and len(obj) > 5:
        results.append(obj)
    elif isinstance(obj, list):
        for item in obj:
            results.extend(find_strings(item, depth + 1))
    return results


def extract_metadata(parsed, package_name):
    meta = {"name": package_name, "category": None, "rating": None, "downloads": None}
    try:
        meta["name"] = parsed[1][2][0][0]
    except (IndexError, TypeError):
        pass
    try:
        meta["category"] = parsed[1][2][79][0][0][0]
    except (IndexError, TypeError):
        pass
    try:
        meta["rating"] = round(parsed[1][2][51][0][1], 2)
    except (IndexError, TypeError):
        pass
    try:
        meta["downloads"] = parsed[1][2][13][1]
    except (IndexError, TypeError):
        pass
    return meta


def extract_package_name(input_str: str) -> str:
    if "play.google.com" in input_str:
        match = re.search(r"[?&]id=([^&]+)", input_str)
        if match:
            return match.group(1)
    return input_str.strip()


def scan(package_name: str) -> dict:
    html = fetch_play_store(package_name)
    parsed = extract_data_block(html)
    if parsed is None:
        raise Exception("Could not parse Play Store data")

    meta = extract_metadata(parsed, package_name)
    permissions = extract_permissions(parsed)
    data_safety = extract_data_safety(parsed)

    total_perms = sum(len(g["permissions"]) for g in permissions)

    return {
        "package_name": package_name,
        "app_name": meta["name"],
        "category": meta["category"],
        "rating": meta["rating"],
        "downloads": meta["downloads"],
        "permissions": permissions,
        "total_permissions": total_perms,
        "data_safety": data_safety,
        "scanned_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "Google Play Store"
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scan.py <package_name_or_url>", file=sys.stderr)
        sys.exit(1)

    pkg = extract_package_name(sys.argv[1])
    try:
        result = scan(pkg)
        print(json.dumps(result, indent=2, ensure_ascii=False))
    except Exception as e:
        print(f"Error scanning {pkg}: {e}", file=sys.stderr)
        sys.exit(1)
