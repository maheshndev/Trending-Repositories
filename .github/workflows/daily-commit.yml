name: Trending Repos Tracker

on:
  schedule:
    - cron: '0 0 * * *' # Every day at midnight UTC
  workflow_dispatch:

jobs:
  update-trending:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.x'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install requests python-dateutil PyGithub

      - name: Run trending repo updater
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
        run: |
          python update_trending.py

      - name: Commit and push changes
        run: |
          git config user.name github-actions
          git config user.email github-actions@github.com
          git add .
          git commit -m "Update trending repositories for $(date +'%Y-%m-%d')" || echo "No changes to commit"
          git push
