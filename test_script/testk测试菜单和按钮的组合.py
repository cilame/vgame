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
    if self.delay(c and c.get('p1')[0]): menu1.toggle(True) or menu2.toggle(True)
    if self.delay(c and c.get('p1')[1]): menu1.toggle(False) or menu2.toggle(False)
player = vgame.Player((0,150,100,0), rectsize=(12, 8)).map.local(main, (5, 5), 1)
player.control = ctl
player.mouse = mouse

bgcolor = (247,197,198,255)
menu1 = vgame.Menu(bgcolor).init(main, (16, 3), 'd', .35)
im = vgame.Image('../test_data/1A00.bmp', showsize=(64, 80))
head0 = vgame.Button(im, showsize=(64, 80)).menu.local((1, 1), menu1)
head1 = vgame.Button(im, showsize=(64, 80)).menu.local((4, 1), menu1)
head2 = vgame.Button(im, showsize=(64, 80)).menu.local((7, 1), menu1)
def click(self, m): print(self, m)
head0.click = click
head1.click = click
head2.click = click

bgcolor = (247,197,198,255)
menu2 = vgame.Menu(bgcolor).init(main, (5, 12), 'ul', (.5-.04, .65-.04), offsets=(.02, .02))
vgame.Button(vgame.Text('北京欢迎你', (0,0,0), 2)).menu.local((1, 2), menu2)
vgame.Button(vgame.Text('时间', (0,0,0), 2)).menu.local((1, 3), menu2)

init.run()
