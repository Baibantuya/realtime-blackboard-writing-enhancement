"""Reproduce Linux UI builds and checks in a Linux-owned directory (WSL compatible)."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import zipfile


def run(command, cwd, log):
    if log.exists():
        history = log.parent / "history"
        history.mkdir(exist_ok=True)
        shutil.copyfile(log, history / f"{log.stem}-{time.time_ns()}{log.suffix}")
    with log.open("w", encoding="utf-8") as output:
        result = subprocess.run(command, cwd=cwd, stdout=output, stderr=subprocess.STDOUT)
    print(log.read_text(encoding="utf-8")[-2200:], flush=True)
    if result.returncode:
        raise SystemExit(f"Failed ({result.returncode}): {command}; see {log}")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lvgl-archive", type=Path, required=True)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--baseline", action="store_true")
    args = parser.parse_args()
    if sys.platform != "linux":
        parser.error("Run inside Linux/WSL.")
    source = Path(__file__).resolve().parents[1]
    work = args.work.expanduser().resolve()
    if work == source or source in work.parents or str(work).startswith("/mnt/"):
        parser.error("Use a separate directory inside the Linux filesystem.")
    work.mkdir(parents=True, exist_ok=True)
    evidence = work / "evidence"
    evidence.mkdir(exist_ok=True)
    checksum = hashlib.sha256(args.lvgl_archive.read_bytes()).hexdigest()
    if checksum != "3ddbd2ac5c98fbad41b7d0aa8f6026f722f5a11daaf32d0422da913ec44437da":
        raise SystemExit("LVGL archive differs from the verified 9.6.0 source.")
    dependency = work / "dependency"
    dependency.mkdir(exist_ok=True)
    lvgl = dependency / "lvgl-80ca777e37a2b176770726a02e07a6fb79ef0b39"
    if not lvgl.exists():
        with zipfile.ZipFile(args.lvgl_archive) as bundle:
            for name in bundle.namelist():
                resolved = (dependency / name).resolve()
                if dependency not in resolved.parents:
                    raise SystemExit("Unsafe LVGL archive member.")
            bundle.extractall(dependency)
    matched = 0
    with zipfile.ZipFile(args.lvgl_archive) as bundle:
        for member in bundle.infolist():
            if member.is_dir():
                continue
            cached = dependency / member.filename
            if not cached.is_file() or hashlib.sha256(cached.read_bytes()).digest() != hashlib.sha256(bundle.read(member)).digest():
                raise SystemExit("Cached LVGL source differs from archive: " + member.filename)
            matched += 1
    (evidence / "lvgl_verification.json").write_text(json.dumps({
        "archive_sha256": checksum, "matched_source_files": matched, "version": "9.6.0"
    }, indent=2), encoding="utf-8")
    target = work / "source"
    target.mkdir(exist_ok=True)
    copied = {}
    for path in source.rglob("*"):
        if not path.is_file() or path.suffix not in (".c", ".h", ".txt", ".py", ".md"):
            continue
        relative = path.relative_to(source)
        if any(part in ("__pycache__", "build", ".git") for part in relative.parts):
            continue
        destination = target / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        content = path.read_bytes()
        if not destination.exists() or destination.read_bytes() != content:
            shutil.copyfile(path, destination)
        copied[str(relative)] = hashlib.sha256(content).hexdigest()
    (evidence / "source_sha256.json").write_text(json.dumps(copied, indent=2), encoding="utf-8")
    print("Source snapshot copied to " + str(target), flush=True)
    build = work / "build"
    run(["cmake", "-S", str(target), "-B", str(build), "-G", "Ninja",
         "-DLVGL_SOURCE_DIR=" + str(lvgl), "-DCMAKE_BUILD_TYPE=Release"], work, evidence / "configure.log")
    run(["cmake", "--build", str(build), "--parallel", "4"], work, evidence / "build.log")
    for name in ("board_light_control_test", "board_light_diagnostics_test", "board_light_inbox_test"):
        run([str(build / name)], work, evidence / (name + ".log"))
    if not args.baseline:
        run(["ctest", "--test-dir", str(build), "--output-on-failure"], work, evidence / "ctest.log")
    print("Linux build/checks complete: " + str(build), flush=True)


if __name__ == "__main__":
    main()
