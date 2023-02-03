import os
import glob
import time

bg_dir = '/home/wadekiny/Pictures/background/'
time_cycle = 1000
bg_list = glob.glob(bg_dir + '*.jpg') + glob.glob(bg_dir + '*.png')

os.system('swww init')
time.sleep(5)
while True:
    # bg_list = glob.glob(bg_dir + '*.jpg') + glob.glob(bg_dir + '*.png')
    for pic_name in bg_list:
        print(pic_name)
        # os.system('feh --bg-fill '+ pic_name)
        cmd = 'swww img {} --transition-type center --transition-fps 255 --transition-step 25'.format(pic_name)
        print(cmd)
        os.system(cmd)
        time.sleep(time_cycle)



