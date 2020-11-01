# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)



import vgame

vgame.DEBUG = True
vgame.Camera.DEBUG = True

vgame.Initer()
main = vgame.Theater(size=(1024, 640))

player = vgame.Player().local(main, (80,600)).follow(main, .05) # 在没有超过边界时，窗口会平滑居中移动
wall = vgame.Wall(showsize=(500,10)).local(main, (400,300))
player.direction = lambda self,d: self.mover.move(d.get('p1'),10)
player.mouse = lambda self,m: self.clicker.dnd(m) # 设置a对象可以被鼠标左键拖动

player.bound = lambda self, b: print(self, b)
player.click = lambda self: print(123)
player.mouseover = lambda self: print('over')
player.mouseout = lambda self: print('out')