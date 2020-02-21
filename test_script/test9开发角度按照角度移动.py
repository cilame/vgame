# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)




import vgame

s = vgame.Initer()
t = vgame.Theater('main')

a = vgame.Actor(showpoint=(100, 100),in_physics=True,in_control=True)
b = vgame.Actor(showsize=(500, 20),showpoint=(100, 400))

def control_a(self, c):
    if c and c.get('p1'):
        v = self.angle(b)
        print(v)
a.control = control_a


t.regist(a, b)
s.regist(t)
s.run()