#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
test ! -e report/native_math
mkdir -p report/native_math
for unit in local_sum ray_tally; do
    g++ -std=c++14 -O2 -Wall -Wextra -Wno-unknown-pragmas -Isrc/pl/hls "sim/tb/test_${unit}.cpp" -o "report/native_math/test_${unit}" 2> "report/native_math/${unit}_build.log"
    "report/native_math/test_${unit}" > "report/native_math/${unit}.log"
done
