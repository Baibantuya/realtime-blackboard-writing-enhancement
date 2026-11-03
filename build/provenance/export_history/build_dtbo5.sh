#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "$0")" && pwd)/dtbo_candidate5"
test ! -e "$ROOT/legacy_recompiled.dtbo" && test ! -e "$ROOT/imx219-v24-2025-2-c5.dtbo"
dtc --version > "$ROOT/tool_version.txt"
dtc -@ -I dts -O dtb -o "$ROOT/legacy_recompiled.dtbo" "$ROOT/legacy.dts" > "$ROOT/legacy_compile.log" 2>&1
dtc -@ -I dts -O dtb -o "$ROOT/imx219-v24-2025-2-c5.dtbo" "$ROOT/imx219-v24-2025-2-c5.dts" > "$ROOT/candidate_compile.log" 2>&1
printf 'DTBO_COMPILE_COMPLETE_NOT_BOARD_TESTED\n'
