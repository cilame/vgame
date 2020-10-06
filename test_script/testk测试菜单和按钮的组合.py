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
vgame.Menu.DEBUG = True



init = vgame.Initer(size=(700, 600))
main = vgame.Theater('main', gridsize=(12, 8))

def mouse(self, m):
    if m: print(self, m)
def ctl(self, c):
    if self.delay(c and c.get('p1')[0]): menu1.toggle(True)
    if self.delay(c and c.get('p1')[1]):
        menu1.toggle(False)
        b2.text = 123
        b2.textcolor = (255,0,0)
player = vgame.Player((0,150,100,0), rectsize=(12, 8)).map.local(main, (5, 5), 1)
player.control = ctl
# player.mouse = mouse

bgcolor = (247,197,198,255)
menu1 = vgame.Menu(bgcolor).init(main, (16, 3), 'd', .35)
im = vgame.Image('../test_data/1A00.bmp', showsize=(64, 80))
head0 = vgame.Button(im, showsize=(64, 80)).menu.local(menu1, (1, 1))
head1 = vgame.Button(im, showsize=(64, 80)).menu.local(menu1, (4, 1))

hywz3 = '../test_data/hywz/3.png'

def load_images(imgpath, Class, menu1, local):
    imake = vgame.ImageMaker(imgpath)
    s = imake.gridcut((64, 64))
    p = []
    for i in range(int(len(s)/3)):
        v = s[i*3:(i+1)*3]
        p.append(v)
    unit_img_u = vgame.Image(p[1], rate=200, showsize=(100,100))
    unit_img_r = vgame.Image(p[2], rate=200, showsize=(100,100))
    unit_img_d = vgame.Image(p[3], rate=200, showsize=(100,100))
    unit_img_l = vgame.Image(p[4], rate=200, showsize=(100,100))
    unit_ = Class(unit_img_d, rectsize=(64, 64)).menu.local(menu1, local)
    unit_.status['direction'] = { 
        'up':    unit_img_u,
        'down':  unit_img_d,
        'right': unit_img_r,
        'left':  unit_img_l,
    }
    return unit_
enemy1 = load_images(hywz3, vgame.Button, menu1, (7,1))

# head2 = vgame.Button(im, showsize=(64, 80)).menu.local(menu1, (7, 1))
def click(self, m): print(self, m)
head0.click = click
head1.click = click
# head2.click = click

bgcolor = (247,197,198,255)
menu2 = vgame.Menu(bgcolor).init(main, (5, 12), 'ul', (.5-.04, .65-.04), offsets=(.02, .02))
b1 = vgame.Button(vgame.Text('J键打开菜单', (0,0,0), 2, textwidth=150, textside='r')).menu.local(menu2, (1, 2))
b2 = vgame.Button(vgame.Text('K键关闭菜单', (0,0,0), 2, textwidth=150, textside='r')).menu.local(menu2, (1, 4))

init.run()