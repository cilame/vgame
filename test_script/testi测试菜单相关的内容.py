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
main = vgame.Theater('main', gridsize=(12, 8))


city = vgame.Enemy(showsize=(12, 8)).map.local((3, 3), 1, main)

def mouse(self, m):
    if m:
        # 鼠标右键单击时菜单的开关闭
        if m[0] == 2 and m[1] == 0:
            menu.toggle()


def ctl(self, c):
    # J 键切换显示/隐藏菜单
    if self.delay(c and c.get('p1')[0], time=0):
        if self.axis == city.axis:
            menu.toggle()

def direct(self, d):
    if d:
        # 方向键进行栅格化的移动
        self.map.direct(d.get('p1'), 10)

player = vgame.Player((10,10,10,100), rectsize=(12, 8)).map.local((5,5), 1, main)
player.control = ctl
player.direction = direct
player.mouse = mouse




menu = vgame.Menu((247,197,198,255)).pack(main, 'd', .4)
head = vgame.Button('../test_data/1A00.bmp', showsize=(64, 80)).map.local((10,45), 0, main)
print(head.showsize)
menu
print(menu.add)
print(menu.group)









init.run()
