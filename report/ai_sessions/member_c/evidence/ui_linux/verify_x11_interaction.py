"""Drive our SDL window through X11 input and retain renderer captures plus state assertions."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time
from PIL import Image


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    trace = args.out / "input_trace.jsonl"
    if trace.exists() or (args.out / "window.log").exists():
        parser.error("Choose a fresh evidence folder; existing runs are preserved.")
    checks = []
    captures = []
    environment = dict(os.environ, SDL_VIDEODRIVER="x11")
    log = (args.out / "window.log").open("w", encoding="utf-8")
    process = subprocess.Popen([str(args.binary), "--trace", str(trace), "--capture-dir", str(args.out),
                                "--quit-after-ms", "180000"], stdout=log, stderr=subprocess.STDOUT, env=environment)

    def records():
        if not trace.exists():
            return []
        result = []
        for line in trace.read_text(encoding="utf-8").splitlines():
            try:
                result.append(json.loads(line))
            except json.JSONDecodeError:
                pass
        return result

    def wait(predicate, description, timeout=6):
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            events = records()
            if events and predicate(events[-1]):
                checks.append(dict(check=description, state=events[-1]))
                print("PASS: " + description, flush=True)
                return events[-1]
            if process.poll() is not None:
                raise RuntimeError("SDL window exited early; inspect window.log")
            time.sleep(0.03)
        raise AssertionError(description + ": latest trace " + repr(records()[-3:]))

    def xdo(*command):
        return subprocess.run(["xdotool", *map(str, command)], env=environment,
                              text=True, capture_output=True, check=True, timeout=8).stdout

    def stays(predicate, description, seconds):
        deadline = time.monotonic() + seconds
        while time.monotonic() < deadline:
            rows = records()
            if process.poll() is not None or not rows or not predicate(rows[-1]):
                raise AssertionError(description + ": latest trace " + repr(rows[-3:]))
            time.sleep(0.03)
        checks.append(dict(check=description, observed_seconds=seconds, state=rows[-1]))
        print("PASS: " + description, flush=True)

    def press(key):
        # SDL rejects XSendEvent keyboard messages. Focus our own window, then use XTest.
        xdo("windowfocus", "--sync", window)
        if xdo("getwindowfocus").strip() != window:
            raise RuntimeError("Our test window does not own X11 keyboard focus.")
        xdo("key", "--clearmodifiers", key)

    def click(x, y):
        geometry = dict(line.split("=", 1) for line in xdo("getwindowgeometry", "--shell", window).splitlines())
        width, height = int(geometry["WIDTH"]), int(geometry["HEIGHT"])
        draw_w, draw_h = width, width * 1080 // 1920
        if draw_h > height:
            draw_w, draw_h = height * 1920 // 1080, height
        sx = (width-draw_w)//2 + x*draw_w//1920
        sy = (height-draw_h)//2 + y*draw_h//1080
        # --sync waits for motion; clicking the same fixed handle twice has
        # no new motion and can block indefinitely. The subsequent state check
        # verifies the actual click, including the SDL coordinate transform.
        xdo("mousemove", "--window", window, sx, sy)
        xdo("click", "1")

    def capture(name):
        time.sleep(0.15)
        previous = records()[-1]["captures"]
        press("F12")
        state = wait(lambda item: item["captures"] == previous + 1, "renderer capture: " + name)
        bitmap = args.out / f"capture-{state['captures']:03d}.bmp"
        with Image.open(bitmap) as source:
            source.convert("RGB").save(args.out / (name + ".png"))
        captures.append(name + ".png")

    try:
        wait(lambda item: any(record["event"] == "ready" for record in records()), "WSLg window ready")
        found = xdo("search", "--onlyvisible", "--pid", process.pid).splitlines()
        if len(found) != 1:
            raise RuntimeError("Expected exactly one window owned by our test process: " + repr(found))
        window = found[0]
        xdo("windowfocus", "--sync", window)
        # WSLg remaps/focuses a newly shown surface asynchronously. Its first
        # focus report can precede a queued focus loss/gain cycle; early XTest
        # input is discarded. Wait for both SDL focus and a quiet event stream.
        xdo("mousemove", "--window", window, 510, 400)
        deadline = time.monotonic() + 8
        last_count, stable_since = -1, time.monotonic()
        while time.monotonic() < deadline:
            rows = records()
            if len(rows) != last_count:
                last_count, stable_since = len(rows), time.monotonic()
            if rows and rows[-1]["input_focus"] and rows[-1]["pointer_focus"] \
                    and time.monotonic() - stable_since >= 0.5:
                break
            time.sleep(0.03)
        else:
            raise AssertionError("WSLg window focus did not settle")
        wait(lambda item: item["input_focus"] == 1 and item["pointer_focus"] == 1,
             "SDL receives stable keyboard and pointer focus before input")
        # The first synthetic event can still be discarded during WSLg/XTest
        # activation. Establish an observed input round trip with a harmless
        # modifier; never retry a control action or use it as setup input.
        deadline = time.monotonic() + 4
        while not any(row["event"] == "key" for row in records()):
            if time.monotonic() >= deadline:
                raise AssertionError("WSLg did not deliver the setup modifier")
            xdo("key", "Shift_L")
            time.sleep(0.15)
        wait(lambda item: item["serial"] == 0 and item["collapsed"] == 1,
             "input setup does not issue a control request")
        wait(lambda item: item["collapsed"] == 1 and item["toolbar_visible"] == 0
             and item["status_visible"] == 0 and item["toggle_visible"] == 1,
             "startup shows only the up-arrow handle")
        wait(lambda item: item["width"] == 1920 and item["height"] == 1080 and item["native_1080p"] == 1
             and item["font_bpp"] == 8 and item["linear_filter"] == 1,
             "default window uses native 1080p and Regular A8 glyphs")
        capture("startup-collapsed")
        click(1844, 1044)
        wait(lambda item: item["collapsed"] == 0 and item["toolbar_visible"] == 1
             and item["status_visible"] == 1, "mouse: up arrow opens toolbar")
        capture("main")
        idle_start = time.monotonic()
        before = records()[-1]
        wait(lambda item: item["event"] == "idle-collapse" and item["collapsed"] == 1
             and item["toolbar_visible"] == 0 and item["status_visible"] == 0 and item["toggle_visible"] == 1,
             "10 seconds idle hides toolbar and status", timeout=12)
        elapsed = time.monotonic() - idle_start
        assert 9 <= elapsed <= 11.5, elapsed
        assert all(records()[-1][key] == before[key] for key in ("mode", "board", "background", "recovery", "serial"))
        checks.append(dict(check="auto-hide preserves all control settings", observed_seconds=elapsed, state=records()[-1]))
        capture("auto-collapsed")
        click(1844, 1044)
        wait(lambda item: item["collapsed"] == 0, "mouse reopens toolbar after idle")
        stays(lambda item: item["collapsed"] == 0, "toolbar remains visible before timeout", 6)
        press("F2")
        wait(lambda item: item["mode"] == 1, "keyboard activity restarts idle timer")
        stays(lambda item: item["collapsed"] == 0, "keyboard activity extends visibility past original deadline", 6)
        click(296, 984)
        wait(lambda item: item["event"] == "up" and item["mode"] == 1, "mouse activity restarts idle timer")
        stays(lambda item: item["collapsed"] == 0, "mouse activity extends visibility past keyboard deadline", 6)
        wait(lambda item: item["collapsed"] == 1, "idle timer resumes after mouse activity", timeout=6)
        click(1844, 1044)
        wait(lambda item: item["collapsed"] == 0, "reopen for idle dialog check")
        press("F6")
        wait(lambda item: item["panel"] == 1, "confirmation opens for idle dialog check")
        stays(lambda item: item["panel"] == 1 and item["collapsed"] == 0 and item["toggle_visible"] == 0,
              "confirmation stays open beyond idle timeout", 11)
        press("Escape")
        wait(lambda item: item["panel"] == 0 and item["collapsed"] == 0, "closing dialog restarts full idle period")
        stays(lambda item: item["collapsed"] == 0, "toolbar stays visible after closing idle dialog", 6)
        wait(lambda item: item["collapsed"] == 1, "auto-hide resumes after closing dialog", timeout=6)
        click(1844, 1044)
        wait(lambda item: item["collapsed"] == 0, "reopen after idle dialog check")
        click(772, 984)
        wait(lambda item: item["board"] == 1, "mouse: select whiteboard")
        capture("white")
        press("F4")
        wait(lambda item: item["board"] == 0, "keyboard: select blackboard")
        click(296, 984)
        wait(lambda item: item["mode"] == 1, "mouse: select basic enhancement")
        press("F6")
        before = wait(lambda item: item["panel"] == 1, "record confirmation opens")
        capture("initialize")
        press("F3")
        time.sleep(0.15)
        assert records()[-1]["mode"] == 1 and records()[-1]["serial"] == before["serial"]
        checks.append(dict(check="modal blocks background shortcut", state=records()[-1]))
        press("Escape")
        wait(lambda item: item["panel"] == 0 and item["background"] == 0, "Escape cancels recording")
        press("F6"); press("Tab"); press("Return")
        wait(lambda item: item["background"] == 1 and item["recovery"] == 0, "Tab/Enter confirms recording without enabling recovery")
        press("F5")
        wait(lambda item: item["recovery"] == 1, "recovery remains an independent switch")
        press("F1")
        wait(lambda item: item["mode"] == 0 and item["recovery"] == 1, "original mode preserves independent recovery state")
        capture("recovery")
        press("F7")
        before = wait(lambda item: item["panel"] == 2, "parameters open")
        capture("parameters")
        press("Up")
        edited = wait(lambda item: item["draft"] != before["draft"], "arrow edits parameter draft")
        press("F10")
        wait(lambda item: item["info"] == 1 and item["panel"] == 2, "diagnostics overlays parameter draft")
        capture("diagnostics")
        press("Escape")
        wait(lambda item: item["info"] == 0 and item["draft"] == edited["draft"], "diagnostics return preserves draft")
        press("Escape")
        wait(lambda item: item["panel"] == 0 and item["delta"] == before["delta"], "cancel leaves applied parameters unchanged")
        press("F7"); press("Up")
        edited = wait(lambda item: item["panel"] == 2 and item["draft"] != before["draft"], "edit draft again")
        click(1542, 933)
        wait(lambda item: item["panel"] == 0 and item["delta"] == edited["draft"]
             and item["background"] == 0 and item["recovery"] == 0, "mouse applies draft and invalidates prior background")
        click(1844, 1044)
        wait(lambda item: item["collapsed"] == 1 and item["toolbar_visible"] == 0
             and item["status_visible"] == 0 and item["toggle_visible"] == 1,
             "mouse: down arrow hides toolbar and status")
        capture("collapsed")
        click(1844, 1044)
        wait(lambda item: item["collapsed"] == 0, "mouse: same handle reopens toolbar")
        press("F9")
        wait(lambda item: item["collapsed"] == 1, "F9 still collapses toolbar")
        press("shift+Tab"); press("Return")
        wait(lambda item: item["collapsed"] == 0, "collapsed keyboard focus stays on expand")
        press("F8")
        before = wait(lambda item: item["known"] == 0, "disconnect disables operations")
        capture("disconnected")
        click(296, 984); press("F2")
        time.sleep(0.15)
        assert records()[-1]["known"] == 0 and records()[-1]["serial"] == before["serial"]
        checks.append(dict(check="disabled mouse/key cannot issue control request", state=records()[-1]))
        press("F8")
        wait(lambda item: item["known"] == 1, "return to local demo")
        xdo("windowsize", "--sync", window, 1000, 800)
        wait(lambda item: item["width"] == 1000 and item["height"] == 800, "resize to letterboxed window")
        click(772, 984)
        before = wait(lambda item: item["board"] == 1, "mouse coordinates remain correct after resize")
        xdo("mousemove", "--sync", "--window", window, 5, 5); xdo("click", "1")
        time.sleep(0.15)
        assert records()[-1]["serial"] == before["serial"]
        checks.append(dict(check="letterbox ignores clicks", state=records()[-1]))
        capture("resized")
        click(1844, 1044)
        wait(lambda item: item["collapsed"] == 1 and item["status_visible"] == 0,
             "mouse: down arrow works after letterboxed resize")
        capture("resized-collapsed")
        click(1844, 1044)
        wait(lambda item: item["collapsed"] == 0 and item["toolbar_visible"] == 1,
             "mouse: up arrow works after letterboxed resize")
        press("F11")
        wait(lambda item: item["fullscreen"] == 1, "F11 enters fullscreen")
        press("Escape")
        wait(lambda item: item["fullscreen"] == 0, "Escape restores windowed mode")
        press("F4")
        wait(lambda item: item["board"] == 0, "restore blackboard preview")
        receipt = dict(status="PASS", driver="x11/WSLg", input="xdotool X11 mouse and keyboard events",
                       binary_sha256=hashlib.sha256(args.binary.read_bytes()).hexdigest(),
                       process_id=process.pid, window_id=window, checks=checks, captures=captures,
                       scope="Synthetic LVGL display and interaction only; no camera, FPGA or real history pixels")
        (args.out / "interaction_receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"PASS: {len(checks)} interaction/capture checks", flush=True)
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill(); process.wait(timeout=5)
        log.close()


if __name__ == "__main__":
    main()
