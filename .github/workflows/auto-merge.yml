name: Merge Rules & Commit

on:
  workflow_dispatch: {}        # 手动触发
  schedule:
    - cron: "*/20 * * * *"    # 每 20 分钟执行一次 (UTC 时间)

jobs:
  merge_commit:
    runs-on: ubuntu-latest

    steps:
      # 1️⃣ Checkout 仓库并保持 GITHUB_TOKEN 权限
      - name: Checkout repository
        uses: actions/checkout@v3
        with:
          persist-credentials: true

      # 2️⃣ 安装 Python
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: 3.x

      # 3️⃣ 安装依赖
      - name: Install requests
        run: pip install requests

      # 4️⃣ 运行 merge_rules.py
      - name: Run merge_rules.py
        run: python merge_rules.py

      # 5️⃣ 显示生成文件（调试用）
      - name: List tmp/dist
        run: |
          echo "当前目录: $(pwd)"
          ls -R

      # 6️⃣ 设置 Git 用户
      - name: Set Git user
        run: |
          git config --global user.name "github-actions[bot]"
          git config --global user.email "github-actions[bot]@users.noreply.github.com"

      # 7️⃣ 添加 tmp/dist 文件
      - name: Add tmp/dist files
        run: |
          git add tmp/*.txt dist/*.txt || echo "没有文件可添加"

      # 8️⃣ Commit 变更（仅有变更才 commit）
      - name: Commit changes
        run: |
          git diff --cached --quiet || git commit -m "更新合并规则"

      # 9️⃣ Push 变更
      - name: Push changes
        run: git push origin HEAD

      # 🔟 上传 artifact
      - name: Upload merged rules artifacts
        uses: actions/upload-artifact@v4
        with:
          name: merged-rules-artifacts
          path: |
            tmp/*.txt
            dist/merged_rules.txt
            dist/log.txt
