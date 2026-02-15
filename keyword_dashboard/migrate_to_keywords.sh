#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "사용법: ./migrate_to_keywords.sh https://github.com/<계정명>/keywords.git"
  exit 1
fi

NEW_REMOTE_URL="$1"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

cd "$REPO_ROOT"

if git remote get-url origin >/dev/null 2>&1; then
  git remote remove origin
fi

git remote add origin "$NEW_REMOTE_URL"
git push -u origin HEAD:main

echo "완료: 새 저장소로 푸시되었습니다 -> $NEW_REMOTE_URL"
