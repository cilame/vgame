# 增加环境变量，仅测试使用
import os
import sys
p = os.path.split(os.getcwd())[0]
sys.path = [p] + sys.path
import sys;print(sys.stdout.encoding)




import vgame
s = vgame.Initer(60)
t = vgame.Theater('main')

vgame.Actor.DEBUG = True

a = vgame.Actor(in_control=True,showsize=(50,100))
b = vgame.Actor(showsize=(510,10))
c = vgame.Actor(showsize=(80,80))
d = vgame.Actor(showsize=(40,40),in_physics=False) 
# 如果不想让某些块处理刚体碰撞，实例化时候设置 in_physics 为 False，自动去除刚体检测

# 使用物理性质来进行移动，自动对其他实体对象实现刚体碰撞，并能极大简化代码
a.direction = lambda self,d: self.physics.move(d.get('p1')) 

# physics.move 这种移动会检测其他刚体，或停止或切边移动，直接修改坐标则无法处理碰撞
c.idle = lambda self,d: self.physics.move([4, 2]) # 不断向左下移动

a.rect[0:2] = 100, 100
b.rect[0:2] = 10, 400
c.rect[0:2] = 400, 200
d.rect[0:2] = 200, 200
t.regist(a)
t.regist(b)
t.regist(c)
t.regist(d)

s.regist(t) # 将场景 t 注入游戏
s.run()