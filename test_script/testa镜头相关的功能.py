# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)



import vgame

s = vgame.Initer()
t = vgame.Theater('main')

a = vgame.Player()
b = vgame.Wall(showsize=(500,10),showpoint=(100,400))
a.direction = lambda self,d: self.mover.move(d.get('p1'))
a.mouse = lambda self,m: self.clicker.dnd(m) # 设置a对象可以被鼠标左键拖动

t.regist(a, b)

s.regist(t)
s.run()