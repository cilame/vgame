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
main = vgame.Theater('main', gridsize=(32, 32))



hywz1 = '../test_data/hywz/1.png'
hywz2 = '../test_data/hywz/2.png'
hywz3 = '../test_data/hywz/3.png'

def load_images(imgpath, Class, theater, local, speed):
    imake = vgame.ImageMaker(imgpath)
    s = imake.gridcut((64, 64))
    p = []
    for i in range(int(len(s)/3)):
        v = s[i*3:(i+1)*3]
        p.append(v)
    unit_img_u = vgame.Image(p[1], rate=200, showsize=(60,60))
    unit_img_r = vgame.Image(p[2], rate=200, showsize=(60,60))
    unit_img_d = vgame.Image(p[3], rate=200, showsize=(60,60))
    unit_img_l = vgame.Image(p[4], rate=200, showsize=(60,60))
    unit_ = Class(unit_img_d, rectsize=(32, 32)).map.local(theater, local, speed)
    unit_.status['direction'] = { 
        'up':    unit_img_u,
        'down':  unit_img_d,
        'right': unit_img_r,
        'left':  unit_img_l,
    }
    return unit_

def direct(self, d):
    if d: 
        self.mover.move(d.get('p1'))

def ctl(self, c):
    if self.delay(c and c.get('p1')[0], time=150, delayer='A'):
        trs = self.map.trace(enemy1)
        self.map.move(trs, 10)
        print(trs)

    if self.delay(c and c.get('p1')[1], time=150, delayer='B'):
        print(self.theater.name)
        print(self.map)

def e_idle(self, i):
    import random
    w, h = main.map.size
    x = random.randint(0, w-1)
    y = random.randint(0, h-1)
    trs = self.map.trace((x, y))
    self.map.move(trs, 1)

def p_idle(self):
    s = self.collide(enemy1)
    if s:
        print(s)

player = load_images(hywz1, vgame.Player, main, (1,1), 10)
player.direction = direct
player.control = ctl
player.idle = p_idle

enemy1 = load_images(hywz2, vgame.Enemy, main, (8,6), 1)
enemy2 = load_images(hywz3, vgame.Enemy, main, (6,6), 1)
enemy1.idle = e_idle
enemy2.idle = e_idle

print(main.map.size)

for i in range(0, 5): vgame.Wall(showsize=(32, 32)).map.local(main, (3, i), float('inf')) 
for i in range(3, 7): vgame.Wall(showsize=(32, 32)).map.local(main, (6, i), float('inf')) 

init.run()