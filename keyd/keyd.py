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

# 找到所需设备
# devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
# for device in devices:
#     if "Keyboard" in device.name or "keyboard" in device.name:
#         print(device.path,"--", device.name,"--", device.phys)
#     if "keyd virtual" in device.name:
#         print(device.path,"--", device.name,"--", device.phys)

# device = evdev.InputDevice("/dev/input/event21") # virtual mouse
# device = evdev.InputDevice("/dev/input/event20") # virtual keyboard
# keyboard1 = evdev.InputDevice("/dev/input/event2") #自带键盘
# keyboard2 = evdev.InputDevice("/dev/input/event4") # 外接键盘
# os.system('notify-send hh')
# #读取键盘事件
# for event in device.read_loop():
#     if event.type == evdev.ecodes.EV_KEY:
#         print("isthis!",evdev.categorize(event))



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

#保存成文件，或者保存成全局的环境变量
def save_flag(flag):
    path = '/home/wadekiny/Scripts/keyd/asd2num_flag.txt'
    with open(path,'w') as f:
        if flag : f.write("export _asd2num='ASD2NUM'")
        else :f.write("export _asd2num='NORMAL'")

def remap(flag,waybar_signal = True):
    print("flag:", flag, "| waybar_signal", waybar_signal)
    waybar_update_command = "pkill -RTMIN+8 waybar"
    if flag:
        asd = ['a','s','d','f','g','h','j','k','l',';']
        num = ['1','2','3','4','5','6','7','8','9','0']
        # subprocess.popen()
        for i in range(len(num)):
            subprocess.Popen("keyd -e '{}={}'".format(asd[i],num[i]), shell=True)
            subprocess.Popen("keyd -e '{}={}'".format(num[i],asd[i]), shell=True)
            save_flag(asd2num_flag)
    else:
        subprocess.Popen("keyd -e reset", shell=True)
        save_flag(asd2num_flag)
    if waybar_signal:
        subprocess.Popen(waybar_update_command,shell=True)


print('starting keyd...')
os.system("sudo systemctl start keyd")
print('waiting keyd...')
time.sleep(5) #等待keyd启动
print('scanning device...')
selector = DefaultSelector()
devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
    if "Keyboard" in device.name or "keyboard" in device.name:
        selector.register(device,EVENT_READ)
        print(device.path, device.name, device.phys)
    if "keyd virtual" in device.name and "pointer" not in device.name:
        selector.register(device,EVENT_READ)
        print(device.path,device.name,device.phys)



# 启用keyd之后，按键code也会变(并没有，是默认将rightshift映射到了leftshift)
# quit_target = target(58, 1, 0);    #close  esc
# toggle_target = target(100, 1, 0);  #toggle right fn
quit_target = target(58, 1, 0);    #close  esc
toggle_target = target(54, 1, 0);  #toggle shift_r
asd2num_flag = False 

print("init all settings")
remap(asd2num_flag)

try:
    while True:
        # 扫描键盘事件, 更新asd2num_flag
        last_flag = asd2num_flag
        for key, mask in selector.select():
            device = key.fileobj
            for event in device.read():
                # print(event) #用来查看按键code
                if toggle_target.match_key(event):
                    asd2num_flag = not asd2num_flag
                if quit_target.match_key(event):
                    asd2num_flag = False
        if last_flag != asd2num_flag:
            # flag更新了 #需要root权限 
            remap(asd2num_flag)
except:
    remap(False)
    os.system("sudo systemctl stop keyd")




# 问题：需不需要等待子进程完成
# os.system("nohup sudo systemctl start keyd &" 可以实现异步执行, 或者subprocess
# 更改映射，读不到按键了,因为设备变成了keyd virtual device?
# 相比于不断开启关闭keyd,用keyd -e <expression> 更好
# 问题在于，怎么确定虚拟键盘的设备号
# 如果开机直接启动虚拟键盘，就可以上来就找到虚拟键盘的设备号
