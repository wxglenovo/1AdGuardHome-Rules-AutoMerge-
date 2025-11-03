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

def process_line(line):
    line = line.strip()
    log_msgs = []
    results = []

    if not line:
        return results, log_msgs

    # 去掉注释行
    if line.startswith("!"):
        log_msgs.append(f"🚫 去掉注释行: {line}")
        return results, log_msgs

    # HOSTS 转换
    if line.startswith("0.0.0.0") or line.startswith("127.0.0.1"):
        parts = line.split()
        if len(parts) >= 2:
            hosts = parts[1].split(",")  # 多域名逗号拆分
            for host in hosts:
                host = host.strip()
                if host:
                    converted = f"||{host}^"
                    results.append(converted)
                    log_msgs.append(f"✅ HOSTS 转换: {line} → {converted}")
        else:
            log_msgs.append(f"⚠ HOSTS 格式错误，忽略: {line}")
        return results, log_msgs

    # 多域名拆分规则
    if "," in line:
        sep = ''
        if '##' in line:
            sep = '##'
        elif '#@#' in line:
            sep = '#@#'
        elif '#?#' in line:
            sep = '#?#'

        if sep:
            domains_part, suffix = line.split(sep, 1)
            domains = [d.strip() for d in domains_part.split(",") if d.strip()]
            for domain in domains:
                new_rule = f"||{domain}{sep}{suffix}"
                results.append(new_rule)
                log_msgs.append(f"✅ 多域名拆分: {line} → {new_rule}")
        else:
            # 普通逗号规则
            domains = [d.strip() for d in line.split(",") if d.strip()]
            for domain in domains:
                new_rule = f"||{domain}^"
                results.append(new_rule)
                log_msgs.append(f"✅ 多域名拆分: {line} → {new_rule}")
        return results, log_msgs

    # 普通规则，不打印日志
    results.append(line)
    return results, log_msgs

def main():
    merged_rules = []
    log_lines = []

    if not os.path.exists(URLS_FILE):
        print(f"⚠ {URLS_FILE} 不存在")
        return

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
                    print(log)         # 中文逐条打印日志
                    log_lines.append(log)
                processed.extend(results)
            # 保存每个源拆分后的规则
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
    print(f"📂 tmp/ 文件: {len(os.listdir(TMP_DIR))} 个")
    print(f"📄 合并规则文件: {MERGED_FILE}")
    print(f"📝 日志文件: {LOG_FILE}")

if __name__ == "__main__":
    main()
