import evdev
from evdev import UInput, ecodes as e
import time
from selectors import DefaultSelector, EVENT_READ

devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
# for device in devices:
#     print(device.path, device.name, device.phys)

#device = evdev.InputDevice("/dev/input/event10")
# 读取键盘事件
# for event in device.read_loop():
#     if event.type == evdev.ecodes.EV_KEY:
#         print("isthis!",evdev.categorize(event))

keyboard1 = evdev.InputDevice("/dev/input/event2") #自带键盘
keyboard2 = evdev.InputDevice("/dev/input/event4") # 外接键盘

selector = DefaultSelector()
selector.register(keyboard1,EVENT_READ)
selector.register(keyboard2,EVENT_READ)


class target():
    def __init__(self,_code,_type,_value):
        self._code = _code 
        self._type = _type
        self._value = _value
    def match_key(self, event):
        if event.code == self._code and event.type == self._type and event.value == self._value:
            return True
        else:
            return False

ESC = target(58, 1, 0);
SHIFT_R = target(54, 1, 0);

while True:
    for key, mask in selector.select():
        device = key.fileobj
        for event in device.read():
            print(SHIFT_R.match_key(event))



# shift-r code:54 esc code:58
# type a 
# || event at 1675342230.806734, code 04, type 04, val 458756
# || event at 1675342230.806734, code 30, type 01, val 01
# || event at 1675342230.806734, code 00, type 00, val 00
# || event at 1675342230.897485, code 04, type 04, val 458756
# || event at 1675342230.897485, code 30, type 01, val 00
# || event at 1675342230.897485, code 00, type 00, val 00



# ui = UInput()
# print("wait 3 seconds")
# time.sleep(3)
# ui.write(e.EV_KEY,e.KEY_A, 1)
# time.sleep(1)
# ui.write(e.EV_KEY,e.KEY_A, 0)



# from wayremap import ecodes as e, run, WayremapConfig, Binding, wait_sway
# import uinput as k
#
#
# wayremap_config = WayremapConfig(
#         input_path='/dev/input/event4',
#         applications=[
#             'neovim',
#             ],
#         bindings=[
#             Binding([e.KEY_0],[[ k.KEY_A ]]),
#             ],
#
#         )
# run(wayremap_config)
#



# # Import necessary libraries.
# import atexit
# # You need to install evdev with a package manager or pip3.
# import evdev  # (sudo pip3 install evdev)
#
#
# # Define an example dictionary describing the remaps.
# REMAP_TABLE = {
#     # Let's swap A and B...
#     evdev.ecodes.KEY_A: evdev.ecodes.KEY_B,
#     evdev.ecodes.KEY_B: evdev.ecodes.KEY_A,
#     # # ... and make the right Shift into a second Space.
#     # evdev.ecodes.KEY_RIGHTSHIFT: evdev.ecodes.KEY_SPACE,
#     # # We'll also remap CapsLock to Control when held ...
#     # evdev.ecodes.KEY_CAPSLOCK: evdev.ecodes.KEY_LEFTCTRL,
#     # # ... but to Esc when pressed solo, xcape style! See below.
# }
# # The names can be found with evtest or in evdev docs.
#
#
# # The keyboard name we will intercept the events for. Obtainable with evtest.
# MATCH = 'AT Translated Set 2 keyboard'
# # Find all input devices.
# devices = [evdev.InputDevice(fn) for fn in evdev.list_devices()]
# # Limit the list to those containing MATCH and pick the first one.
# kbd = [d for d in devices if MATCH in d.name][0]
# atexit.register(kbd.ungrab)  # Don't forget to ungrab the keyboard on exit!
# kbd.grab()  # Grab, i.e. prevent the keyboard from emitting original events.
#
#
# soloing_caps = False  # A flag needed for CapsLock example later.
#
# # Create a new keyboard mimicking the original one.
# with evdev.UInput.from_device(kbd, name='kbdremap') as ui:
#     for ev in kbd.read_loop():  # Read events from original keyboard.
#         if ev.type == evdev.ecodes.EV_KEY:  # Process key events.
#             if ev.code == evdev.ecodes.KEY_PAUSE and ev.value == 1:
#                 # Exit on pressing PAUSE.
#                 # Useful if that is your only keyboard. =)
#                 # Also if you bind that script to PAUSE, it'll be a toggle.
#                 break
#             elif ev.code in REMAP_TABLE:
#                 # Lookup the key we want to press/release instead...
#                 remapped_code = REMAP_TABLE[ev.code]
#                 # And do it.
#                 ui.write(evdev.ecodes.EV_KEY, remapped_code, ev.value)
#                 # Also, remap a 'solo CapsLock' into an Escape as promised.
#                 if ev.code == evdev.ecodes.KEY_CAPSLOCK and ev.value == 0:
#                     if soloing_caps:
#                         # Single-press Escape.
#                         ui.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_ESC, 1)
#                         ui.write(evdev.ecodes.EV_KEY, evdev.ecodes.KEY_ESC, 0)
#             else:
#                 # Passthrough other key events unmodified.
#                 ui.write(evdev.ecodes.EV_KEY, ev.code, ev.value)
#             # If we just pressed (or held) CapsLock, remember it.
#             # Other keys will reset this flag.
#             soloing_caps = (ev.code == evdev.ecodes.KEY_CAPSLOCK and ev.value)
#         else:
#             # Passthrough other events unmodified (e.g. SYNs).
#             ui.write(ev.type, ev.code, ev.value)
