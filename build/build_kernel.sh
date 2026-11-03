#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd)"
WORK="$ROOT/build/work/kernel"
mkdir -p "$WORK"
cp "$ROOT/src/kernel/"*.c "$WORK/"
cp "$ROOT/src/kernel/makefile.template" "$WORK/Makefile"
make -C "/lib/modules/$(uname -r)/build" M="$WORK" modules
