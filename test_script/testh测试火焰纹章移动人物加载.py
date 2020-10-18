# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)



import vgame

vgame.DEBUG = True
# vgame.Player.DEBUG = True
vgame.Map.DEBUG = True

init = vgame.Initer()
main = vgame.Theater()



hywz1 = '../test_data/hywz/1.png'
hywz2 = '../test_data/hywz/2.png'
hywz3 = '../test_data/hywz/3.png'

def load_images(imgpath, Class, map, local, speed):
    imake = vgame.ImageMaker(imgpath)
    s = imake.gridcut((64, 64))
    p = []
    for i in range(int(len(s)/3)):
        v = s[i*3:(i+1)*3]
        p.append(v)
    unit_img_u = vgame.Image(p[1], rate=150, showsize=(60,60))
    unit_img_r = vgame.Image(p[2], rate=150, showsize=(60,60))
    unit_img_d = vgame.Image(p[3], rate=150, showsize=(60,60))
    unit_img_l = vgame.Image(p[4], rate=150, showsize=(60,60))
    unit_ = Class(unit_img_d, rectsize=(32, 32)).map.local(map, local, speed)
    unit_.status['direction'] = { 
        'up':    unit_img_u,
        'down':  unit_img_d,
        'right': unit_img_r,
        'left':  unit_img_l,
    }
    return unit_

map = vgame.Map(showsize=main.showsize, grid=(20,15))
map.local(main)

player = load_images(hywz1, vgame.Player, map, (1,1), 10)
enemy1 = load_images(hywz2, vgame.Enemy, map, (8,6), 1)
enemy2 = load_images(hywz3, vgame.Enemy, map, (9,9), 1)


for i in range(0, 5): vgame.Wall(showsize=(32, 32)).map.local(map, (3, i), float('inf')) 
for i in range(3, 7): vgame.Wall(showsize=(32, 32)).map.local(map, (6, i), float('inf')) 

init.run()