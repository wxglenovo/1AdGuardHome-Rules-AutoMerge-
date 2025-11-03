#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import requests

URLS_FILE = "urls.txt"
TMP_DIR = "tmp"
DIST_DIR = "dist"
MERGED_FILE = os.path.join(DIST_DIR, "all_rules.txt")

os.makedirs(TMP_DIR, exist_ok=True)
os.makedirs(DIST_DIR, exist_ok=True)


def load_urls():
    urls = []
    with open(URLS_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("!"):
                urls.append(line)
    return urls


def download_rules(url):
    try:
        print(f"🔗 下载: {url}")
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            return r.text.splitlines()
    except Exception as e:
        print(f"⚠ 下载失败 {url} -> {e}")
    return []


# HOSTS 转换
def is_hosts_rule(line):
    parts = line.split()
    return len(parts) == 2 and parts[0] in ["0.0.0.0", "127.0.0.1"]


def convert_hosts_rule(line):
    domain = line.split()[1].strip()
    rule = f"|{domain}^"
    print(f"🧩 HOSTS 转换: {line}  →  {rule}")
    return rule


# 多域名拆分
def is_multi_domain_rule(line):
    if "," not in line:
        return False
    for tag in ["##", "#@#", "#?#"]:
        if tag in line:
            domain_part = line.split(tag)[0]
            if "," in domain_part and all(" " not in d for d in domain_part.split(",")):
                return True
    return False


def split_multi_domain(line):
    suffix_index = None
    prefix = ""
    for tag in ["##", "#@#", "#?#"]:
        idx = line.find(tag)
        if idx != -1:
            suffix_index = idx
            break

    if suffix_index is None:
        return [line]

    domain_part = line[:suffix_index]
    suffix = line[suffix_index:]

    if line.startswith("||"):
        prefix = "||"
        domain_part = domain_part[2:]
    elif line.startswith("|"):
        prefix = "|"
        domain_part = domain_part[1:]

    domains = domain_part.split(",")
    result = []

    print(f"🔁 多域名拆分: {line}")
    for d in domains:
        d = d.strip()
        if d:
            rule = f"{prefix}{d}{suffix}"
            result.append(rule)
            print(f"   → {rule}")

    return result


def main():
    urls = load_urls()
    merged = set()

    for url in urls:
        lines = download_rules(url)
        for line in lines:
            line = line.strip()
            if not line or line.startswith("!"):
                continue

            if is_hosts_rule(line):
                merged.add(convert_hosts_rule(line))
                continue

            if is_multi_domain_rule(line):
                for new_rule in split_multi_domain(line):
                    merged.add(new_rule)
                continue

            merged.add(line)

    # 保存合并结果
    with open(MERGED_FILE, "w", encoding="utf-8") as f:
        for rule in sorted(merged):
            f.write(rule + "\n")

    print(f"✅ 合并完成，总计 {len(merged)} 条规则")
    print(f"📁 输出文件: {MERGED_FILE}")


if __name__ == "__main__":
    main()
