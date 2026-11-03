#!/usr/bin/env python3
"""Check, load, start, stop, or inspect a structured KV260 runtime."""

import hashlib
import json
import os
import signal
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path


APP = Path(__file__).resolve().parents[1]
MANIFEST = APP / "config/deployment.json"
OVERLAY_HELPER = APP / "drivers/load_overlay.py"
from runtime_paths import DATA
STATE = APP.parent / (APP.name.removesuffix(".previous") + ".state.json")
FIRMWARE_ROOT = Path("/lib/firmware/xilinx")


def fail(message):
    raise RuntimeError(message)


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def digest(data):
    return hashlib.sha256(data).hexdigest()


def environment():
    env = os.environ.copy()
    env["XILINX_XRT"] = "/usr"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONPATH"] = os.pathsep.join(str(APP / part) for part in ("app", "drivers", "ui"))
    env["PATH"] = "/usr/local/share/pynq-venv/bin:" + env.get("PATH", "")
    return env


def load_manifest():
    manifest = read_json(MANIFEST)
    if manifest.get("schema") != 2 or manifest.get("package_layout") != "structured":
        fail("Expected schema 2 structured deployment.json")
    for key in ("bit", "hwh", "dtbo", "bit_bin"):
        relative = Path(manifest.get(key, ""))
        target = (APP / relative).resolve()
        if relative.is_absolute() or not target.is_relative_to(APP) or not target.is_file():
            fail("Missing or invalid hardware file: " + key)
    if not manifest.get("python") or not Path(manifest["python"]).is_file():
        fail("PYNQ Python interpreter not found: " + str(manifest.get("python")))
    firmware_basename = manifest.get("firmware_basename", manifest.get("name", "kv260-design"))
    firmware_name = manifest.get("firmware_name", firmware_basename + ".bit.bin")
    if Path(firmware_basename).name != firmware_basename or Path(firmware_name).name != firmware_name:
        fail("firmware_basename and firmware_name must be plain filenames")
    for key in ("pre_load", "media_setup", "live"):
        value = manifest.get(key, [])
        if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
            fail(key + " must be a list of command arguments")
    if not manifest.get("live"):
        fail("live command must be configured")
    if not any(ET.parse(APP / manifest["hwh"]).getroot().iter("MODULE")):
        fail("HWH contains no MODULE metadata")
    return manifest


def artifact_paths(manifest, destination):
    destination.mkdir(parents=True, exist_ok=True)
    paths = {}
    firmware_basename = manifest.get("firmware_basename", manifest.get("name", "kv260-design"))
    for key in ("bit", "hwh", "dtbo"):
        suffix = {"bit": ".bit", "hwh": ".hwh", "dtbo": ".dtbo"}[key]
        target = destination / (firmware_basename + suffix)
        target.write_bytes((APP / manifest[key]).read_bytes())
        paths[key] = target
    if manifest.get("bit_bin"):
        source = APP / manifest["bit_bin"]
        if not source.is_file():
            fail("Missing bit_bin: " + str(source))
    else:
        source = paths["bit"]
    bit_bin = destination / (firmware_basename + ".bit.bin")
    bit_bin.write_bytes(source.read_bytes())
    paths["bit_bin"] = bit_bin
    if manifest.get("xclbin"):
        source_xclbin = APP / manifest["xclbin"]
        if not source_xclbin.is_file():
            fail("Missing xclbin: " + str(source_xclbin))
        target = destination / "design.xclbin"
        target.write_bytes(source_xclbin.read_bytes())
        paths["xclbin"] = target
    return paths


def format_command(manifest, command_key, paths):
    values = {"dir": str(APP), "python": manifest["python"]}
    values.update({key: str(value) for key, value in paths.items()})
    return [item.format_map(values) for item in manifest.get(command_key, [])]


def invoke(manifest, key, paths):
    command = format_command(manifest, key, paths)
    if command:
        print(key + ": " + " ".join(command), flush=True)
        subprocess.run(command, check=True, cwd=APP, env=environment())


def prepare_check(manifest):
    check_dir = Path("/tmp") / ("kv260-check-" + manifest.get("name", APP.name))
    paths = artifact_paths(manifest, check_dir)
    command = [manifest["python"], str(OVERLAY_HELPER), "--bit", str(paths["bit"]), "--dtbo", str(paths["dtbo"]), "--check-only"]
    subprocess.run(command, check=True, cwd=APP, env=environment())
    print("CHECK_PASS folder={} bit={} hwh={} dtbo={}".format(APP, manifest["bit"], manifest["hwh"], manifest["dtbo"]), flush=True)


def hardware_hash(manifest):
    digest_obj = hashlib.sha256()
    for key in ("bit", "hwh", "dtbo", "bit_bin", "xclbin"):
        name = manifest.get(key)
        if name:
            digest_obj.update(Path(name).name.encode("utf-8"))
            digest_obj.update((APP / name).read_bytes())
    return digest_obj.hexdigest()


def read_state():
    return read_json(STATE) if STATE.is_file() else {}


def save_state(value):
    temp = STATE.with_suffix(".tmp")
    temp.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    temp.replace(STATE)


def process_alive(pid):
    if not isinstance(pid, int) or pid < 2:
        return False
    try:
        stat = Path("/proc") / str(pid) / "stat"
        if stat.is_file() and stat.read_text().rsplit(") ", 1)[1].split()[0] == "Z":
            return False
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False


def stop_pid(pid, group=True):
    if not process_alive(pid):
        return
    try:
        (os.killpg if group else os.kill)(pid, signal.SIGTERM)
    except ProcessLookupError:
        return
    for _ in range(300):
        if not process_alive(pid):
            return
        time.sleep(0.1)
    fail("Program is still draining DMA after 30s; retained buffers and files. Inspect before retrying.")


def stop_existing(manifest, state):
    pid = state.get("pid")
    if process_alive(pid):
        proc = Path("/proc") / str(pid)
        marker = state.get("process_marker", "run_pipeline.py")
        command_line = (proc / "cmdline").read_bytes()
        if marker.encode() not in command_line:
            fail("PID file points to another process; refusing to stop it")
        stop_pid(pid)
    elif not state and manifest.get("legacy_pid_file"):
        pid_file = Path(manifest["legacy_pid_file"])
        if pid_file.is_file():
            try:
                old_pid = int(pid_file.read_text().strip())
            except ValueError:
                fail("Legacy PID file is invalid")
            cmdline = Path("/proc") / str(old_pid) / "cmdline"
            marker = manifest.get("legacy_cmd_contains", "run_pipeline.py")
            if cmdline.is_file() and marker.encode() in cmdline.read_bytes():
                stop_pid(old_pid, group=False)
            elif process_alive(old_pid):
                fail("Legacy PID does not match run_pipeline.py")
    time.sleep(1)
    busy = subprocess.run(["fuser", "/dev/video0"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if busy.returncode == 0:
        fail("/dev/video0 remains busy; no hardware changes were made")


def activate(manifest, reload_hardware):
    hardware_dir = FIRMWARE_ROOT / manifest.get("name", "kv260-whiteboard")
    paths = artifact_paths(manifest, hardware_dir)
    if reload_hardware:
        # FPGA full overlays request the bitstream by the literal
        # firmware-name stored in their DTBO. It is not necessarily the
        # same path passed to fpgautil -b, so stage that alias in the kernel's
        # default firmware search directory (/lib/firmware on this image).
        firmware_name = manifest.get("firmware_name", paths["bit_bin"].name)
        firmware_request = Path("/lib/firmware") / firmware_name
        firmware_request.write_bytes(paths["bit_bin"].read_bytes())
        subprocess.run(["xmutil", "unloadapp"], check=False, env=environment())
        invoke(manifest, "pre_load", paths)
        command = [manifest["python"], str(OVERLAY_HELPER), "--bit", str(paths["bit"]), "--dtbo", str(paths["dtbo"])]
        subprocess.run(command, check=True, cwd=APP, env=environment())
        subprocess.run(["udevadm", "settle", "--timeout=15"], check=True)
    invoke(manifest, "media_setup", paths)
    DATA.mkdir(parents=True, exist_ok=True)
    log_path = DATA / "live.log"
    if log_path.is_file() and log_path.stat().st_size > 16 * 1024 * 1024:
        log_path.replace(DATA / "live.previous.log")
    with log_path.open("ab") as log:
        log.write(("\nSTART {}\n".format(time.strftime("%Y-%m-%d %H:%M:%S"))).encode())
        log.flush()
        live_command = format_command(manifest, "live", paths)
        process = subprocess.Popen(live_command, cwd=APP, env=environment(), stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    time.sleep(4)
    if process.poll() is not None:
        fail("Live program exited; inspect " + str(log_path))
    marker = next((item for item in live_command if item.endswith(".py")), "run_pipeline.py")
    return process.pid, marker, log_path


def deploy(manifest):
    from verify_manifest import verify_package
    verify_package(APP)
    state = read_state()
    new_hash = hardware_hash(manifest)
    skip_load = bool(state and process_alive(state.get("pid")) and state.get("hardware_hash") == new_hash)
    stop_existing(manifest, state)
    try:
        pid, marker, log = activate(manifest, not skip_load)
    except Exception:
        print("DEPLOY FAILED; automatic full-load retry is disabled. Check FPGA manager and media devices before retrying.", file=sys.stderr, flush=True)
        raise
    save_state({"folder": str(APP), "pid": pid, "process_marker": marker, "hardware_hash": new_hash, "started": time.strftime("%Y-%m-%d %H:%M:%S")})
    print("DEPLOY_RUNNING folder={} pid={} FPGA_reloaded={} log={}".format(APP, pid, not skip_load, log), flush=True)


def main():
    action = sys.argv[1] if len(sys.argv) > 1 else "deploy"
    if action not in ("check", "deploy", "status", "stop", "rollback"):
        fail("Usage: run.sh [check|deploy|status|stop|rollback]")
    if os.geteuid() != 0:
        fail("Run with sudo: sudo ./run.sh " + action)
    if action == "rollback":
        previous = APP.with_name(APP.name + ".previous")
        if not (previous / "run.sh").is_file():
            fail("No previous package folder exists")
        stop_existing(load_manifest(),read_state())
        temporary = APP.with_name(APP.name + ".rollback-tmp")
        if temporary.exists():
            fail("A previous rollback operation left a temporary folder: " + str(temporary))
        APP.rename(temporary)
        previous.rename(APP)
        temporary.rename(previous)
        os.execv("/bin/bash", ["/bin/bash", str(APP / "run.sh"), "deploy"])
    manifest = load_manifest()
    if action == "check":
        prepare_check(manifest)
    elif action == "status":
        state = read_state()
        state["alive"] = process_alive(state.get("pid"))
        print(json.dumps(state, indent=2), flush=True)
    elif action == "stop":
        stop_existing(manifest, read_state())
        print("STOPPED", flush=True)
    else:
        deploy(manifest)


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print("BOARD RUN ERROR:", exc, file=sys.stderr, flush=True)
        sys.exit(1)
