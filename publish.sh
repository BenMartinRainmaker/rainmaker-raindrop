#!/bin/bash
# Publishes to GitHub Pages: commits everything and pushes to the rainmaker-raindrop repo.
# The GitHub Action then renders every month and deploys the site (about two minutes).
# Usage:  ./publish.sh [message]
# Live at: https://benmartinrainmaker.github.io/rainmaker-raindrop/<month-folder>/
# Remove everything from the web:  gh repo delete BenMartinRainmaker/rainmaker-raindrop --yes
set -e
cd "$(dirname "$0")"
gh auth switch -u BenMartinRainmaker >/dev/null 2>&1 || true   # never the personal account
git add -A
git commit -qm "${1:-Update raindrop}" || echo "nothing new to commit; pushing anyway"
git pull -q --rebase origin main || { echo "pull failed: someone saved from the web editor at the same time; fix the conflict in content.md, then git rebase --continue and rerun"; exit 1; }
git push -q origin main
echo "Pushed. Watch the build: gh run watch --repo BenMartinRainmaker/rainmaker-raindrop"
echo "Live in ~2 minutes at https://benmartinrainmaker.github.io/rainmaker-raindrop/"
