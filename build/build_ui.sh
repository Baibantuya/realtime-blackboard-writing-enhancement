#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd)"
WORK="$ROOT/build/work/ui"
mkdir -p "$WORK/source" "$WORK/lvgl"
cp -a "$ROOT/src/ps/ui_native/." "$WORK/source/"
cp "$ROOT/src/ps/ui_native/cmakelists.txt" "$WORK/source/CMakeLists.txt"
tar -xf "$ROOT/src/ps/vendor/lvgl-9.6.0-runtime.tar.gz" -C "$WORK/lvgl"
LVGL_CMAKE="$(find "$WORK/lvgl" -name CMakeLists.txt -print | awk '{print length, $0}' | sort -n | head -1 | cut -d' ' -f2-)"
test -n "$LVGL_CMAKE"
cmake -S "$WORK/source" -B "$WORK/build" -DLVGL_SOURCE_DIR="$(dirname "$LVGL_CMAKE")" -DCMAKE_BUILD_TYPE=Release
cmake --build "$WORK/build" -j "${JOBS:-4}"
printf 'Native UI library (check ELF architecture before deployment): %s\n' "$WORK/build/libboard_ps_ui.so"
