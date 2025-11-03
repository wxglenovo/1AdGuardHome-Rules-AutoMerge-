#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests

URLS_FILE = "urls.txt"
TMP_DIR = "tmp"
DIST_DIR = "dist"
MERGED_FILE = os.path.join(DIST_DIR, "merged_rules.txt")
LOG_FILE = os.path.join(DIST_DIR, "log.txt")

# 创建目录
os.makedirs(TMP_DIR, exist_ok=True)
os.makedirs(DIST_DIR, exist_ok=True)

def process_line(line):
    line = line.strip()
    if not line or line.startswith("!"):
        return []

    results = []

    # HOSTS 规则转换
    if line.startswith("0.0.0.0") or line.startswith("127.0.0.1"):
        parts = line.split()
        if len(parts) >= 2:
            domain = parts[1]
            results.append(f"|{domain}^")
    # 多域名拆分
    elif ',' in line.split('##')[0] or ',' in line.split('#@#')[0] or ',' in line.split('#?#')[0]:
        sep = ''
        if '##' in line:
            sep = '##'
        elif '#@#' in line:
            sep = '#@#'
        elif '#?#' in line:
            sep = '#?#'

        domains_part, suffix = line.split(sep, 1)
        domains = domains_part.split(',')
        for d in domains:
            d = d.strip()
            if line.startswith('||'):
                results.append(f"||{d}{sep}{suffix}")
            else:
                results.append(f"|{d}{sep}{suffix}")
    else:
        results.append(line)

    return results

merged_rules = []
log_lines = []

if not os.path.exists(URLS_FILE):
    print(f"⚠ {URLS_FILE} 不存在")
    exit(1)

with open(URLS_FILE, 'r', encoding='utf-8') as f:
    urls = [line.strip() for line in f if line.strip()]

for idx, url in enumerate(urls, start=1):
    print(f"🔗 处理源 {idx}/{len(urls)}: {url}")
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        lines = r.text.splitlines()
        processed = []
        for line in lines:
            results = process_line(line)
            for res in results:
                print(f"  ✅ {res}")
                log_lines.append(res)
            processed.extend(results)
        # 保存每个源的拆分结果到 tmp
        tmp_file = os.path.join(TMP_DIR, f"{idx:03}.txt")
        with open(tmp_file, 'w', encoding='utf-8') as ftmp:
            ftmp.write('\n'.join(processed))
        merged_rules.extend(processed)
    except Exception as e:
        print(f"❌ 下载或处理失败: {e}")

# 保存合并后的规则
with open(MERGED_FILE, 'w', encoding='utf-8') as f:
    f.write('\n'.join(merged_rules))

# 保存日志
with open(LOG_FILE, 'w', encoding='utf-8') as f:
    f.write('\n'.join(log_lines))

print(f"🎉 完成！共生成 {len(merged_rules)} 条规则")
print(f"tmp/ 文件: {len(os.listdir(TMP_DIR))} 个")
print(f"合并规则文件: {MERGED_FILE}")
print(f"日志文件: {LOG_FILE}")
