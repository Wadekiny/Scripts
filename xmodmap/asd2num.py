from pynput import keyboard#,mouse
from pynput.keyboard import Key
#from pynput.mouse import Button
import os
#key_ctrl = keyboard.Controller()
#key_ctrl.press('a')
#key_ctrl.release('a')
#key_ctrl.type('qwert')

asd2num = False
def on_press(key):
    global asd2num
    try:
        #if key == keyboard.KeyCode.:
        print('try')
        if key == keyboard.Key.esc:
            if asd2num == True:
                print('asd2asd')
                os.system("bash ~/.config/i3/xmodmap/asd2asd.sh")
                asd2num = False
                print('asd2num: ',asd2num)

        elif key == keyboard.Key.shift_r:
            if asd2num == False:
                print('asd2123')
                os.system("bash ~/.config/i3/xmodmap/asd2123.sh")
                asd2num = True
                print('asd2num: ',asd2num)
            elif asd2num == True:
                print('asd2asd')
                os.system("bash ~/.config/i3/xmodmap/asd2asd.sh")
                asd2num = False
                print('asd2num: ',asd2num)
    except:
        print('error!')

if __name__ == '__main__':
    with keyboard.Listener(on_press=on_press) as listener:
        listener.join()

