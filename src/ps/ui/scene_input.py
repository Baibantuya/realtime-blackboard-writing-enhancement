"""Nonblocking Linux evdev input, with bounded hotplug rescans and no device grab."""
import errno
import glob
import os
import struct
import time


class LinuxInput:
    EVENT = struct.Struct('@llHHi')
    KEYS = {59: 0xF1, 60: 0xF2, 61: 0xF3, 62: 0xF4, 63: 0xF5,
            64: 0xF6, 65: 0xF7, 66: 0xF8, 67: 0xF9, 68: 0xFA}
    NAV = {15: 1, 28: 3, 57: 3, 103: 4, 108: 5, 105: 6, 106: 7, 1: 8}

    def __init__(self, paths=None, rescan_seconds=1.0, clock=time.monotonic):
        self.paths = None if paths is None else tuple(paths)
        self.clock = clock
        self.rescan_seconds = max(0.1, float(rescan_seconds))
        self.next_scan = 0.0
        self.devices = {}
        self.identities = {}
        self.device_paths = {}
        self.shifts = {}
        self.buttons = {}
        self.x = 1844
        self.y = 1044
        self.down = 0
        self.shift = set()
        self.dropped = set()
        self.native = None
        self.errors = {}
        self.counters = dict(connected=0, disconnected=0, events=0, sync_dropped=0)
        self._scan(self.clock())

    @staticmethod
    def _identity(st):
        # Aliases share an inode; a re-created event node gets a new identity.
        return st.st_dev, st.st_ino, st.st_rdev

    @staticmethod
    def _supported(fd):
        """Include keyboards and relative mice; exclude unrelated evdev sensors."""
        import fcntl

        def bits(event, size):
            data = bytearray(size)
            # Linux EVIOCGBIT(event, len), architecture-independent ioctl layout.
            fcntl.ioctl(fd, (2 << 30) | (size << 16) | (ord('E') << 8) | (0x20 + event), data, True)
            return lambda bit: bool(data[bit // 8] & (1 << (bit % 8)))

        key = bits(1, 96)
        relative = bits(2, 8)
        keyboard = key(28) and (key(30) or key(59))
        mouse = key(272) and relative(0) and relative(1)
        return keyboard or mouse

    def _candidates(self):
        if self.paths is not None:
            return self.paths
        # event* also covers devices lacking udev by-id aliases.
        return sorted(glob.glob('/dev/input/event*'))

    def _scan(self, now):
        self.next_scan = now + self.rescan_seconds
        known = set(self.identities.values())
        for path in self._candidates():
            fd = None
            try:
                identity = self._identity(os.stat(path))
                if identity in known:
                    continue
                fd = os.open(path, os.O_RDONLY | os.O_NONBLOCK | getattr(os, 'O_CLOEXEC', 0))
                identity = self._identity(os.fstat(fd))
                if identity in known or (self.paths is None and not self._supported(fd)):
                    os.close(fd)
                    continue
                self.devices[fd] = b''
                self.identities[fd] = identity
                self.device_paths[fd] = str(path)
                self.shifts[fd] = set()
                self.buttons[fd] = False
                self.counters['connected'] += 1
                known.add(identity)
                self.errors.pop(str(path), None)
            except OSError as exc:
                if fd is not None:
                    os.close(fd)
                # Missing/permission-denied devices must not stop the video loop.
                self.errors[str(path)] = exc.errno
        if len(self.errors) > 64:
            self.errors = dict(list(self.errors.items())[-64:])

    def _release(self, fd, native):
        self.shifts.get(fd, set()).clear()
        if fd in self.buttons:
            self.buttons[fd] = False
        self.shift = set().union(*self.shifts.values()) if self.shifts else set()
        previous = self.down
        self.down = int(any(self.buttons.values()))
        if native is not None and previous != self.down:
            # Cancel a drag/click on disconnect or SYN_DROPPED; an ordinary
            # release at the old position could activate a button accidentally.
            native.lib.ps_pointer(-1, -1, 0)

    def _remove(self, fd, native):
        self.counters['disconnected'] += 1
        self._release(fd, native)
        try:
            os.close(fd)
        except OSError:
            pass
        for table in (self.devices, self.identities, self.device_paths, self.shifts, self.buttons):
            table.pop(fd, None)
        self.dropped.discard(fd)

    def poll(self, native):
        self.native = native
        now = self.clock()
        if now >= self.next_scan:
            # Remove dead nodes before scanning, including replacement at same path.
            for fd in list(self.devices):
                try:
                    if self._identity(os.stat(self.device_paths[fd])) == self.identities[fd]:
                        continue
                except OSError:
                    pass
                self._remove(fd, native)
            self._scan(now)
        for fd in list(self.devices):
            try:
                data = os.read(fd, self.EVENT.size * 64)
            except OSError as exc:
                if exc.errno in (errno.EAGAIN, errno.EWOULDBLOCK, errno.EINTR):
                    continue
                self._remove(fd, native)
                continue
            if not data:
                self._remove(fd, native)
                continue
            data = self.devices[fd] + data
            n = len(data) // self.EVENT.size * self.EVENT.size
            self.devices[fd] = data[n:]
            for offset in range(0, n, self.EVENT.size):
                _, _, kind, code, value = self.EVENT.unpack_from(data, offset)
                self.counters['events'] += 1
                if kind == 0 and code == 3:
                    self.counters['sync_dropped'] += 1
                    self.dropped.add(fd)
                    self._release(fd, native)
                elif fd in self.dropped:
                    if kind == 0 and code == 0:
                        self.dropped.discard(fd)
                elif kind == 1:
                    if code in (42, 54):
                        if value:
                            self.shifts[fd].add(code)
                        else:
                            self.shifts[fd].discard(code)
                        self.shift = set().union(*self.shifts.values())
                    elif code == 272:
                        self.buttons[fd] = value != 0
                        self.down = int(any(self.buttons.values()))
                        native.lib.ps_pointer(self.x, self.y, self.down)
                    elif value == 1:
                        if code in self.KEYS:
                            native.lib.ps_key(self.KEYS[code])
                        elif code in self.NAV:
                            native.lib.ps_nav(2 if code == 15 and self.shift else self.NAV[code])
                elif kind == 2 and code in (0, 1):
                    if code == 0:
                        self.x = max(0, min(1919, self.x + value))
                    else:
                        self.y = max(0, min(1079, self.y + value))
                    native.lib.ps_pointer(self.x, self.y, self.down)

    def close(self):
        for fd in list(self.devices):
            self._remove(fd, self.native)
