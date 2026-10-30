#!/bin/sh
set -eu
cd "$(git rev-parse --show-toplevel)"
expected=${1:-$(git rev-parse HEAD)}
assert_source() {
  [ "$(git rev-parse HEAD)" = "$expected" ] || { echo 'Validation source does not match pushed commit.' >&2; exit 1; }
  [ -z "$(git status --porcelain --untracked-files=normal)" ] || { echo 'Commit or remove source changes, including untracked files, before validation.' >&2; exit 1; }
}
assert_source
evidence=$(git rev-parse --git-path local-validation)
mkdir -p "$evidence"
receipt="$evidence/$expected.md"
pending="$receipt.pending"
rm -f "$receipt" "$pending"
trap 'rm -f "$pending"' EXIT HUP INT TERM
{
  printf '# Local validation\n\nCommit: `%s`\n\n' "$expected"
  printf 'Environment: `%s`\n\n' "$(uname -srm)"
  printf 'Started UTC: %s\n\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
} > "$pending"
run_check() {
  command=$1
  printf '\n> %s\n' "$command"
  if sh -c "$command"; then
    printf -- '- PASS: `%s`\n' "$command" >> "$pending"
  else
    result=$?
    echo "Validation failed (exit $result): $command" >&2
    exit "$result"
  fi
  assert_source
}
run_check 'git show --format= --check HEAD'
. ./scripts/local-checks.sh
assert_source
printf '\nCompleted UTC: %s\n' "$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$pending"
mv "$pending" "$receipt"
printf '\nValidation succeeded for %s. PR evidence: %s\n' "$expected" "$receipt"
