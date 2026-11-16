import ctypes
import os
import subprocess
import time

core_foundation = ctypes.CDLL("/System/Library/Frameworks/CoreFoundation.framework/CoreFoundation")
iokit = ctypes.CDLL("/System/Library/Frameworks/IOKit.framework/IOKit")

utf8 = 0x08000100
deliver_immediately = 4
can_system_sleep = 0xE0000270
system_will_sleep = 0xE0000280

notification_type = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p)
power_type = ctypes.CFUNCTYPE(None, ctypes.c_void_p, ctypes.c_uint32, ctypes.c_uint32, ctypes.c_void_p)

core_foundation.CFStringCreateWithCString.restype = ctypes.c_void_p
core_foundation.CFStringCreateWithCString.argtypes = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_uint32]
core_foundation.CFNotificationCenterGetDistributedCenter.restype = ctypes.c_void_p
core_foundation.CFNotificationCenterAddObserver.restype = None
core_foundation.CFNotificationCenterAddObserver.argtypes = [
    ctypes.c_void_p, ctypes.c_void_p, notification_type, ctypes.c_void_p, ctypes.c_void_p, ctypes.c_long,
]
core_foundation.CFRunLoopGetCurrent.restype = ctypes.c_void_p
core_foundation.CFRunLoopAddSource.restype = None
core_foundation.CFRunLoopAddSource.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_void_p]
core_foundation.CFRunLoopRun.restype = None
iokit.IORegisterForSystemPower.restype = ctypes.c_uint32
iokit.IORegisterForSystemPower.argtypes = [
    ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p), power_type, ctypes.POINTER(ctypes.c_uint32),
]
iokit.IONotificationPortGetRunLoopSource.restype = ctypes.c_void_p
iokit.IONotificationPortGetRunLoopSource.argtypes = [ctypes.c_void_p]
iokit.IOAllowPowerChange.restype = ctypes.c_int
iokit.IOAllowPowerChange.argtypes = [ctypes.c_uint32, ctypes.c_long]

base = os.path.dirname(os.path.abspath(__file__))
sleep_script = os.path.join(base, "sleep.sh")
unlock_script = os.path.join(base, "unlock.sh")
log = os.path.expanduser("~/Library/Logs/network-sleep.log")
root_port = 0


def write_log(message):
    with open(log, "a") as file:
        file.write(time.strftime("%Y-%m-%d %H:%M:%S") + " " + message + "\n")


def on_power(refcon, service, message_type, argument):
    if message_type == system_will_sleep:
        subprocess.run(["/bin/bash", sleep_script], check=False)
    if message_type in (can_system_sleep, system_will_sleep):
        iokit.IOAllowPowerChange(root_port, argument or 0)


def on_unlock(center, observer, name, sender, info):
    write_log("unlock event")
    subprocess.run(["/bin/bash", unlock_script], check=False)


power_handler = power_type(on_power)
unlock_handler = notification_type(on_unlock)

notify_port = ctypes.c_void_p()
notifier = ctypes.c_uint32()
root_port = iokit.IORegisterForSystemPower(None, ctypes.byref(notify_port), power_handler, ctypes.byref(notifier))
if root_port == 0:
    write_log("IORegisterForSystemPower failed")
    raise SystemExit(1)
default_mode = ctypes.c_void_p.in_dll(core_foundation, "kCFRunLoopDefaultMode")
core_foundation.CFRunLoopAddSource(
    core_foundation.CFRunLoopGetCurrent(), iokit.IONotificationPortGetRunLoopSource(notify_port), default_mode,
)

unlock_name = core_foundation.CFStringCreateWithCString(None, b"com.apple.screenIsUnlocked", utf8)
core_foundation.CFNotificationCenterAddObserver(
    core_foundation.CFNotificationCenterGetDistributedCenter(), None, unlock_handler, unlock_name, None, deliver_immediately,
)
write_log("listener started")
subprocess.run(["/bin/bash", unlock_script, "start"], check=False)
core_foundation.CFRunLoopRun()
