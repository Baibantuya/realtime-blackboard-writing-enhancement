"""Run against the already loaded, matching V24 overlay. Never loads firmware."""
import argparse
import json
import signal
import time
from .board import BoardIO
from .contracts import BoardState
from .scheduler import VideoScheduler


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--runtime',required=True,help='Matching V24 hardware/device-driver/UI directory')
    parser.add_argument('--no-display',action='store_true')
    parser.add_argument('--seconds',type=float,default=0.)
    parser.add_argument('--content-budget-ms',type=float,default=80.)
    args=parser.parse_args()
    boot_start=time.monotonic()
    print(json.dumps(dict(event='startup_begin',elapsed_ms=0.)),flush=True)
    io=BoardIO(args.runtime,display=not args.no_display)
    print(json.dumps(dict(event='startup_devices_ready',elapsed_ms=(time.monotonic()-boot_start)*1000)),flush=True)
    startup_marks=set()
    scheduler=VideoScheduler(io,content_budget=args.content_budget_ms/1000.)
    stopping=False;started=next_report=time.monotonic()
    def stop(*unused):
        nonlocal stopping
        stopping=True;scheduler.accepting=False;scheduler.resume_after_reset=False
    signal.signal(signal.SIGTERM,stop);signal.signal(signal.SIGINT,stop)
    try:
        while True:
            now=time.monotonic()
            if args.seconds and now-started>=args.seconds:stop()
            io.pump_camera(now)
            capture_epoch=io.camera.capture_epoch
            transform=io.update_geometry(now,capture_epoch)
            if transform is not None and 'geometry' not in startup_marks:
                startup_marks.add('geometry')
                print(json.dumps(dict(event='startup_geometry_ready',elapsed_ms=(now-boot_start)*1000)),flush=True)
            if 'sensor' not in startup_marks and io.sensor.snapshot(now)[0]:
                startup_marks.add('sensor')
                print(json.dumps(dict(event='startup_sensor_ready',elapsed_ms=(now-boot_start)*1000)),flush=True)
            if transform is not None and not stopping:scheduler.publish_transform(transform)
            if scheduler.reset_pending:
                scheduler.resume_after_reset=not stopping and io.state in (BoardState.TRACK,BoardState.OCCLUDED)
            if not stopping and not scheduler.reset_pending:
                scheduler.accepting=io.state in (BoardState.TRACK,BoardState.OCCLUDED)
            io.ui_tick(now,scheduler.request_reset)
            scheduler.tick(now)
            if io.initialized and 'content' not in startup_marks:
                startup_marks.add('content')
                print(json.dumps(dict(event='startup_first_content',elapsed_ms=(time.monotonic()-boot_start)*1000)),flush=True)
            io.discard_unused_camera()
            if now>=next_report:
                print(json.dumps(dict(io.report(now),scheduler=scheduler.metrics)),flush=True)
                next_report=now+2.
            if stopping and not scheduler.work and not scheduler.active:break
            time.sleep(.0005)
    finally:
        # A hardware timeout must retain ownership, not free DMA destinations.
        if scheduler.work or scheduler.active:
            print(json.dumps(dict(event='hardware_ownership_retained',active=list(scheduler.active))),flush=True)
            # Keep device/CMA objects alive. Exiting this process would close
            # their FDs even if Python never explicitly called freebuffer().
            while scheduler.active:time.sleep(.1)
        else:
            io.close()
            print(json.dumps(dict(event='runtime_closed',completed=scheduler.metrics['completed'])),flush=True)


if __name__=='__main__':main()
