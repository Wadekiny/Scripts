import os
import subprocess
import evdev
from evdev import UInput, ecodes as e
import time
from selectors import DefaultSelector, EVENT_READ

# || /dev/input/event21 keyd virtual pointer
# || /dev/input/event20 keyd virtual device
# /dev/input/event19 Integrated RGB Camera: Integrat usb-0000|35| 00.0-1/button
# || /dev/input/event18 ELAN0662:00 04F3:317C Touchpad i2c-ELAN0662:00
# || /dev/input/event17 ELAN0662:00 04F3:317C Mouse i2c-ELAN0662:00
# || /dev/input/event16 HD-Audio Generic HDMI/DP,pcm=7 ALSA
# || /dev/input/event15 HD-Audio Generic Headphone ALSA
# || /dev/input/event14 HD-Audio Generic Mic ALSA
# /dev/input/event8 Integrated RGB Camera: Integrat usb-0000|35| 00.0-1/button
# || /dev/input/event6 HD-Audio Generic HDMI/DP,pcm=3 ALSA
# || /dev/input/event13 Ideapad extra buttons ideapad/input0
# || /dev/input/event12 PC Speaker isa0061/input0
# || /dev/input/event5 Video Bus LNXVIDEO/video/input0
# /dev/input/event3 Logitech G304 usb-0000|34| 00.3-4/input2:1
# /dev/input/event11 CATEX TECH. 84EC-S Mouse usb-0000|34| 00.4-1/input2
# /dev/input/event10 CATEX TECH. 84EC-S Keyboard usb-0000|34| 00.4-1/input2
# /dev/input/event9 CATEX TECH. 84EC-S System Control usb-0000|34| 00.4-1/input2
# /dev/input/event7 CATEX TECH. 84EC-S Consumer Control usb-0000|34| 00.4-1/input2
# /dev/input/event4 CATEX TECH. 84EC-S usb-0000|34| 00.4-1/input0
# || /dev/input/event2 AT Translated Set 2 keyboard isa0060/serio0/input0
# || /dev/input/event1 Lid Switch PNP0C0D/button/input0
# || /dev/input/event0 Power Button PNP0C0C/button/input0


class TargetKey:
    def __init__(self, _code, _type, _value):
        self._code = _code
        self._type = _type
        self._value = _value

    def match_key(self, event):
        if (
            event.code == self._code
            and event.type == self._type
            and event.value == self._value
        ):
            return True
        else:
            return False


class KeyboardRemap(object):
    def __init__(
        self,
        list_toggle_key: list[TargetKey],
        list_quit_key: list[TargetKey],
        list_swap_key: list[list[str]],
        save_flag_path: str,
        waybar_signal_flag: bool = True,
    ):
        self._toggle_keys = list_toggle_key
        self._quit_keys = list_quit_key
        self._swap_keys = list_swap_key
        self._save_flag_path = save_flag_path
        self._swap_flag = False
        self._waybar_signal_flag = waybar_signal_flag
        self._waybar_update_command = "pkill -RTMIN+8 waybar"
        self._selector = DefaultSelector()
        self._devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        for device in self._devices:
            if "Keyboard" in device.name or "keyboard" in device.name:
                self._selector.register(device, EVENT_READ)
                # print(device.path, device.name, device.phys)
            if "keyd virtual" in device.name and "pointer" not in device.name:
                self._selector.register(device, EVENT_READ)
                # print(device.path,device.name,device.phys)
        self.remap()

    def print_device_event(self, device_path: str = "/dev/input/event20"):
        device = evdev.InputDevice(device_path)
        for event in device.read_loop():
            if event.type == evdev.ecodes.EV_KEY:
                print("isthis!:", evdev.categorize(event))

    def print_all_device(self):
        for device in self._devices:
            print(device.path, device.name, device.phys)

    def save_flag(self):
        flag = self._swap_flag
        path = self._save_flag_path
        with open(path, "w") as f:
            if flag:
                f.write("export _asd2num='ASD2NUM'")
            else:
                f.write("export _asd2num=''")

    def remap(self):
        print("flag:", self._swap_flag, "| waybar_signal", self._waybar_signal_flag)
        if self._swap_flag:
            source = self._swap_keys[0]
            target = self._swap_keys[1]
            for i in range(len(target)):
                subprocess.Popen(
                    "keyd -e '{}={}'".format(source[i], target[i]), shell=True
                )
                subprocess.Popen(
                    "keyd -e '{}={}'".format(target[i], source[i]), shell=True
                )
                self.save_flag()
        else:
            subprocess.Popen("keyd -e reset", shell=True)
            self.save_flag()
        if self._waybar_signal_flag:
            subprocess.Popen(self._waybar_update_command, shell=True)

    def loop_detector(self, is_print_all_event: bool = False):
        try:
            while True:
                last_flag = self._swap_flag
                for key, mask in self._selector.select():  # 设备循环
                    device = key.fileobj
                    for event in device.read():  # 事件循环
                        if is_print_all_event:
                            print(event)  # 用来查看按键code
                        for toggle_key in self._toggle_keys:  # 触发键循环
                            if toggle_key.match_key(event):
                                self._swap_flag = not self._swap_flag
                                break
                        for quit_key in self._quit_keys:  # 触发键循环
                            if quit_key.match_key(event):
                                self._swap_flag = False
                                break
                if last_flag != self._swap_flag:
                    self.remap()
        except:
            self._swap_flag = False
            self.remap()
            os.system("sudo systemctl stop keyd")


quit_key = TargetKey(58, 1, 0)
# close  esc
toggle_key = TargetKey(54, 1, 0)
# toggle shift_r
list_swap_key = [
    ["a", "s", "d", "f", "g", "h", "j", "k", "l", ";"],
    ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"],
]

print("starting keyd...")
os.system("sudo systemctl start keyd")
print("waiting keyd...")
time.sleep(5)  # 等待keyd启动
print("wait remapper...")
remapper = KeyboardRemap(
    [toggle_key],
    [quit_key],
    list_swap_key,
    "/home/wadekiny/Scripts/keyd/asd2num_flag.txt",
    waybar_signal_flag=True,
)

print("running...")
remapper.loop_detector()
print("TERMINATED")


## 问题：需不需要等待子进程完成
## os.system("nohup sudo systemctl start keyd &" 可以实现异步执行, 或者subprocess
## 更改映射，读不到按键了,因为设备变成了keyd virtual device?
## 相比于不断开启关闭keyd,用keyd -e <expression> 更好
## 问题在于，怎么确定虚拟键盘的设备号
## 如果开机直接启动虚拟键盘，就可以上来就找到虚拟键盘的设备号
