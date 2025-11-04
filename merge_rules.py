#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests

URLS_FILE = "urls.txt"
TMP_DIR = "tmp"
DIST_DIR = "dist"
MERGED_FILE = os.path.join(DIST_DIR, "merged_rules.txt")
LOG_FILE = os.path.join(DIST_DIR, "log.txt")

os.makedirs(TMP_DIR, exist_ok=True)
os.makedirs(DIST_DIR, exist_ok=True)

log_lines = []

# ------------------------------
# 删除 tmp/ 中所有以 # 开头的文件并打印日志
# ------------------------------
for fname in os.listdir(TMP_DIR):
    if fname.startswith("#"):
        fpath = os.path.join(TMP_DIR, fname)
        try:
            os.remove(fpath)
            log_msg = f"🗑 删除注释文件: {fpath}"
            print(log_msg)
            log_lines.append(log_msg)
        except Exception as e:
            log_msg = f"❌ 删除文件失败: {fpath} -> {e}"
            print(log_msg)
            log_lines.append(log_msg)

def process_line(line):
    line = line.strip()
    line_logs = []
    results = []

    if not line:
        return results, line_logs

    # 注释行处理: 记录日志
    if line.startswith("!") or line.startswith("#"):
        line_logs.append(f"🚫 去掉注释行: {line}")
        return results, line_logs

    # HOSTS 规则转换
    if line.startswith("0.0.0.0") or line.startswith("127.0.0.1"):
        parts = line.split()
        if len(parts) >= 2:
            domain = parts[1]
            new_rule = f"|{domain}^"
            results.append(new_rule)
            line_logs.append(f"✅ HOSTS 转换: {line} → {new_rule}")
        return results, line_logs

    # 多域名拆分逻辑
    sep = ''
    if '##' in line:
        sep = '##'
    elif '#@#' in line:
        sep = '#@#'
    elif '#?#' in line:
        sep = '#?#'

    if sep and ',' in line.split(sep)[0]:
        domains_part, suffix = line.split(sep, 1)
        prefix = ''
        if domains_part.startswith('||'):
            prefix = '||'
            domains_part = domains_part[2:]
        elif domains_part.startswith('|'):
            prefix = '|'
            domains_part = domains_part[1:]
        else:
            prefix = '|'
        domains = [d.strip() for d in domains_part.split(',')]
        new_rules = [f"{prefix}{d}{sep}{suffix}" for d in domains]
        results.extend(new_rules)
        line_logs.append(f"✅ 多域名拆分: {line}")
        for r in new_rules:
            line_logs.append(f"    → {r}")
        return results, line_logs

    # 普通规则，不打印日志
    results.append(line)
    return results, line_logs

merged_rules = []

if not os.path.exists(URLS_FILE):
    print(f"⚠ {URLS_FILE} 不存在")
    exit(1)

with open(URLS_FILE, 'r', encoding='utf-8') as f:
    urls = [line.strip() for line in f if line.strip()]

for idx, url in enumerate(urls, start=1):
    print(f"🔗 开始处理第 {idx}/{len(urls)} 个源: {url}")
    try:
        r = requests.get(url, timeout=20)
        r.raise_for_status()
        lines = r.text.splitlines()
        processed = []
        for line in lines:
            results, logs = process_line(line)
            for log in logs:
                print(log)          # 逐条打印日志
                log_lines.append(log)
            processed.extend(results)
        # 保存每个源拆分后的规则
        tmp_file = os.path.join(TMP_DIR, f"{idx:03}.txt")
        with open(tmp_file, 'w', encoding='utf-8') as ftmp:
            ftmp.write('\n'.join(processed))
        merged_rules.extend(processed)
    except Exception as e:
        log_msg = f"❌ 下载或处理失败: {e}"
        print(log_msg)
        log_lines.append(log_msg)

# 保存合并后的规则
with open(MERGED_FILE, 'w', encoding='utf-8') as f:
    f.write('\n'.join(merged_rules))

# 保存日志
with open(LOG_FILE, 'w', encoding='utf-8') as f:
    f.write('\n'.join(log_lines))

print(f"🎉 完成！共生成 {len(merged_rules)} 条规则")
print(f"📂 tmp/ 文件: {len(os.listdir(TMP_DIR))} 个")
print(f"📄 合并规则文件: {MERGED_FILE}")
print(f"📝 日志文件: {LOG_FILE}")
