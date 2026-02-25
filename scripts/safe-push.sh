#!/usr/bin/env bash
set -euo pipefail

REMOTE="origin"
BRANCH="main"
EXPECTED_ORIGIN="arjun187456/Honey_sandbox_20260225.git"
ALLOW_DIRTY="false"
NO_PULL="false"

usage() {
  cat <<'EOF'
Usage: scripts/safe-push.sh [options]

Options:
  --remote <name>             Remote name (default: origin)
  --branch <name>             Branch to push (default: main)
  --expected-origin <text>    Required substring in remote URL
                              (default: arjun187456/Honey_sandbox_20260225.git)
  --allow-dirty               Allow push with uncommitted changes
  --no-pull                   Skip pull --rebase before push
  -h, --help                  Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --remote)
      REMOTE="${2:-}"
      shift 2
      ;;
    --branch)
      BRANCH="${2:-}"
      shift 2
      ;;
    --expected-origin)
      EXPECTED_ORIGIN="${2:-}"
      shift 2
      ;;
    --allow-dirty)
      ALLOW_DIRTY="true"
      shift
      ;;
    --no-pull)
      NO_PULL="true"
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      usage
      exit 1
      ;;
  esac
done

if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "❌ Not inside a git repository."
  exit 1
fi

current_branch="$(git branch --show-current)"
if [[ "$current_branch" != "$BRANCH" ]]; then
  echo "❌ Current branch is '$current_branch', expected '$BRANCH'."
  exit 1
fi

if [[ -d .git/rebase-apply || -d .git/rebase-merge ]]; then
  echo "❌ Rebase in progress. Complete/abort rebase first."
  exit 1
fi

if [[ -f .git/MERGE_HEAD ]]; then
  echo "❌ Merge in progress. Complete/abort merge first."
  exit 1
fi

origin_url="$(git remote get-url "$REMOTE" 2>/dev/null || true)"
if [[ -z "$origin_url" ]]; then
  echo "❌ Remote '$REMOTE' does not exist."
  exit 1
fi

if [[ "$origin_url" != *"$EXPECTED_ORIGIN"* ]]; then
  echo "❌ Remote '$REMOTE' URL mismatch."
  echo "   Found:    $origin_url"
  echo "   Expected: contains '$EXPECTED_ORIGIN'"
  exit 1
fi

if [[ "$ALLOW_DIRTY" != "true" ]]; then
  if [[ -n "$(git status --porcelain)" ]]; then
    echo "❌ Working tree is not clean. Commit/stash changes first."
    echo "   (or run with --allow-dirty)"
    exit 1
  fi
fi

echo "🔎 Checks passed"
echo "   Branch: $BRANCH"
echo "   Remote: $REMOTE ($origin_url)"

git fetch "$REMOTE" "$BRANCH"

if ! git rev-parse --verify "${BRANCH}@{upstream}" >/dev/null 2>&1; then
  if git show-ref --verify --quiet "refs/remotes/${REMOTE}/${BRANCH}"; then
    git branch --set-upstream-to="${REMOTE}/${BRANCH}" "$BRANCH"
  fi
fi

if [[ "$NO_PULL" != "true" ]]; then
  echo "⬇️  Pulling latest with rebase..."
  git pull --rebase "$REMOTE" "$BRANCH"
fi

echo "⬆️  Pushing..."
git push -u "$REMOTE" "$BRANCH"

echo "✅ Push complete"
git branch -vv
