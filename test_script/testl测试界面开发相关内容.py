# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)



import vgame
# vgame.DEBUG = True
# vgame.Player.DEBUG = True
# vgame.Map.DEBUG = True
# vgame.Menu.DEBUG = True



init = vgame.Initer(size=(700, 600))
start = vgame.Theater((0,0,0,255)).draw.rect((255,255,255),5,3).draw.rect((255,255,255),10,3)
sbtn = vgame.Button(vgame.Text('开始游戏', (255,255,255))).local(start, start.rect.center)
sbtn.click = lambda: vgame.change_theater(main)
sbtn.control = lambda self,c: (vgame.change_theater(main) if self.delay(c and c.get('p1')[0]) else None)





def strB2Q(ustring):
    # 半角符号转全角符号
    rstring = ""
    for uchar in ustring:
        inside_code=ord(uchar)
        if inside_code == 32:
            inside_code = 12288
        elif inside_code >= 32 and inside_code <= 126:
            inside_code += 65248
        rstring += chr(inside_code)
    return rstring

main = vgame.Theater(gridsize=(12, 8))
def mouse(self, m):
    if m: print(self, m)
def ctl(self, c):
    if self.delay(c and c.get('p1')[0]): 
        menu1.toggle(True); b0.text = '打开状态'; b0.textcolor = (0,0,0); a1.text += 1
    if self.delay(c and c.get('p1')[1]):
        menu1.toggle(False); b0.text = '关闭状态'; b0.textcolor = (255,0,0); a2.text += 1
player = vgame.Player((0,150,100,0), rectsize=(12, 8)).map.local(main, (5, 5), 1)
player.control = ctl
# player.mouse = mouse
bgcolor = (247,197,198,255)
menu1 = vgame.Menu(bgcolor).init(main, (16, 7), 'd', .35)
im = vgame.Image('../test_data/1A00.bmp', showsize=(64, 80))
head = vgame.Button(im, showsize=(64, 80)).menu.local(menu1, (3, 2))
name = vgame.Anime(vgame.Text('英雄名字', (0,0,0), 2, textside='r')).menu.local(menu1, (3, 4))

def click(self, m): 
    a3.text += 1
    print(self, m)
head.click = click

menu2 = vgame.Menu(bgcolor).init(main, (5, 12), 'ul', (.5-.04, .63-.09), offsets=(.02, .10)).draw.rect((0,0,0), 3, 3)
b0 = vgame.Anime(vgame.Text('打开状态', (0,0,0), 2, textwidth=280, textside='r')).menu.local(menu2, (2, 1))
b1 = vgame.Anime(vgame.Text('Ｊ键打开菜单', (0,0,0), 2, textwidth=280, textside='r')).menu.local(menu2, (2, 2))
b2 = vgame.Anime(vgame.Text('Ｋ键关闭菜单', (0,0,0), 2, textwidth=280, textside='r')).menu.local(menu2, (2, 3))
a1 = vgame.Anime(vgame.Text(0, (0,0,0), 2, textwidth=280, textside='r', textformat='Ｊ点击次数:{:>2d}')).menu.local(menu2, (2, 4))
a2 = vgame.Anime(vgame.Text(0, (0,0,0), 2, textwidth=280, textside='r', textformat='Ｋ点击次数:{:>2d}')).menu.local(menu2, (2, 5))
a3 = vgame.Anime(vgame.Text(0, (0,0,0), 2, textwidth=280, textside='r', textformat='头像点击次数:{:>2d}')).menu.local(menu2, (2, 6))
a3 = vgame.Anime(vgame.Text(0, (0,0,0), 2, textwidth=280, textside='r', textformat='头像点击次数:{:>2d}')).menu.local(menu2, (2, 6))

import time
timestamp = time.strftime("%H-%M-%S", time.localtime())
menu_time = vgame.Menu(bgcolor).init(main, (1, 1), 'ul', (.3, .08), offsets=(.18, .01)).draw.rect((0,0,0), 3, 3)
a5 = vgame.Button(vgame.Text(timestamp, (0,0,0), 1.7, textwidth=180, textside='r')).menu.local(menu_time, (0, 0))
def change_time(self):
    ctime = time.strftime("%H-%M-%S", time.localtime())
    if self.text != ctime: self.text = strB2Q(ctime)
a5.idle = change_time

init.run()