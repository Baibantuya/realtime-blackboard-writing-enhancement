#!/usr/bin/env bash
# Requires installed AMD 2025.2 tools and licensed devices/IP in PATH.
# This entry is prepared for Linux; the full tool flow has only run on Windows.
set -euo pipefail
cd "$(dirname "$0")/.."
for generated in h v i; do
    if [ -e "$generated" ]; then echo "Use a fresh source-only directory" >&2; exit 1; fi
done
mkdir -p logs report
python3 build/verify_sources.py > logs/inputs_before.json
for core in r s w; do
    vitis-run --mode hls --tcl "build/hls_${core}.tcl" > "logs/hls_${core}.log" 2>&1
done
vivado -mode batch -source build/vivado.tcl -log logs/vivado.log -journal logs/vivado.jou > logs/vivado_console.log 2>&1
python3 build/verify_sources.py > logs/inputs_after.json
