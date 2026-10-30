#!/bin/sh
set -eu
cd "$(git rev-parse --show-toplevel)"
if [ -n "$(git config --get core.hooksPath || true)" ] && [ "$(git config --get core.hooksPath)" != .githooks ]; then
  echo 'Existing hooksPath detected. Integrate existing hooks before installing.' >&2
  exit 1
fi
git config --local core.hooksPath .githooks
echo 'Installed tracked pre-push hook for this clone. Run again in each new clone.'
