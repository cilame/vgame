# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)



import vgame

vgame.DEBUG = True

s = vgame.Initer()
t = vgame.Theater(size=(1024, 640))

a = vgame.Player()
b = vgame.Wall(showsize=(500,10),showpoint=(20,300))
a.direction = lambda self,d: self.mover.move(d.get('p1'),10)
a.mouse = lambda self,m: self.clicker.dnd(m) # 设置a对象可以被鼠标左键拖动


# b.idle = lambda self:self.mover.move([8])
# import pygame
# v = pygame.display.get_surface().get_size()

# t.camera.follow = a
a.follow(t, offsets=(0,100))

t.regist(a, b)

s.regist(t)
s.run()